# Tuning Log — RAG Pipeline (Auto-generated)

> Auto-generated from `run_tuning_experiments.py` results.

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
chunk_strategy = "_split_by_paragraph_recursive"
```

**Scorecard Baseline:**
| Metric           | Average Score |
| ---------------- | ------------- |
| Faithfulness     | 4.56/5 |
| Answer Relevance | 4.67/5 |
| Context Recall   | 5.00/5 |
| Completeness     | 4.50/5 |

**Câu hỏi yếu nhất (điểm thấp):**
- gq05 (Access Control): F=2, R=4, Rc=5, C=2
- gq09 (IT Helpdesk): F=4, R=5, Rc=5, C=4
- gq07 (Insufficient Context): F=5, R=4, Rc=None, C=5

**Giả thuyết nguyên nhân (Error Tree):**
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Retrieval: Dense bỏ lỡ exact keyword / alias
- [ ] Retrieval: Top-k quá ít -> thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài -> lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13
**Biến thay đổi:** retrieval_mode = "hybrid"
**Lý do chọn biến này:**
- Ưu tiên test retrieval variant theo đúng plan (dense/sparse/hybrid).

**Config thay đổi:**
```
retrieval_mode = "hybrid"
chunk_size = 500
overlap = 80
top_k_search = 10
top_k_select = 3
use_rerank = False
```

**Scorecard Variant 1:**
| Metric           | Baseline | Variant 1 | Delta |
| ---------------- | -------- | --------- | ----- |
| Faithfulness     | 4.56/5 | 3.57/5 | -0.98 |
| Answer Relevance | 4.67/5 | 3.89/5 | -0.78 |
| Context Recall   | 5.00/5 | 5.00/5 | +0.00 |
| Completeness     | 4.50/5 | 4.00/5 | -0.50 |

**Nhận xét:**
- Xem chi tiết từng câu trong `scorecard.md` và `rows.json` của variant.

**Kết luận:**
- Dựa trên delta ở bảng trên để quyết định variant có tốt hơn baseline hay không.

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** retrieval_mode = "sparse"
**Config:**
```
retrieval_mode = "sparse"
chunk_size = 500
overlap = 80
top_k_search = 10
top_k_select = 3
use_rerank = False
```

**Scorecard Variant 2:**
| Metric           | Baseline | Variant 1 | Variant 2 | Best |
| ---------------- | -------- | --------- | --------- | ---- |
| Faithfulness     | 4.56/5 | 3.57/5 | 3.50/5 | ? |
| Answer Relevance | 4.67/5 | 3.89/5 | 4.50/5 | ? |
| Context Recall   | 5.00/5 | 5.00/5 | 5.00/5 | ? |
| Completeness     | 4.50/5 | 4.00/5 | 3.88/5 | ? |

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > Điền theo kết quả thực tế sau khi review rows chi tiết.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > So sánh delta các variant để kết luận.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Bật rerank hoặc query transform rồi chạy lại cùng testset.