# LỖI TRUY CẬP ODOO - HƯỚNG DẪN FIX

## Lỗi: "Lỗi khi tạo cơ sở dữ liệu: Quyền truy cập bị từ chối"

Lỗi này xảy ra khi PostgreSQL không cấp đủ quyền cho người dùng `odoo`.

---

## ✅ CÁCH FIX NHANH NHẤT (Chạy trong WSL)

Mở WSL terminal tại thư mục `/home/dmin/Business-Internship/` và chạy các lệnh sau:

### 1. Dừng Odoo
```bash
pkill -f "python3 odoo-bin"
sleep 2
```

### 2. Fix quyền PostgreSQL
```bash
# Chạy dưới quyền postgres
sudo -u postgres psql -d data << EOF
DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;
GRANT ALL PRIVILEGES ON DATABASE data TO odoo;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odoo;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odoo;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO odoo;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO odoo;
EOF
```

### 3. Khởi động lại Odoo
```bash
cd ~/Business-Internship
python3 odoo-bin.py -c odoo.conf &
sleep 5
```

### 4. Kiểm tra xem Odoo đã chạy chưa
```bash
ps aux | grep odoo-bin | grep -v grep
```

---

## 📍 CÁCH CHẠY SCRIPT TỰ ĐỘNG

Nếu không muốn chạy từng lệnh, hãy chạy script:

```bash
cd ~/Business-Internship
bash QUICK_FIX.sh
```

---

## 🌐 SAU KHI FIX XONG

1. Mở trình duyệt: **http://localhost:8069**
2. Nếu thấy trang login Odoo → ✅ Thành công
3. Điền:
   - **Mật khẩu chính**: admin (hoặc mật khẩu bạn đã cấu hình)
   - **Tên cơ sở dữ liệu**: data
   - Các thông tin khác tuỳ ý
4. Bấm **"Tạo cơ sở dữ liệu"**

---

## 🔍 KIỂM TRA LOG NẾU CÓ LỖI

Xem log Odoo để biết chi tiết lỗi:

```bash
# Nếu dùng script QUICK_FIX.sh
tail -f /tmp/odoo.log

# Hoặc chạy Odoo trực tiếp để xem log
python3 odoo-bin.py -c odoo.conf
```

---

## ❌ NẾU VẪN KHÔNG ĐƯỢC

Thử reset toàn bộ database:

```bash
# 1. Dừng Odoo
pkill -f "python3 odoo-bin"
sleep 2

# 2. Xoá database cũ
sudo -u postgres dropdb data 2>/dev/null || true

# 3. Tạo database mới
sudo -u postgres createdb -O odoo data

# 4. Chạy Odoo lại
cd ~/Business-Internship
python3 odoo-bin.py -c odoo.conf &
sleep 10

# 5. Kiểm tra
curl http://localhost:8069 2>/dev/null | head -5
```

---

## 📝 GHI CHÚ

- Các module `nhan_su`, `quan_ly_du_an`, `quan_ly_cong_viec` đã được fix lỗi code
- Lỗi "base_registry_signaling already exists" sẽ được tự động fix khi chạy lệnh trên
- Nếu PostgreSQL yêu cầu mật khẩu, hãy chạy: `sudo -u postgres` (cần quyền sudo)

---

**Nếu vẫn có vấn đề, hãy để lại log output ở đây!**
