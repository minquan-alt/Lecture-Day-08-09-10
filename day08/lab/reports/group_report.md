# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** A2-4C1
**Thành viên:**
| Tên | Vai trò             | GitHub |
| --- | ------------------- | ----- |
|  Hoàng Bá Minh Quang| Tech Lead + Index.py          |  minhquan-alt  |
| Đỗ Lê Thành Nhân  | Retrieval Owner (rag_anwser.py)    | nolandhub   |
| Trần Quang Long| Eval Owner          | quanglong2100   |
| Vũ Minh Quân | Eval Owner            | quandz11-ũ   |
| Nguyễn Công Quốc Huy| Documentation Owner + Test + Eval | ncqh   |
| Nguyễn Anh Tài| Stress Test Case Gen + Test | anhtai204   |

**Ngày nộp:** 13/4/2026  
**Repo:** https://github.com/minquan-alt/Lecture-Day-08-09-10/
---

> **Hướng dẫn nộp group report:**
>
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code, scorecard, hoặc tuning log** — không mô tả chung chung
## 1. Pipeline nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn pipeline của nhóm:
> - Chunking strategy: size, overlap, phương pháp tách (by paragraph, by section, v.v.)
> - Embedding model đã dùng
> - Retrieval mode: dense / hybrid / rerank (Sprint 3 variant)

**Chunking decision:**
> Nhóm dùng chunk_size=500, overlap=80, tách theo section headers vì tài liệu có cấu trúc rõ ràng.

**Embedding model:**
> embeddinggemma-300m (local)

**Retrieval variant (Sprint 3):**
> Chọn tune strategy thành sparse và hybrid vì corpus có cả câu tự nhiên (policy) lẫn mã lỗi và tên chuyên ngành (SLA ticket P1, ERR-403).

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất trong lab.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn.

**Quyết định:** tune retriever strategy sang sparse và hybrid

**Bối cảnh vấn đề:**

Không biết chọn tune hyperparameter nào

**Phương án đã chọn và lý do:**

Chọn tune strategy thành sparse và hybrid vì corpus có cả câu tự nhiên (policy) lẫn mã lỗi và tên chuyên ngành (SLA ticket P1, ERR-403).

**Bằng chứng từ scorecard/tuning-log:**

Tuy vậy, sau khi tune các metrics đánh giá tự động lại kém hơn so với baseline --> Tune thất bại, nhóm lên kế hoạch tune thông số khác đó là sử dụng thêm Rerank và tăng top_k_search (chưa kịp thực hiện)

---

## 3. Kết quả grading questions (100–150 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Câu nào pipeline xử lý tốt nhất? Tại sao? Câu 2 pineline xử lý tốt nhất vì tất cả thông tin trong đều có bằng chứng rõ
> - Câu 5 pipeline lỗi 
> - Câu 7 Pineline được chấm điểm 5/5/None/5 vì tuy không biết nhưng không chỉ nói tôi không biết mà còn đưa ra gợi ý

**Ước tính điểm raw:** 90 / 98

**Câu tốt nhất:** ID: 2 — Lý do: Được LLM Judge chấm toàn bộ 5/5, thông tin đưa ra đầy đủ trích dẫn

**Câu fail:** ID: 5

**Câu gq07 (abstain):** 10/10

**Quy đổi sang 30 điểm nhóm: 27.55

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

> Dựa vào `docs/tuning-log.md`. Tóm tắt kết quả A/B thực tế của nhóm.

**Biến đã thay đổi (chỉ 1 biến):** Strategy retriever: dense -> sparse

**Scorecard Variant 1:**
| Metric           | Baseline | Variant 1 | Delta |
| ---------------- | -------- | --------- | ----- |
| Faithfulness     | 4.56/5   | 3.50/5    | -1.06 |
| Answer Relevance | 4.67/5   | 4.50/5    | -0.17 |
| Context Recall   | 5.00/5   | 5.00/5    | +0.00 |
| Completeness     | 4.50/5   | 3.88/5    | -0.62 |

**Biến đã thay đổi (chỉ 1 biến):** Strategy retriever: dense -> hybrid

**Scorecard Variant 2 (hybrid_50_50):**
| Metric           | Baseline | Variant 2 | Delta |
| ---------------- | -------- | --------- | ----- |
| Faithfulness     | 4.56/5   | 3.57/5    | -0.99 |
| Answer Relevance | 4.67/5   | 3.89/5    | -0.78 |
| Context Recall   | 5.00/5   | 5.00/5    | +0.00 |
| Completeness     | 4.50/5   | 4.00/5    | -0.50 |

**Kết luận:**
> Variant 1 (sparse) không tốt hơn baseline dense.
> Variant 2 (hybrid_50_50) cũng chưa vượt baseline dù đỡ hơn sparse ở một vài metric.
> Bằng chứng: cả 3 metric generation chính (Faithfulness, Relevance, Completeness) đều giảm so với baseline; chỉ Context Recall giữ nguyên.
_________________

---

## 5. Phân công và đánh giá nhóm

> Đánh giá trung thực về quá trình làm việc nhóm.

**Điều nhóm làm tốt:**

> Phân công việc, teamwork tốt

**Điều nhóm làm chưa tốt:**

> Chưa chọn được hướng đi hợp lý (Biến để tune) dẫn đến kết quả tune kém hơn baseline

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? 

> Thử A-B Test với rerank và top_k_search để cố gẳng cải thiện kết quả

_________________

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
