# Hệ thống Phát hiện Đạo văn & Tương đồng Văn bản các tài liệu khoa học 

Dự án môn học Khai phá Dữ liệu Lớn (CS246). 
Hệ thống sử dụng PySpark và thuật toán LSH (Locality-Sensitive Hashing) để quét tương đồng văn bản quy mô lớn (dữ liệu Wikipedia Tiếng Việt và Báo chí/Luận văn).

## Thành viên nhóm
1. Phạm Quốc Anh B22DCKH006
2. Nguyễn Trường Giang B22DCKH034
3. Trương Quốc Bình B22DCKH008
4. Đỗ Đức Dũng B22DCKH020

## Cài đặt môi trường
1. Clone repository này về máy:
   ```bash
   git clone [https://github.com/QQ2794/PTIT-Phat-hien-dao-van-khoa-hoc.git](https://github.com/QQ2794/PTIT-Phat-hien-dao-van-khoa-hoc.git)

## Kiến Trúc Luồng Dữ Liệu (Data Pipeline)

Dự án được thiết kế theo kiến trúc Big Data tiêu chuẩn, chia thành 5 giai đoạn cốt lõi:

**Giai đoạn 1: Data Ingestion & Storage (Lưu trữ trên Google Cloud)**
* **Thu thập:** Sử dụng Python/Scrapy (Requests/BeautifulSoup) cào dữ liệu từ VnExpress, VJOL, Viblo,...
* **Lưu trữ (Raw Zone):** Đẩy file định dạng `.jsonl` hoặc `.parquet` chứa nội dung thô lên bucket của Google Cloud Storage (GCS) (VD: `gs://plagiarism-raw-data/`).

**Giai đoạn 2: Preprocessing (Tiền xử lý dữ liệu với Apache Spark)**
* **Load Data:** PySpark đọc dữ liệu trực tiếp từ GCS vào DataFrame (định nghĩa rõ schema để tránh sập Job).
* **Vietnamese NLP:** Làm sạch văn bản, sử dụng `underthesea` bên trong các Spark UDF để tách từ (word segmentation) và loại bỏ stop-words.
* **Lưu trữ (Clean Zone):** Ghi dữ liệu sạch ngược lại GCS dưới định dạng Parquet để tối ưu tốc độ.

**Giai đoạn 3: Xây dựng mô hình với Spark MLlib**
* **Shingling:** Biến đổi văn bản thành các N-grams (3-grams hoặc 5-grams).
* **MinHashing:** Chạy thuật toán MinHash trên Spark để tạo Signatures thu gọn cho mỗi tài liệu.
* **LSH (Locality-Sensitive Hashing):** Băm Signatures vào các bucket (hoạt động tương tự Inverted Index) để tăng tốc độ tìm kiếm ứng viên.
* **Lưu mô hình:** Export model LSH đã huấn luyện xuống GCS.

**Giai đoạn 4: Phân cụm (Clustering) & Đồ thị**
* **Tính toán đồ thị:** Biểu diễn kết quả LSH dưới dạng đồ thị (Vertices = Document, Edges = Jaccard Similarity Score).
* **Gom nhóm:** Dùng Spark GraphX (Connected Components) hoặc KMeans để phân cụm các bài báo có nội dung/chủ đề trùng lặp.

**Giai đoạn 5: Streaming & Web Interface**
* **Backend:** Xây dựng API bằng FastAPI/Flask, nạp model LSH vào bộ nhớ.
* **Luồng xử lý:** Khi User upload văn bản $\rightarrow$ Tiền xử lý $\rightarrow$ Tạo Shingle $\rightarrow$ Tạo Signature $\rightarrow$ Băm qua LSH model để lấy danh sách bucket.
* **So sánh nhanh:** Tính Jaccard Similarity cục bộ với các tài liệu trong bucket và trả kết quả % đạo văn ngay trên giao diện Web.
