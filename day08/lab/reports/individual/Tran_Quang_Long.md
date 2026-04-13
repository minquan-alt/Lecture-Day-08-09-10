# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Trần Quang Long  
**Vai trò trong nhóm:** Eval Owner
**Ngày nộp:** 13/4/2026 
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong buổi lab này, tôi chịu trách nhiệm chính cho Sprint 4: Evaluation & Scorecard. Tôi xây dựng file eval.py, bao gồm logic tính toán compare_ab để so sánh hiệu suất giữa bản Baseline (Dense Retrieval) và bản Variant (Hybrid Retrieval).
Ngoài việc viết code so sánh, tôi đã thiết lập hệ thống LLM-as-a-Judge bằng cách sử dụng Gemini API trên Google Colab. Tôi đã viết các prompt chấm điểm tự động cho 3 tiêu chí: Faithfulness, Relevance và Completeness. Nhiệm vụ của tôi đóng vai trò là "chốt chặn" cuối cùng, kết nối kết quả từ thám tử tìm kiếm (phần của Tech Lead) để đưa ra các con số đo lường cụ thể, giúp cả nhóm biết được việc nâng cấp lên Hybrid Retrieval có thực sự mang lại giá trị hay không. Cuối cùng, tôi cũng là người cấu trúc lại luồng chạy để hệ thống có thể tự động xuất báo cáo Markdown và file log nộp bài.

_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Concept mà tôi hiểu rõ nhất sau lab này chính là Evaluation Loop và sức mạnh của Hybrid Retrieval. Trước đây, tôi nghĩ AI trả lời đúng hay sai chỉ cần đọc bằng mắt là xong. Tuy nhiên, khi làm việc với 10-20 câu hỏi test, việc đọc thủ công là không khả thi. Việc áp dụng một "AI lớn" để chấm điểm "AI nhỏ" (LLM-as-a-Judge) giúp quy trình chấm điểm khách quan và nhanh hơn hẳn.
Về mặt kỹ thuật, tôi nhận ra rằng Dense Retrieval (tìm kiếm theo ý nghĩa) dù thông minh nhưng lại rất kém khi gặp các từ khóa chuyên ngành, mã hiệu (như mã lỗi IT). Việc kết hợp thêm Sparse Search (BM25) giúp hệ thống bắt được chính xác các từ khóa "cứng", từ đó cải thiện đáng kể điểm Context Recall. RAG không chỉ là về Prompt hay, mà quan trọng nhất là lấy đúng bằng chứng.

_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều khiến tôi bất ngờ nhất là việc cấu hình môi trường cho LLM-as-a-judge tốn thời gian hơn cả việc viết logic chấm điểm. Tôi đã gặp bài toán khó khi phải chọn một model đủ "nhạy bén" để đóng vai trò giám khảo khách quan, nhưng vẫn phải đảm bảo tốc độ xử lý cực nhanh để kịp deadline 4 tiếng của buổi lab.
Việc cân đối giữa chi phí và hiệu năng là một thử thách thực sự: dùng model local (Ollama) thì tiết kiệm nhưng lại gây quá tải tài nguyên khi chạy song song với pipeline RAG, còn dùng model Cloud thì dễ gặp lỗi kết nối, hết token, hay lỗi syntax giữa các model. Khó khăn lớn nhất là xử lý sự bất đồng bộ về định dạng output khi đổi giữa các model; mỗi model có một cách "chào hỏi" khác nhau trước khi trả về JSON điểm số.

_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

Câu hỏi: "ERR-403-AUTH là lỗi gì và cách xử lý?"
Phân tích:
Trong bản Baseline (Dense Retrieval), câu hỏi này nhận điểm Faithfulness và Context Recall rất thấp (chỉ khoảng 1-2/5). Nguyên nhân là vì cụm từ "ERR-403-AUTH" là một mã lỗi kỹ thuật khô khan, vector embedding của nó không có nhiều sự tương đồng về mặt "ngữ nghĩa" với các đoạn văn mô tả trong tài liệu FAQ. Thám tử tìm kiếm chỉ mang về các đoạn văn nói chung chung về "Tài khoản" hoặc "Mật khẩu" nhưng không chứa mã lỗi này.
Khi chuyển sang bản Variant (Hybrid Retrieval), điểm số đã cải thiện lên mức tuyệt đối (5/5). Điều này xảy ra vì thuật toán BM25 (Sparse Search) trong Hybrid đã thực hiện so khớp từ khóa chính xác 100% với chuỗi ký tự "ERR-403-AUTH" có trong tài liệu IT Helpdesk. Kết quả là mẩu tài liệu đúng được đưa vào Prompt, giúp AI trả lời chính xác quy trình xử lý lỗi này. Đây là bằng chứng rõ nhất cho thấy Hybrid Retrieval là bắt buộc đối với các hệ thống tra cứu tài liệu kỹ thuật/doanh nghiệp.

_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Tôi sẽ thử áp dụng thêm bước Rerank (Cross-Encoder) sau khi lấy được kết quả Hybrid để lọc bỏ những đoạn văn bản có score cao nhưng không chứa câu trả lời, từ đó tăng độ chính xác cuối cùng cho câu trả lời của Agent. Bước này tốn thời gian lắm!
