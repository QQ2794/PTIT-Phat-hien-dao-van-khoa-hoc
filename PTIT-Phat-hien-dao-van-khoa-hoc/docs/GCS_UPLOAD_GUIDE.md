# Hướng dẫn Upload dữ liệu lên Google Cloud Storage (GCS)

## 📋 Yêu cầu

- Tài khoản Google Cloud Platform (GCP)
- Python 3.8+
- Package `google-cloud-storage` (đã có trong requirements.txt)

---

## 🚀 Hướng dẫn chi tiết

### Bước 1: Tạo GCP Project và Bucket

1. **Truy cập GCP Console**: https://console.cloud.google.com

2. **Tạo Project mới** (nếu chưa có):
   - Click "Select a project" → "New Project"
   - Đặt tên: `ptit-plagiarism-detection`
   - Click "Create"

3. **Tạo Cloud Storage Bucket**:
   - Vào **Navigation Menu** (☰) → **Cloud Storage** → **Buckets**
   - Click **"CREATE BUCKET"**
   - Điền thông tin:
     - **Name**: `ptit-plagiarism-data` (hoặc tên khác, phải unique toàn cầu)
     - **Location type**: Region
     - **Region**: `asia-southeast1` (Singapore - gần VN nhất)
     - **Storage class**: Standard
     - **Access control**: Uniform
   - Click **"CREATE"**

### Bước 2: Tạo Service Account và tải Credentials

1. **Vào IAM & Admin**:
   - Navigation Menu (☰) → **IAM & Admin** → **Service Accounts**

2. **Tạo Service Account**:
   - Click **"CREATE SERVICE ACCOUNT"**
   - **Service account name**: `upload-service`
   - **Description**: "Service account để upload dữ liệu"
   - Click **"CREATE AND CONTINUE"**

3. **Gán quyền**:
   - **Role**: Chọn `Storage Object Admin` (cho phép upload/download/delete files)
   - Click **"CONTINUE"** → **"DONE"**

4. **Tải Credentials JSON**:
   - Click vào Service Account vừa tạo
   - Tab **"KEYS"** → **"ADD KEY"** → **"Create new key"**
   - Chọn **JSON** → Click **"CREATE"**
   - File JSON sẽ tự động download về máy (VD: `ptit-plagiarism-detection-1a2b3c4d5e6f.json`)

5. **Lưu file Credentials**:
   ```bash
   # Tạo thư mục config (nếu chưa có)
   mkdir -p config
   
   # Copy file JSON vào thư mục config
   # QUAN TRỌNG: Thêm vào .gitignore để không push lên GitHub!
   mv ~/Downloads/ptit-plagiarism-*.json config/gcp-credentials.json
   ```

6. **Thêm vào .gitignore**:
   ```
   # File .gitignore
   config/gcp-credentials.json
   config/*.json
   ```

### Bước 3: Cài đặt Dependencies

```bash
# Cài đặt google-cloud-storage
pip install google-cloud-storage

# Hoặc cài toàn bộ requirements
pip install -r requirements.txt
```

### Bước 4: Cấu hình và chạy Upload Script

1. **Mở file** `src/gcs_upload.py`

2. **Sửa cấu hình** (dòng 163-169):
   ```python
   BUCKET_NAME = "ptit-plagiarism-data"  # Đổi thành tên bucket của bạn
   CREDENTIALS_PATH = "config/gcp-credentials.json"  # Đường dẫn file JSON
   ```

3. **Chạy script**:
   ```bash
   # Từ thư mục gốc project
   python src/gcs_upload.py
   ```

### Bước 5: Kiểm tra kết quả

Kết quả mong đợi:
```
✅ Đã kết nối tới bucket: ptit-plagiarism-data
📤 Đang upload: data/raw/viblo_data.jsonl (2,548,392 bytes)
   → gs://ptit-plagiarism-data/raw/viblo/viblo_data.jsonl
✅ Upload thành công!
   GCS URI: gs://ptit-plagiarism-data/raw/viblo/viblo_data.jsonl

📂 Files trong bucket 'ptit-plagiarism-data' (prefix: 'raw/'):
--------------------------------------------------------------------------------
  📄 raw/viblo/viblo_data.jsonl                      |     2.43 MB | 2026-03-09
--------------------------------------------------------------------------------
  Tổng: 1 file(s)
```

---

## 🔐 Cách 2: Dùng biến môi trường (Recommended)

Thay vì hard-code đường dẫn credentials trong code, bạn có thể set biến môi trường:

### Windows PowerShell:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="D:\path\to\config\gcp-credentials.json"
python src/gcs_upload.py
```

### Windows CMD:
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=D:\path\to\config\gcp-credentials.json
python src/gcs_upload.py
```

### Linux/MacOS:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/config/gcp-credentials.json"
python src/gcs_upload.py
```

Sau đó trong code, set `CREDENTIALS_PATH = None`:
```python
CREDENTIALS_PATH = None  # Sẽ tự động dùng biến môi trường
```

---

## 📦 Các tính năng của script

### 1. Upload một file
```python
uploader.upload_file(
    local_file_path="data/raw/viblo_data.jsonl",
    gcs_path="raw/viblo/viblo_data.jsonl",
    overwrite=False
)
```

### 2. Upload toàn bộ thư mục
```python
uploader.upload_directory(
    local_dir="data/raw",
    gcs_prefix="raw",
    pattern="*.jsonl",  # Hoặc "*" để upload tất cả
    overwrite=False
)
```

### 3. Liệt kê files trong bucket
```python
uploader.list_files(prefix="raw/")
```

---

## 🛠️ Troubleshooting

### ❌ Lỗi: "Could not automatically determine credentials"
**Nguyên nhân**: Chưa set credentials hoặc đường dẫn sai

**Giải pháp**:
- Kiểm tra file JSON có tồn tại không
- Kiểm tra đường dẫn trong `CREDENTIALS_PATH`
- Hoặc set biến môi trường `GOOGLE_APPLICATION_CREDENTIALS`

### ❌ Lỗi: "403 Forbidden"
**Nguyên nhân**: Service account chưa có quyền

**Giải pháp**:
- Vào GCP Console → IAM & Admin → IAM
- Tìm service account và gán role `Storage Object Admin`

### ❌ Lỗi: "404 Not Found"
**Nguyên nhân**: Bucket không tồn tại hoặc tên sai

**Giải pháp**:
- Kiểm tra lại tên bucket trong GCP Console
- Đảm bảo `BUCKET_NAME` trong code khớp với tên bucket

### ❌ File không upload được
**Nguyên nhân**: File `data/raw/viblo_data.jsonl` chưa tồn tại

**Giải pháp**:
- Chạy crawler trước: Mở `src/crawler.ipynb` và chạy cell đầu tiên
- Kiểm tra file đã được tạo: `ls data/raw/`

---

## 💰 Chi phí GCS (Tham khảo)

- **Storage**: ~$0.020/GB/tháng (region Asia Southeast1)
- **Data download**: $0.12/GB (từ Asia ra Internet)
- **Operation**: Tính theo số requests (rất rẻ)

**VD**: Lưu 10GB dữ liệu raw:
- Storage: 10GB × $0.020 = **$0.20/tháng** (~5,000 VND)
- Upload: Miễn phí
- Download: Nếu tải về 10GB = $1.20 (~30,000 VND)

**GCP Free Tier**: 
- 5GB storage/tháng miễn phí
- 1GB network egress/tháng miễn phí

➡️ **Kết luận**: Cho project học tập (~2-5GB), gần như **miễn phí** hoặc < $0.50/tháng

---

## 📚 Tài liệu tham khảo

- [GCS Python Client](https://googleapis.dev/python/storage/latest/index.html)
- [GCS Pricing](https://cloud.google.com/storage/pricing)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)

---

## ✅ Checklist

- [ ] Đã tạo GCP Project
- [ ] Đã tạo GCS Bucket
- [ ] Đã tạo Service Account với quyền Storage Object Admin
- [ ] Đã tải file credentials JSON
- [ ] Đã lưu credentials vào `config/gcp-credentials.json`
- [ ] Đã thêm `config/*.json` vào `.gitignore`
- [ ] Đã cài `google-cloud-storage`
- [ ] Đã sửa `BUCKET_NAME` trong `gcs_upload.py`
- [ ] Đã chạy crawler để tạo file `viblo_data.jsonl`
- [ ] Chạy `python src/gcs_upload.py` thành công
