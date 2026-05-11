# Hệ Thống Phát Hiện Đạo Văn Trên Tập Dữ Liệu Quy Mô Lớn (ArXiv)

Dự án hướng tới xây dựng một hệ thống phát hiện đạo văn học thuật trên tập dữ liệu quy mô lớn từ kho lưu trữ ArXiv với hơn 3 triệu bài báo khoa học. Hệ thống được thiết kế nhằm tiếp nhận tài liệu PDF đầu vào, thực hiện đối sánh với toàn bộ tập dữ liệu đã được lập chỉ mục, từ đó đưa ra các chỉ số định lượng về mức độ tương đồng và khả năng tồn tại hành vi đạo văn.

Đây là bài tập lớn của Nhóm 9 thuộc học phần Phân tích Khai phá Dữ liệu lớn, Khoa Khoa học Máy tính, Học viện Công nghệ Bưu chính Viễn thông (PTIT).

---

# Mục tiêu dự án

Hệ thống được xây dựng nhằm phát hiện nhiều cấp độ đạo văn khác nhau, bao gồm:

- **Đạo văn nguyên văn (Verbatim Plagiarism):** Sao chép trực tiếp nội dung mà không chỉnh sửa.
- **Đạo văn thay thế từ đồng nghĩa (Synonym Substitution):** Thay đổi từ ngữ nhưng giữ nguyên cấu trúc câu.
- **Đạo văn diễn đạt lại (Paraphrasing):** Biến đổi cấu trúc câu nhưng bảo toàn ý nghĩa.
- **Đạo văn ý tưởng (Idea Plagiarism):** Sử dụng phương pháp, kết quả hoặc ý tưởng nghiên cứu mà không trích dẫn nguồn.
- **Tự đạo văn (Self-Plagiarism):** Tái sử dụng công trình nghiên cứu trước đó của chính tác giả mà không công bố rõ ràng.

---

# Kiến trúc dữ liệu và hạ tầng xử lý

## Quy mô dữ liệu

- Hơn 300.000 bài báo khoa học.
- Khoảng 438GB dữ liệu PDF.
- Khoảng 4GB metadata định dạng JSONL.

## Hạ tầng xử lý

Hệ thống được triển khai trên nền tảng điện toán đám mây với các thành phần:

- Google Colab.
- Google Cloud Storage (GCS).
- Google Dataproc Cluster.

## Kiến trúc Data Lake

Hệ thống tổ chức dữ liệu theo mô hình Medallion Architecture gồm ba tầng:

### Bronze Layer
Lưu trữ dữ liệu thô bao gồm metadata JSONL và các tệp PDF gốc thu thập từ ArXiv.

### Silver Layer
Văn bản được trích xuất từ PDF bằng PyMuPDF, sau đó trải qua quy trình làm sạch và chuẩn hóa dữ liệu.

### Gold Layer
Lưu trữ dữ liệu phục vụ truy vấn và phát hiện đạo văn, bao gồm:
- Sentence chunks.
- MinHash signatures.
- Chỉ mục LSH.
- FAISS vector index.

---

# Kiến trúc phát hiện đạo văn nhiều lớp

Hệ thống sử dụng cơ chế phát hiện nhiều tầng nhằm cân bằng giữa tốc độ xử lý và độ chính xác trên tập dữ liệu lớn.

## Lớp 1 – MinHash LSH

Sử dụng kỹ thuật MinHash kết hợp Locality Sensitive Hashing (LSH) để thực hiện lọc ứng viên nhanh dựa trên độ tương đồng Jaccard. Thành phần này đóng vai trò giảm không gian tìm kiếm ban đầu với độ phức tạp gần hằng số.

## Lớp 2 – Fuzzy String Matching

Áp dụng khoảng cách Levenshtein để so khớp chuỗi ở cấp độ câu nhằm phát hiện các trường hợp chỉnh sửa nhỏ hoặc thay thế từ đồng nghĩa.

## Lớp 3 – Semantic Similarity với FAISS

Văn bản được biểu diễn dưới dạng vector ngữ nghĩa 768 chiều thông qua mô hình Transformer `allenai/specter`, sau đó được lập chỉ mục bằng FAISS để truy vấn tương đồng ngữ nghĩa bằng Cosine Similarity. Thành phần này hỗ trợ phát hiện paraphrase và đạo văn ý tưởng.

## Lớp 4 – Concept Matching

Đánh giá mức độ tương đồng khái niệm thông qua:
- So khớp tiêu đề.
- Độ giao nhau của từ khóa.
- So sánh phát biểu nghiên cứu (claims).
- Phân tích số liệu và kết quả thực nghiệm.

## Lớp 5 – Self-Plagiarism Detection

Phân tích metadata tác giả nhằm phát hiện hành vi tái sử dụng nội dung từ các công trình trước đó của cùng một tác giả.

---

# Quy trình tiền xử lý văn bản

Để nâng cao chất lượng dữ liệu đầu vào, hệ thống áp dụng quy trình làm sạch văn bản gồm nhiều bước:

1. Loại bỏ header và metadata không cần thiết từ ArXiv.
2. Cắt bỏ phần tài liệu tham khảo và bibliography.
3. Chuẩn hóa Unicode theo chuẩn NFKC và xử lý lỗi ligature.
4. Xóa ký tự điều khiển, số trang và nhiễu định dạng.
5. Sửa lỗi xuống dòng giữa từ (hyphenation fix).
6. Loại bỏ email, URL và các thành phần không mang ý nghĩa ngữ nghĩa.

---

# Thành viên thực hiện

- Nguyễn Trường Giang – B22DCKH034
- Phạm Quốc Anh – B22DCKH006
- Trương Quốc Bình – B22DCKH008

**Giảng viên hướng dẫn:** Đặng Hoàng Long
