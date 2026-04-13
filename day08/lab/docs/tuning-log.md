# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 500 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = ollama-7b
```

**Scorecard Baseline:**
| Metric           | Average Score |
| ---------------- | ------------- |
| Faithfulness     | 4.56 /5          |
| Answer Relevance | 4.67 /5          |
| Context Recall   | 5.00 /5          |
| Completeness     | 4.50 /5          |

**Câu hỏi yếu nhất (điểm thấp):**
- gq05 (Access Control): Faithfulness = 2/5, Completeness = 2/5. Answer suy diễn contractor không được cấp Admin Access, thiếu các ý quan trọng: vẫn có thể cấp Level 4 nếu đủ phê duyệt, SLA 5 ngày làm việc, và training bắt buộc.
- gq09 (IT Helpdesk): Faithfulness = 4/5, Completeness = 4/5. Trả lời đúng ý chính nhưng thiếu chi tiết chu kỳ đổi mật khẩu 90 ngày và chưa nêu rõ URL reset/liên hệ Helpdesk.
- gq07 (Insufficient Context): Relevance = 4/5. Có trả lời "không đủ dữ liệu" nhưng thêm thông tin thời gian SLA 4 giờ không cần thiết cho câu hỏi về mức phạt.


**Giả thuyết nguyên nhân (Error Tree):**
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Retrieval: Dense bỏ lỡ exact keyword / alias
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 + 2 (Sprint 3)

**Ngày:** 2026-04-13  
**Biến thay đổi:** dense -> sparse -> hybrid
**Lý do chọn biến này:**
> Baseline cho thấy lỗi chính nằm ở các câu cần bám chặt keyword/chính sách dài (đặc biệt gq05, gq09), nên nhóm thử retrieval lexical trước (sparse) rồi kết hợp semantic + lexical (hybrid) để kiểm tra có tăng độ bao phủ evidence và giảm hallucination không.
> Vì đã giữ nguyên chunking/top-k/rerank, thay đổi retrieval mode giúp so sánh đúng A/B rule (mỗi lần đổi 1 biến retrieval).

**Config thay đổi:**
```
# Variant 1
retrieval_mode = "sparse"

# Variant 2
retrieval_mode = "hybrid"  # hybrid_50_50

# Các tham số còn lại giữ nguyên baseline:
# chunk_size=500, overlap=80, top_k_search=10, top_k_select=3, use_rerank=False
```

**Scorecard Variant 1:**
| Metric           | Baseline | Variant 1 | Delta |
| ---------------- | -------- | --------- | ----- |
| Faithfulness     | 4.56/5   | 3.50/5    | -1.06 |
| Answer Relevance | 4.67/5   | 4.50/5    | -0.17 |
| Context Recall   | 5.00/5   | 5.00/5    | +0.00 |
| Completeness     | 4.50/5   | 3.88/5    | -0.62 |

**Scorecard Variant 2 (hybrid_50_50):**
| Metric           | Baseline | Variant 2 | Delta |
| ---------------- | -------- | --------- | ----- |
| Faithfulness     | 4.56/5   | 3.57/5    | -0.99 |
| Answer Relevance | 4.67/5   | 3.89/5    | -0.78 |
| Context Recall   | 5.00/5   | 5.00/5    | +0.00 |
| Completeness     | 4.50/5   | 4.00/5    | -0.50 |

**Nhận xét:**
> Cả sparse và hybrid đều không vượt baseline ở mức trung bình; điểm Context Recall giữ nguyên 5.00/5 cho thấy retriever vẫn lấy đúng nguồn, nhưng generation/judge quality giảm.
> Sparse kém rõ ở các câu tổng hợp/chính sách phức tạp: gq05 (Access Control) và gq07 (Insufficient Context) giảm mạnh về Faithfulness/Relevance.
> Hybrid cải thiện nhẹ so với sparse ở Faithfulness (+0.07) và Completeness (+0.12), nhưng vẫn thấp hơn baseline; đặc biệt gq10 trả lời "Không biết" làm Relevance/Completeness giảm sâu.
> Kết quả có nhiễu do một số lượt judge bị 401 (missing scope), nên so sánh nên xem thêm rows chi tiết theo từng câu.

**Kết luận:**
> Variant 1 (sparse) không tốt hơn baseline dense.
> Variant 2 (hybrid_50_50) cũng chưa vượt baseline dù đỡ hơn sparse ở một vài metric.
> Bằng chứng: cả 3 metric generation chính (Faithfulness, Relevance, Completeness) đều giảm so với baseline; chỉ Context Recall giữ nguyên.

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > Retriever lấy đúng nguồn (Context Recall cao) nhưng answer vẫn lệch/thiếu ở câu phức tạp; thêm vào đó có nhiễu do lỗi judge 401 ở một số lượt chấm.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > Biến retrieval_mode tác động lớn nhất: dense giữ chất lượng tốt nhất; sparse và hybrid trong cấu hình hiện tại đều làm Faithfulness/Relevance/Completeness giảm.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Chạy lại với judge ổn định (fix hẳn 401), bật rerank cho hybrid, và tinh chỉnh prompt để ép answer bám evidence + tránh trả lời "Không biết" khi đã có context.
