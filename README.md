# ROSA System Monitor

ROSA System Monitor là công cụ giám sát quạt CPU chuyên dụng, giúp phát hiện sớm các dấu hiệu bất thường về tản nhiệt và cảnh báo người dùng kịp thời. Ứng dụng chạy nền, tự động khởi động cùng Windows và hoạt động đồng bộ với **Libramonitor** (yêu cầu Libramonitor phải được chạy trước để đọc được thông số quạt).

---

## 🚀 Chức năng chính

- Giám sát tốc độ quạt CPU theo thời gian thực (RPM).
- Theo dõi nhiệt độ CPU để đánh giá hiệu suất tản nhiệt.
- Phát hiện và cảnh báo các trạng thái bất thường về quạt.
- Tự động chạy nền khi máy khởi động.
- Tương thích với mô-đun đọc cảm biến từ Libramonitor.

---

## ⚠️ Các ngưỡng cảnh báo quan trọng

Hệ thống giám sát dựa trên 3 ngưỡng rủi ro chính:

### 1. Quạt hư – **Fan RPM = 0**
- Khi phát hiện quạt ngừng quay hoàn toàn.
- Cảnh báo ngay lập tức vì nguy cơ quá nhiệt rất cao.

### 2. Quạt quay chậm kéo dài  
- Tốc độ quạt không đạt hiệu suất tối đa dù CPU nóng.  
- Nguyên nhân phổ biến: **bám bụi**, **khô keo**, hoặc **cản trở luồng gió**.  
- Ứng dụng đưa ra cảnh báo “hiệu suất thấp kéo dài”.

### 3. Quạt quay nhanh nhưng CPU vẫn không hạ nhiệt  
- Quạt hoạt động hết công suất trong thời gian dài.  
- Nhiệt độ CPU không giảm → nguy cơ:  
  - Keo tản nhiệt hỏng  
  - Tản nhiệt lỏng / không tiếp xúc tốt  
  - Nhiệt độ môi trường quá cao  
  - Hệ thống tản nhiệt suy giảm

---

## ⚙️ Cơ chế hoạt động

### Chạy nền (Background Mode)
- Ứng dụng tự động chạy ẩn và giám sát liên tục.
- Không ảnh hưởng đến hiệu năng hệ thống.

### Yêu cầu: Libramonitor
- ROSA System Monitor **chỉ đọc được thông số quạt khi Libramonitor đã khởi chạy trước**.
- Nếu chưa chạy, ứng dụng sẽ chờ hoặc hiển thị thông báo yêu cầu bật Libramonitor.

### Tự động khởi chạy
- Được cấu hình autostart khi Windows bật.
- Theo dõi định kỳ và xử lý cảnh báo theo thời gian thực.

---

## 🏗️ Build & Installer

Dự án sử dụng **Inno Setup** để tạo file cài đặt.

Trong thư mục `InnoSetup/` có **2 file .iss quan trọng**:

| File | Chức năng |
|------|-----------|
| `setup_admin.iss` | Cài đặt với quyền quản trị (recommended) |
| `setup_normal.iss` | Cài đặt chế độ thường |

Chỉ cần mở các file `.iss` bằng Inno Setup Compiler và build theo đúng cấu trúc thư mục là tạo được file cài đặt.

---

## 📁 Cấu trúc dự án

```
ROSA-System-Monitor/
│
├── src/                     # Mã nguồn chính
├── InnoSetup/               # Chứa 2 file .iss để build installer
│   ├── setup_admin.iss
│   └── setup_normal.iss
├── assets/                  # Icon, tài nguyên giao diện
├── README.md
└── ...
```

---

## ❤️ Đóng góp

Mọi góp ý và đề xuất tính năng đều được chào đón.  
Hãy mở issue hoặc gửi pull request nếu bạn muốn cải thiện dự án.

---

## 📄 Giấy phép

Dự án thuộc sở hữu của **Rosa Computer** và sử dụng nội bộ cho hệ thống giám sát thiết bị.

