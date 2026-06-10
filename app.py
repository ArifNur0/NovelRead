import os
import uuid
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import config

from werkzeug.security import generate_password_hash

from storage import (
    find_user_by_username,
    add_user,
    get_novels,
    add_novel,
    delete_novel,
)

import vercel_blob

ALLOWED_COVER_EXT = {".jpg", ".jpeg", ".png"}




def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    # Ensure upload dirs exist
    os.makedirs(config.COVERS_DIR, exist_ok=True)
    os.makedirs(config.PDFS_DIR, exist_ok=True)

    # JSON storage (no MySQL)
    # Stored data lives in: data/users.json and data/novels.json


    def login_required(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not session.get("user_id"):
                flash("Silakan login terlebih dahulu.", "error")
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)

        return wrapper

    @app.get("/")
    @login_required
    def dashboard():
        user_id = session.get("user_id")
        novels = [
            n
            for n in get_novels()
            if int(n.get("user_id")) == int(user_id)
        ]
        # newest first (JSON doesn't store ordering guarantees)
        novels = sorted(novels, key=lambda x: x.get("uploaded_at") or "", reverse=True)
        return render_template("dashboard.html", novels=novels)


    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            if not username or not password:
                flash("Username dan password wajib diisi.", "error")
                return redirect(url_for("register"))

            if len(username) < 3 or len(username) > 50:
                flash("Username harus 3-50 karakter.", "error")
                return redirect(url_for("register"))
            if len(password) < 6:
                flash("Password minimal 6 karakter.", "error")
                return redirect(url_for("register"))

            pw_hash = generate_password_hash(password)
            try:
                add_user(username=username, password_hash=pw_hash)
            except ValueError:
                flash("Username sudah digunakan.", "error")
                return redirect(url_for("register"))

            flash("Register berhasil. Silakan login.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            if not username or not password:
                flash("Username dan password wajib diisi.", "error")
                return redirect(url_for("login"))

            user = find_user_by_username(username)
            if not user or not check_password_hash(user["password"], password):

                flash("Login gagal. Cek username/password.", "error")
                return redirect(url_for("login"))

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login berhasil.", "success")
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/api-mapping")
    def api_mapping():
        return render_template("api_mapping.html")

    @app.get("/logout")
    def logout():

        session.clear()
        flash("Anda telah logout.", "success")
        return redirect(url_for("login"))

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            author = (request.form.get("author") or "").strip() or None
            user_id = session.get("user_id")

            if not title:
                flash("Judul wajib diisi.", "error")
                return redirect(url_for("upload"))

            cover_file = request.files.get("cover")
            pdf_file = request.files.get("pdf")

            if not cover_file or cover_file.filename == "":
                flash("Cover wajib diupload.", "error")
                return redirect(url_for("upload"))
            if not pdf_file or pdf_file.filename == "":
                flash("PDF wajib diupload.", "error")
                return redirect(url_for("upload"))

            cover_ext = os.path.splitext(cover_file.filename.lower())[1]
            if cover_ext not in ALLOWED_COVER_EXT:
                flash("Cover harus JPG/PNG.", "error")
                return redirect(url_for("upload"))

            cover_filename = secure_filename(cover_file.filename)
            pdf_filename = secure_filename(pdf_file.filename)

            uid = uuid.uuid4().hex

            # Vercel Blob upload (serverless friendly). Store returned URLs in JSON/KV.
            cover_url = None
            pdf_url = None

            # cover
            if getattr(config, "BLOB_STORE_ID", None) and getattr(config, "BLOB_READ_WRITE_TOKEN", None):
                blob_client = vercel_blob.BlobClient(
                    store_id=config.BLOB_STORE_ID,
                    token=config.BLOB_READ_WRITE_TOKEN,
                )

                cover_bytes = cover_file.read()
                cover_ext_clean = os.path.splitext(cover_filename)[1].lower() or cover_ext
                cover_blob_name = f"covers/{uid}{cover_ext_clean}"
                cover_resp = blob_client.put(
                    blob_name=cover_blob_name,
                    data=cover_bytes,
                    content_type=cover_file.mimetype or "image/jpeg",
                )
                cover_url = cover_resp.url

                # pdf
                pdf_bytes = pdf_file.read()
                pdf_blob_name = f"pdfs/{uid}.pdf"
                pdf_resp = blob_client.put(
                    blob_name=pdf_blob_name,
                    data=pdf_bytes,
                    content_type="application/pdf",
                )
                pdf_url = pdf_resp.url
            else:
                # local dev fallback (writes to static folders)
                cover_on_disk = f"{uid}{cover_ext}"
                pdf_on_disk = f"{uid}.pdf"

                cover_abs = os.path.join(config.COVERS_DIR, cover_on_disk)
                pdf_abs = os.path.join(config.PDFS_DIR, pdf_on_disk)

                cover_file.stream.seek(0)
                pdf_file.stream.seek(0)
                cover_file.save(cover_abs)
                pdf_file.save(pdf_abs)

                cover_url = f"{config.COVER_WEB_PREFIX}/{cover_on_disk}"
                pdf_url = f"{config.PDF_WEB_PREFIX}/{pdf_on_disk}"

            # persist to KV/JSON
            add_novel(
                user_id=int(user_id),
                title=title,
                author=author,
                cover_path=cover_url,
                pdf_path=pdf_url,
            )



            flash("Novel berhasil ditambahkan.", "success")
            return redirect(url_for("dashboard"))

        return render_template("upload.html")

    # Optional helper route (dev): create user quickly
    @app.route("/novels/<int:novel_id>/delete", methods=["POST"])
    @login_required
    def delete_novel_route(novel_id: int):
        user_id = session.get("user_id")

        deleted = delete_novel(user_id=int(user_id), novel_id=int(novel_id))

        if not deleted:
            flash("Novel tidak ditemukan atau tidak dapat dihapus.", "error")
        else:
            flash("Novel berhasil dihapus.", "success")
        return redirect(url_for("dashboard"))


    @app.route("/dev/create-user", methods=["POST"])
    def dev_create_user():

        """Local dev helper (JSON storage): create user."""
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            return {"ok": False, "error": "username/password required"}, 400

        pw_hash = generate_password_hash(password)
        try:
            add_user(username=username, password_hash=pw_hash)
        except ValueError:
            return {"ok": False, "error": "username already exists"}, 409

        return {"ok": True}


    return app


app = create_app()

if __name__ == "__main__":
    # Local run: python app.py
    app.run(host="127.0.0.1", port=5000, debug=True)

