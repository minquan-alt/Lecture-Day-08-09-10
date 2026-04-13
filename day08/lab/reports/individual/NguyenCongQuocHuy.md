# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Công Quốc Huy 
**Vai trò trong nhóm:** Documentation Owner  
**Ngày nộp:** 13/4/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? 

Trong lab này, tôi đảm nhiệm vai trò viết documentation và hỗ trợ test & evaluation cho toàn bộ hệ thống RAG. 
Cụ thể, tôi chịu trách nhiệm tổng hợp và chuẩn hóa tài liệu mô tả pipeline architecture, giúp các thành viên trong nhóm dễ dàng contact với nhau. Tôi hỗ trợ nhóm sinh Stress Test xác thực lại các test được sinh. Tôi hỗ trợ nhóm eval cùng eval trên tập stress test và grading.

_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn cách một hệ thống RAG hoạt động end-to-end, không chỉ ở mặt kỹ thuật mà còn ở cách tổ chức và trình bày hệ thống một cách rõ ràng. Trước đây tôi chủ yếu tập trung vào model, nhưng qua lab này tôi nhận ra documentation và evaluation đóng vai trò rất quan trọng để đảm bảo hệ thống có thể mở rộng và cải tiến.

Tôi cũng hiểu rõ hơn về cách xây dựng một bộ đánh giá hiệu quả, bao gồm việc thiết kế câu hỏi, xác định expected answer và phân tích kết quả theo nhiều khía cạnh như correctness, completeness và grounding. Ngoài ra, tôi nhận ra rằng việc ghi lại các experiment một cách có hệ thống giúp tránh việc “tune mù” và dễ dàng so sánh giữa các phương pháp khác nhau. Điều này đặc biệt quan trọng khi làm việc nhóm.

_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn 

Điều khiến tôi ngạc nhiên là việc viết documentation không đơn thuần là ghi lại những gì đã làm, mà cần tổ chức lại thông tin sao cho logic, dễ hiểu và có thể sử dụng lại. Khi hệ thống có nhiều thành phần (index, retriever, rerank, generator), nếu không có tài liệu rõ ràng thì rất khó để debug
_________________

---/

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** gq05 - Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access không? Nếu có, cần bao nhiêu ngày và có yêu cầu đặc biệt gì?

**Phân tích:**
- Câu gq05 là một câu kiểm tra RAG khó chịu vì buộc hệ thống kết hợp nhiều mảnh thông tin trong cùng tài liệu thay vì trích từ 1 mảnh đơn lẻ. Trọng tâm không chỉ là trả lời có hay không mà còn xác định đúng phạm vi áp dụng (contractor được xét cấp quyền), sau đó nối sang rule chi tiết của Admin Access (Level 4) gồm ba thành phần bắt buộc: approver, thời gian xử lý, và yêu cầu training. Ở đây, nếu retriever chỉ lấy chunk nói về Level 4 mà thiếu Section 1, model dễ suy diễn là contractor không được cấp; ngược lại nếu chỉ có scope mà thiếu section policy chi tiết, câu trả lời sẽ thiếu approver hoặc SLA thời gian.

- Failure mode quan trọng nhất là nhầm lẫn giữa Level 3 và Level 4, vì cả hai đều liên quan quyền cao nhưng khác phê duyệt. Vì vậy, đáp án tốt cần nêu đủ: contractor được áp dụng quy trình, Level 4 cần IT Manager + CISO, thời gian 5 ngày làm việc, và training security policy bắt buộc. Câu này đo cả độ chính xác lẫn completeness, nên rất phù hợp để bắt lỗi retriever và prompt grounding.
_________________
---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

> Tôi sẽ bổ sung thêm nhiều test case đa dạng hơn, đặc biệt là các câu hỏi yêu cầu reasoning nhiều bước, nhằm đánh giá hệ thống một cách toàn diện hơn. Tôi cũng sẽ tune với các tham số khác.

_________________

---
