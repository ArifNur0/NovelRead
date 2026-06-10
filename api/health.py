from app import create_app

flask_app = create_app()

# Expose a very simple callable for Vercel.
# If this is invoked, you should not see Vercel 404.
handler = flask_app

