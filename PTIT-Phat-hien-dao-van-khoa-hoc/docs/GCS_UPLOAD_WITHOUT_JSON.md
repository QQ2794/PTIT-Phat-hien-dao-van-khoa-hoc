# Upload lên GCS không cần Service Account Key JSON

## 🎯 Tình huống
Bạn không thể tạo Service Account key JSON do chính sách bảo mật của tổ chức/project.

## ✅ Giải pháp: Dùng gcloud User Authentication

### Bước 1: Cài đặt Google Cloud SDK

**Tải về:**
- Windows: https://cloud.google.com/sdk/docs/install#windows
- Mac/Linux: https://cloud.google.com/sdk/docs/install

**Hoặc dùng PowerShell:**
```powershell
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### Bước 2: Đăng nhập bằng tài khoản Google của bạn

```powershell
# Đăng nhập (mở trình duyệt để xác thực)
gcloud auth login

# Xác nhận đã đăng nhập
gcloud auth list

# Set project (thay YOUR_PROJECT_ID bằng project ID thực tế)
gcloud config set project YOUR_PROJECT_ID

# Cấp quyền cho Python SDK (quan trọng!)
gcloud auth application-default login
```

### Bước 3: Test kết nối

```powershell
# Test xem kết nối có hoạt động không
python src/test_gcs_connection.py
```

Kết quả mong đợi:
```
✅ Kết nối thành công!
   Project ID: your-project-id
📦 Danh sách Buckets:
   • qq2794
```

---

## 📤 CÁCH 1: Upload bằng Python Script

Code đã được cập nhật để tự động dùng gcloud credentials.

```powershell
# Chạy script Python
python src/gcs_upload.py
```

Script sẽ:
- Tự động phát hiện gcloud credentials (không cần file JSON)
- Upload file `data/raw/viblo_data.jsonl`
- Lưu vào `gs://qq2794/raw/viblo/viblo_data.jsonl`

---

## 📤 CÁCH 2: Upload bằng gsutil (Đơn giản hơn)

Script PowerShell tự động hóa toàn bộ quá trình.

```powershell
# Chạy script PowerShell
.\upload_gsutil.ps1
```

Script sẽ tự động:
1. Kiểm tra gsutil đã cài chưa
2. Kiểm tra đã đăng nhập chưa
3. Kiểm tra file tồn tại
4. Upload lên GCS
5. Hiển thị thông tin file

---

## 📤 CÁCH 3: Upload thủ công bằng gsutil

Nếu muốn kiểm soát từng bước:

```powershell
# Upload một file
gsutil cp data/raw/viblo_data.jsonl gs://qq2794/raw/viblo/

# Upload cả thư mục
gsutil -m cp -r data/raw/* gs://qq2794/raw/

# Xem files đã upload
gsutil ls -lh gs://qq2794/raw/

# Download file về (nếu cần)
gsutil cp gs://qq2794/raw/viblo/viblo_data.jsonl data/downloaded/
```

---

## 📤 CÁCH 4: Upload qua GCP Console (Web UI)

Nếu tất cả đều không được:

1. Truy cập: https://console.cloud.google.com/storage/browser/qq2794
2. Click **"UPLOAD FILES"**
3. Chọn file `data/raw/viblo_data.jsonl`
4. Đợi upload xong

**Nhược điểm:** Chậm, không tự động hóa được.

---

## 🔍 Troubleshooting

### ❌ "gcloud: command not found"
**Giải pháp:** Chưa cài Google Cloud SDK hoặc chưa restart terminal.
- Cài SDK từ link trên
- Restart PowerShell/Terminal
- Chạy lại `gcloud auth login`

### ❌ "You do not currently have an active account"
**Giải pháp:** Chưa đăng nhập.
```powershell
gcloud auth login
gcloud auth application-default login
```

### ❌ "AccessDeniedException: 403"
**Giải pháp:** Tài khoản không có quyền truy cập bucket.
- Kiểm tra IAM permissions trên GCP Console
- Cần role: **Storage Object Admin** hoặc **Storage Object Creator**
- Liên hệ admin để cấp quyền

### ❌ "BucketNotFoundException: 404"
**Giải pháp:** Bucket không tồn tại hoặc tên sai.
```powershell
# Xem list buckets hiện có
gsutil ls

# Tạo bucket mới (nếu cần)
gsutil mb -l asia-southeast1 gs://qq2794
```

### ❌ File chưa tồn tại: "data/raw/viblo_data.jsonl"
**Giải pháp:** Chạy crawler trước.
1. Mở `src/crawler.ipynb`
2. Chạy cell đầu tiên để crawl dữ liệu
3. Kiểm tra: `ls data/raw/`

---

## 🆚 So sánh các phương pháp

| Phương pháp | Ưu điểm | Nhược điểm | Khuyên dùng |
|-------------|---------|------------|-------------|
| **Python Script** | Tích hợp sẵn, code chi tiết | Cần cài google-cloud-storage | ✅ Tự động hóa |
| **gsutil (PowerShell)** | Đơn giản, nhanh | Ít tùy chỉnh | ✅ Upload nhanh |
| **gsutil manual** | Linh hoạt, mạnh mẽ | Phải nhớ lệnh | ✅ Debug/test |
| **Web Console** | Trực quan | Chậm, không tự động | ❌ Chỉ dùng khi cần |

---

## ✅ Checklist

- [ ] Đã cài Google Cloud SDK
- [ ] Đã chạy `gcloud auth login`
- [ ] Đã chạy `gcloud auth application-default login`
- [ ] Đã test: `python src/test_gcs_connection.py` → thành công
- [ ] Bucket `qq2794` hiển thị trong danh sách
- [ ] File `data/raw/viblo_data.jsonl` đã tồn tại (chạy crawler nếu chưa)
- [ ] Upload thành công bằng một trong các cách trên

---

## 📚 Tài liệu

- [gcloud auth cheat sheet](https://cloud.google.com/sdk/gcloud/reference/auth)
- [gsutil tool documentation](https://cloud.google.com/storage/docs/gsutil)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)
