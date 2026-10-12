# MƯỜNG LAY TTHC V4.1

Website tra cứu thủ tục hành chính mang thương hiệu UBND phường Mường Lay - Điện Biên.

## Chức năng
- Tra cứu theo mã hoặc tên TTHC.
- Lọc lĩnh vực, mức độ DVC, cấp thực hiện, cơ quan thực hiện.
- Bộ lọc nâng cao: trạng thái, cơ quan công bố, loại thủ tục, thu phí.
- Nút **Chỉ TTHC thực hiện ở cấp xã**.
- Xem chi tiết từng TTHC.
- **Nộp hồ sơ ngay** bằng CitizenURL khi nguồn có liên kết.
- Tạo **QR** cho đường dẫn nộp hồ sơ.
- Xuất **Word (.docx)** từng TTHC.
- Xuất **Excel (.xlsx)** từng TTHC hoặc toàn bộ kết quả đang lọc.
- Đồng bộ dữ liệu tự động bằng GitHub Actions mỗi giờ.
- Có fallback CSV → HTML để giảm rủi ro khi Google thay đổi/gián đoạn xuất CSV.
- Nếu đồng bộ thất bại, workflow không ghi đè dữ liệu cũ bằng file rỗng.
- GitHub Pages tự xuất bản website.

## Nguồn dữ liệu
Nguồn Điện Biên được xác định từ Google Sheets xuất bản của hệ thống điều phối DVC:

`https://docs.google.com/spreadsheets/d/e/2PACX-1vQk2DNzNnpsDR4wTrzBjoy7aKtDKDeubqvnyBdlJstAzxobagxsvSo8kJX2TI9dXHlBMbUjO2htStuw/pub?gid=226385689&single=true&output=csv`

Website **không đọc Google Sheets trực tiếp từ trình duyệt**. GitHub Actions lấy dữ liệu, tạo `data/tthc.json`, sau đó website chỉ đọc file JSON nội bộ. Cách này tránh lỗi CORS ở phía người dùng.

## Cài lên GitHub — chỉ cần làm một lần

### 1. Tạo repository
Ví dụ: `muong-lay-tthc`

### 2. Upload toàn bộ nội dung thư mục này
Giữ nguyên:
- `index.html`
- `data/`
- `scripts/`
- `.github/workflows/`
- `requirements.txt`

### 3. Chạy đồng bộ lần đầu
Vào **Actions** → workflow **Dong bo va xuat ban Mường Lay TTHC** → **Run workflow**.

Workflow sẽ:
1. Cài Python và thư viện.
2. Lấy dữ liệu từ nguồn Điện Biên.
3. Thử CSV trước; nếu CSV lỗi thì thử trang HTML xuất bản.
4. Kiểm tra phải có bản ghi TTHC.
5. Ghi `data/tthc.json` và `data/meta.json`.
6. Deploy GitHub Pages.

### 4. Bật GitHub Pages
Vào **Settings → Pages**. Phần Build and deployment chọn **GitHub Actions**.

Sau lần chạy thành công, GitHub sẽ cung cấp địa chỉ website.

## Đồng bộ tự động
Workflow đặt lịch `17 * * * *`, tức khoảng **mỗi giờ một lần**. Google cũng lưu ý dữ liệu đã Publish to web có thể mất vài phút mới cập nhật sau thay đổi nguồn. 

## Lưu ý
- Website không thu thập hoặc lưu hồ sơ cá nhân của người dân.
- Nút Nộp hồ sơ mở liên kết do nguồn TTHC cung cấp.
- Các thư viện QR/Excel/Word được gọi từ CDN; nếu mạng cơ quan chặn CDN, có thể tải thư viện về và đặt trong `assets/` để chạy nội bộ.


## V4.1 - bản sửa lỗi workflow

Bản V4.1 đã sửa một lỗi quan trọng của workflow cũ: không còn trigger `push` để tránh việc GitHub Actions tự kích hoạt một lượt chạy mới sau khi bot commit dữ liệu, đồng thời chạy đồng bộ và deploy trong cùng một job. Điều này giúp tránh việc lượt deploy đang chạy bị lượt chạy mới hủy.

Workflow cũng thử thêm nguồn Google GViz nếu URL CSV Publish gặp sự cố. Sau khi đồng bộ, workflow kiểm tra `data/tthc.json` phải có bản ghi trước khi deploy.

### Nếu website vẫn báo "Failed to fetch"
Đây thường là do `data/tthc.json` chưa được tạo vì workflow chưa chạy thành công. Vào **Actions → Dong bo va xuat ban Mường Lay TTHC → Run workflow**. Mở lượt chạy và kiểm tra bước **Show sync result**. Nếu bước này báo lỗi, gửi ảnh màn hình phần log màu đỏ cho tôi; tôi sẽ sửa đúng lỗi đó.
