from app import create_app

# Vercel (Serverless Functions) expects an exported callable named `handler`.
# We export the Flask WSGI app object directly.

flask_app = create_app()

handler = flask_app

