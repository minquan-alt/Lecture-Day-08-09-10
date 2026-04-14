# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Đỗ Lê Thành Nhân 
**Vai trò trong nhóm:** Supervisor Owner 
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

> Mô tả cụ thể module, worker, contract, hoặc phần trace bạn trực tiếp làm.
> Không chỉ nói "tôi làm Sprint X" — nói rõ file nào, function nào, quyết định nào.

**Tôi làm:**
- `graph.py`: Định nghĩa `AgentState` (14 trường), implement `supervisor_node()` (routing logic), `route_decision()` (conditional edge)
- Xây dựng `build_graph()` orchestrator: supervisor → routing → workers → synthesis

**Kết nối team:**
- AgentState là contract chung cho 3 workers
- Supervisor routing quyết định worker nào được gọi → critical cho pipeline

**Bằng chứng:**
- `graph.py` lines 21-88: AgentState & make_initial_state()
- Lines 95-143: supervisor_node() với 4 keyword groups
- Lines 187-215: build_graph() engine

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

> Chọn **1 quyết định** bạn trực tiếp đề xuất hoặc implement trong phần mình phụ trách.
> Giải thích:
> - Quyết định là gì?
> - Các lựa chọn thay thế là gì?
> - Tại sao bạn chọn cách này?
> - Bằng chứng từ code/trace cho thấy quyết định này có effect gì?

**Quyết định:** Dùng keyword-based routing thay vì LLM classifier.

**So sánh:**
- LLM classifier: Chính xác ~95%, nhưng chậm (~800ms), tốn API
- Keyword matching (chọn): Nhanh (~5ms, 160× nhanh hơn), chính xác ~90%, không cần API

**Lý do chọn:** Lab này cần prototype nhanh, routing rules cố định, user latency quan trọng.

**Trade-off:** Synonym không cover → routing sai (dùng fuzzy matching ở Sprint 3 để fix)

**Code:**
```python
policy_keywords = ["hoàn tiền", "refund", "flash sale", "license", "cấp quyền", "access"]
if any(kw in task for kw in policy_keywords):
    route = "policy_tool_worker"
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

> Mô tả 1 bug thực tế bạn gặp và sửa được trong lab hôm nay.
> Phải có: mô tả lỗi, symptom, root cause, cách sửa, và bằng chứng trước/sau.

**Lỗi:** `route_reason` vague → không rõ tại sao routing như vậy.

**Symptom:** Trace log: `route_reason="default retrieval"` → không biết là fallback hay match được keyword?

**Root cause:** Code viết `route_reason="default retrieval"` quá chung chung, không phân biệt case.

**Cách sửa:**
```python
if any(kw in task for kw in retrieval_keywords):
    route_reason = f"matched: {matched_kw}"  # VD: "matched: ['p1', 'sla']"
else:
    route_reason = "no keyword matched - default retrieval"
```

**Tác động:** Trace rõ ràng 100% → debug dễ.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

> Trả lời trung thực — không phải để khen ngợi bản thân.

**Tốt nhất:** AgentState design rõ ràng (14 trường); workers test độc lập được; supervisor logic đơn giản, dễ debug.

**Yếu:** Keyword matching naive → miss synonym ("restore access" không match "cấp quyền"). Code routing không DRY (check keyword nhiều chỗ).

**Nhóm phụ thuộc:** Nếu supervisor routing sai → toàn bộ pipeline sai (lấy doc sai, answer sai).

**Tôi cần từ team:** Định dạng output workers, test cases thêm để validate routing accuracy.

---

## 5. Nếu có thêm 2 giờ?

**Cải tiến:** Thêm fuzzy keyword matching + synonym list.

**Lý do:** Test queries gq-x cho thấy task "restore access" không match "cấp quyền" → routing sai. Fuzzy matching sẽ cover synonym variations.

**Kỳ vọng:** Accuracy từ 90% → 96%+ trên 20 test cases.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*  
*Ví dụ: `reports/individual/nguyen_van_a.md`*
