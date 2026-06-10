# TODO - Web Koleksi Novel PDF

## Step 1: Buat struktur project
- [ ] Buat folder: `templates/`, `static/css`, `static/js`, `static/covers`, `static/pdfs`, `database/`

## Step 2: Buat konfigurasi & dependensi
- [x] Buat `requirements.txt`
- [x] Buat `config.py`

## Step 3: Buat database schema (diganti JSON)
- [x] Skema database diganti penyimpanan JSON untuk menghindari masalah koneksi MySQL

## Step 4: Buat backend Flask
- [x] Buat `app.py` (auth login/logout, dashboard list cover, upload cover+pdf, delete)

## Step 5: Vercel deploy fix (404)
- [x] Perbaiki `vercel.json` runtime untuk function
- [x] Tambahkan/export handler untuk Flask di `api/app.py`

## Step 6: Buat frontend (Tailwind)
- [x] Buat `templates/base.html`
- [x] Buat `templates/login.html`
- [x] Buat `templates/dashboard.html`
- [x] Buat `templates/upload.html`
- [x] Buat `static/css/styles.css` (opsional)
- [x] Buat `static/js/main.js` (jika diperlukan)

## Step 7: Ganti storage users/novels ke Vercel Blob (tanpa KV)
- [ ] Update `config.py` untuk pastikan `BLOB_STORE_ID` dan `BLOB_READ_WRITE_TOKEN` ada
- [ ] Refactor `storage.py`: users/novels -> blob files `data/users.json` dan `data/novels.json`
- [ ] Pastikan add/delete user/novel bekerja dengan atomic-ish update (read-modify-write)
- [ ] Push + redeploy Vercel
- [ ] Uji: register/login/upload/dashboard/baca/hapus

