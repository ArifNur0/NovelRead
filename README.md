# Web Koleksi Novel PDF (Flask + MySQL)

Aplikasi web minimalis untuk mengelola koleksi novel PDF beserta cover.

## Struktur
- `app.py` : backend Flask
- `config.py` : konfigurasi MySQL & path upload
- `database/schema.sql` : skema MySQL (users, novels)
- `templates/*` : UI (Tailwind via CDN)
- `static/covers/*` : penyimpanan cover (jpg/png)
- `static/pdfs/*` : penyimpanan file PDF

## 1) Siapkan MySQL (XAMPP/phpMyAdmin)
1. Import/execute `database/schema.sql`.
   - Membuat database: `koleksi_novel`
   - Tabel: `users`, `novels`

2. Buat user admin untuk login:
   - Cara cepat: gunakan route dev `POST /dev/create-user`
   - atau buat manual lewat phpMyAdmin.

> Route dev `POST /dev/create-user` tidak dilindungi autentikasi (untuk local dev saja).

## 2) Konfigurasi environment (opsional)
Jalankan server dengan environment variables berikut (atau biarkan default):
- `MYSQL_HOST` (default: 127.0.0.1)
- `MYSQL_PORT` (default: 3306)
- `MYSQL_USER` (default: root)
- `MYSQL_PASSWORD` (default: blank)
- `MYSQL_DB` (default: koleksi_novel)
- `SECRET_KEY` (default: dev-change-me)

## 3) Install & Run
```bash
pip install -r requirements.txt
python app.py
```
Server: `http://127.0.0.1:5000`

## 4) Alur penggunaan
1. Buka `/login`
2. Login pakai username/password user di tabel `users`
3. Tambah novel di `/upload`
   - Upload cover (jpg/png) dan file PDF
4. Dashboard akan menampilkan cover dan tombol **Baca**

## Catatan
- Lokasi cover/PDF disimpan di folder lokal project.
- Database menyimpan `cover_path` dan `pdf_path` berupa path web `/static/...`.

