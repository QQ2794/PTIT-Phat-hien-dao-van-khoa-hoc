# Thư mục config

Lưu file credentials của Google Cloud Platform (GCP) tại đây.

## Cấu trúc

```
config/
├── gcp-credentials.json    # File service account key (tải từ GCP Console)
└── README.md               # File này
```

## ⚠️ BẢO MẬT

**QUAN TRỌNG**: Thư mục này đã được thêm vào `.gitignore`. 

**KHÔNG BAO GIỜ** push file credentials lên GitHub hoặc bất kỳ repository công khai nào!

## Hướng dẫn

Xem hướng dẫn chi tiết tại: [docs/GCS_UPLOAD_GUIDE.md](../docs/GCS_UPLOAD_GUIDE.md)

### Tóm tắt:

1. Tạo Service Account trên GCP Console
2. Tải file JSON credentials
3. Copy vào thư mục này với tên `gcp-credentials.json`
4. Sử dụng trong code:
   ```python
   CREDENTIALS_PATH = "config/gcp-credentials.json"
   ```

## Kiểm tra

Để kiểm tra file credentials hợp lệ:

```bash
# Kiểm tra file tồn tại
ls config/gcp-credentials.json

# Xem nội dung (cẩn thận, không share!)
cat config/gcp-credentials.json
```

File JSON hợp lệ sẽ có dạng:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "upload-service@your-project.iam.gserviceaccount.com",
  ...
}
```
