# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Hoàng Bá Minh Quang  
**Vai trò trong nhóm:** MCP Owner (phối hợp Supervisor/Worker integration) + hỗ trợ quản lý source code/merge Git  
**Ngày nộp:** 14/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

> **Lưu ý quan trọng:**
> - Viết ở ngôi **"tôi"**, gắn với chi tiết thật của phần bạn làm
> - Phải có **bằng chứng cụ thể**: tên file, đoạn code, kết quả trace, hoặc commit
> - Nội dung phân tích phải khác hoàn toàn với các thành viên trong nhóm
> - Deadline: Được commit **sau 18:00** (xem SCORING.md)
> - Lưu file với tên: `reports/individual/[ten_ban].md` (VD: `nguyen_van_a.md`)

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

**Module/file tôi chịu trách nhiệm:**
- File chính: `day09/lab/mcp_server.py`
- Functions tôi implement: `list_tools`, `dispatch_tool`, `tool_search_kb`, `tool_get_ticket_info`, `tool_check_access_permission`, `tool_create_ticket`

**Cách công việc của tôi kết nối với phần của thành viên khác:**

Tôi chịu trách nhiệm phần contract tool theo kiểu MCP mock để supervisor có thể gọi tool theo tên thay vì hard-code API. Công việc của tôi nối trực tiếp với worker retrieval ở chỗ `tool_search_kb` delegate sang `workers/retrieval.py`; đồng thời nối với supervisor qua `dispatch_tool` để xử lý input/output thống nhất. Nhờ đó, các bạn làm supervisor chỉ cần quyết định route logic, không phải biết chi tiết từng tool implementation. Tôi cũng giữ phần test trong `__main__` để team có script kiểm tra nhanh khi tích hợp. Ngoài phần code, tôi hỗ trợ nhóm xử lý các vấn đề Git (sync nhánh, resolve conflict, merge) để code tổng không bị kẹt khi tích hợp.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Tôi chọn kiến trúc MCP mock in-process (`list_tools` + `dispatch_tool`) thay vì triển khai MCP HTTP server ngay trong lab.

**Lý do:**

Tôi cân nhắc hai phương án: (1) làm server qua FastAPI/mcp library; (2) giữ mock in-process để ưu tiên orchestration và contract trước. Tôi chọn (2) vì dữ liệu eval cho thấy Day 09 cần tập trung vào khả năng route + gọi tool đúng hơn là mở rộng hạ tầng. Trong `artifacts/eval_report.json`, `policy_tool_worker` được route `31/43` trace (72%), `mcp_usage_rate` cũng `31/43` (72%). Nghĩa là phần gọi tool chiếm tỷ trọng lớn của pipeline; nếu contract/tool dispatch không chắc thì toàn hệ thống sẽ fail dây chuyền. Ngoài ra, phần analysis ghi rõ Day 09 có `route_reason` theo từng câu và debug được từng worker độc lập, nên phương án mock in-process phù hợp mục tiêu debug nhanh trong lab.

**Trade-off đã chấp nhận:**

Đổi lại, cách này chưa phản ánh đầy đủ môi trường production: chưa có auth, retry, timeout chuẩn server-side, và chưa đo được độ trễ mạng. Tuy nhiên tôi chấp nhận trade-off này để khóa contract sớm, ưu tiên tính đúng chức năng trước khi tối ưu hạ tầng.

**Bằng chứng từ trace/code:**

```
TOOL_SCHEMAS = {...}

def list_tools() -> list:
	return list(TOOL_SCHEMAS.values())

def dispatch_tool(tool_name: str, tool_input: dict) -> dict:
	if tool_name not in TOOL_REGISTRY:
		return {"error": f"Tool '{tool_name}' không tồn tại..."}
	...

# Demo test
result = dispatch_tool("search_kb", {"query": "SLA P1 resolution time", "top_k": 2})
err = dispatch_tool("nonexistent_tool", {})

# Evidence from artifacts/eval_report.json
# routing_distribution: retrieval_worker 12/43 (27%), policy_tool_worker 31/43 (72%)
# mcp_usage_rate: 31/43 (72%)
# hitl_rate: 2/43 (4%)
# avg_confidence: 0.188, avg_latency_ms: 21189
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Pipeline bị fail cứng khi MCP client gửi input không khớp schema tool.

**Symptom (pipeline làm gì sai?):**

Trong lúc tích hợp, một số lời gọi tool bị thiếu field hoặc sai key (ví dụ gọi tool không tồn tại, hoặc truyền input sai). Khi chưa chặn lỗi tốt ở dispatch layer, pipeline có thể dừng ở bước gọi tool thay vì trả về lỗi có cấu trúc để supervisor xử lý tiếp.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**

Root cause nằm ở lớp contract/dispatch của MCP: lỗi input được ném từ Python call stack (TypeError) nhưng chưa được chuẩn hóa thành output thống nhất cho agent orchestration.

**Cách sửa:**

Tôi xử lý tập trung trong `dispatch_tool`: 
- Nếu tool name không hợp lệ thì trả ngay error dict có danh sách tool khả dụng.
- Nếu input sai signature thì bắt `TypeError` và trả error kèm `inputSchema` để dễ sửa.
- Nếu tool execution lỗi runtime thì bắt exception tổng quát và trả lỗi mềm thay vì crash toàn pipeline.
Ngoài ra, `tool_search_kb` có fallback mock khi retrieval backend chưa sẵn sàng.

**Bằng chứng trước/sau:**

Trước: gọi sai tool/input có thể làm flow dừng đột ngột khi call function.  
Sau: luôn có output dạng dict để supervisor xử lý:

```json
{"error": "Tool 'nonexistent_tool' không tồn tại. Available: [...]"}
```

```json
{"error": "Invalid input for tool 'check_access_permission': ...", "schema": {...}}
```

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**

Tôi làm tốt ở việc chuẩn hóa contract tool và giữ dispatch layer ổn định để team tích hợp nhanh. Tôi cũng chủ động để sẵn các case test trong file giúp mọi người verify ngay mà không cần setup phức tạp, đồng thời hỗ trợ quản lý source code và merge để giảm rủi ro lỗi Git khi ghép code nhóm.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**

Tôi chưa kịp nâng module lên mức production-like (chưa tách HTTP service, chưa có timeout/retry policy đầy đủ, chưa có auth). Việc benchmark độ trễ theo từng tool cũng còn thiếu.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_

Nhóm phụ thuộc vào tôi ở lớp gọi tool thống nhất. Nếu dispatch/schema chưa ổn, supervisor sẽ khó route đúng và worker không có contract chuẩn để trả dữ liệu.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_

Tôi phụ thuộc vào bạn làm retrieval/worker để chất lượng `search_kb` tốt hơn; đồng thời cần kết quả trace từ supervisor để tinh chỉnh format error/output cho phù hợp thực tế call chain.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)
Tôi sẽ thêm lớp validation input theo schema ngay trước khi gọi tool trong `dispatch_tool` (kiểm tra required fields và type cơ bản). Lý do là từ các case test hiện tại, lỗi phổ biến nhất khi tích hợp là truyền input sai format; nếu validate sớm, lỗi sẽ rõ hơn, giảm thời gian debug cho supervisor và tránh fail dây chuyền ở worker.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*  
*Ví dụ: `reports/individual/nguyen_van_a.md`*
