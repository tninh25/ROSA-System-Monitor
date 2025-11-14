# ROSA AI Desktop – Personal AI Assistant for Windows

ROSA AI Desktop là dự án tích hợp AI trực tiếp vào máy tính Windows, giúp bạn thao tác nhanh hơn, thông minh hơn và tự động hóa nhiều tác vụ hằng ngày. Ứng dụng chạy nền, phản hồi tức thì, hỗ trợ nhập liệu thông minh và nhận dạng giọng nói – hình ảnh trực tiếp.

---

## 🚀 Tính năng chính

### 1. Chatbot (AI giống ChatGPT – Không lưu lịch sử)
- Trò chuyện tự nhiên, phản hồi nhanh.
- Không lưu hội thoại → đảm bảo tính riêng tư tối đa.

### 2. Audio → Text
- Nhấn **Ctrl + M** hoặc **giữ nút giữa chuột** để ghi âm nhanh.
- Tự động chuyển giọng nói thành văn bản.
- Kết quả được **copy vào clipboard** để dùng ngay.

### 3. Image → Text
- Chụp màn hình → Nhấn **Ctrl + I** để trích xuất văn bản từ ảnh vừa chụp.
- Hỗ trợ đọc text trong ảnh nhanh chóng.

### 4. Notes / To-do List
- Tích hợp hệ thống ghi chú.
- To-do list giúp quản lý công việc nhanh và tiện.

### 5. Search
- Tìm kiếm thông tin nhanh thông qua AI ngay trên desktop.

---

## 🔐 Xác thực & Bảo mật

Ứng dụng sử dụng cơ chế xác thực dựa trên **3 thông tin phần cứng**:

- **OSID** (bắt buộc – MachineGuid)
- **MBID** (BaseBoard Serial Number – tùy thiết bị)
- **UUID** (ComputerSystemProduct UUID – tùy thiết bị)

Trước mỗi request chức năng, 3 thông tin này được **mã hóa** và gửi đến server PHP:

- `generate_key.php` → xử lý xác thực  
- `check_version1.php` → kiểm tra phiên bản update

Cơ chế này giúp mỗi thiết bị có định danh riêng, tăng bảo mật và kiểm soát license.

---

## ⚙️ Chế độ chạy

### Chạy nền
- Ứng dụng chạy ẩn và lắng nghe hotkey.

### Hotkey chính
| Tính năng | Phím tắt |
|----------|----------|
| Bật / tắt giao diện | **Ctrl + Space** |
| Audio → Text | **Ctrl + M** hoặc giữ nút giữa chuột |
| Image → Text | **Ctrl + I** |

---

## 🔄 Auto Update – Cập nhật tự động

Hệ thống cập nhật dùng **updater.exe**, hoạt động như sau:

1. Khi chạy `rosa.py`, chương trình gọi `updater.exe`.
2. `updater.exe` kiểm tra bản update tại:  
   `/update` trên baihoc.rosacomputer.vn.
3. File update theo dạng:  
   ```
   rosa_2.0.0.zip
   ```
4. Khi có bản mới:
   - Tải và giải nén.
   - Ghi đè chương trình cũ.
   - Cập nhật `version.txt`.
   - Xóa file cũ → chạy bản mới.
   - Tắt `updater.exe`.

---

## 🏗️ Build file cài đặt (Installer)

Sử dụng **Inno Setup**:

- Cài đặt tự động với quyền admin.
- Tự thêm vào Startup của Windows.
- Chỉ cần mở file `rosa_ai.iss` và build đúng cấu trúc thư mục.

---

## 🧩 Build file .exe bằng Nuitka

Dự án Python được biên dịch sang `.exe` bằng **Nuitka**.

- Chạy file build trong thư mục:
  ```
  build/
  ```
- Nuitka tự sinh file thực thi và các thư mục phụ trợ.

---

## 🗂️ PHP Backend

Backend gồm hai file quan trọng:

| File | Chức năng |
|------|-----------|
| `generate_key.php` | Xác thực thiết bị |
| `check_version1.php` | Kiểm tra phiên bản cập nhật |

---

## 📁 Cấu trúc dự án (tóm tắt)

```
project/
│
├── rosa.py
├── updater.exe
├── version.txt
├── build/
├── installer/
├── php/
│   ├── generate_key.php
│   └── check_version1.php
└── update/
```

---

## ❤️ Đóng góp

Mọi ý tưởng, issue, hoặc pull request đều được hoan nghênh.

---

## 📄 Giấy phép

Dự án thuộc sở hữu của **Rosa Computer**.
