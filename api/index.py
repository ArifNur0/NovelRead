import os

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Re-export handler for Vercel's Python entrypoint.
# Vercel expects an ASGI/WSGI-like callable named `handler`.

# Import your Flask app factory
from app import create_app

flask_app = create_app()

# Wrap Flask in DispatcherMiddleware so it can act as a generic WSGI app.
# (Some Vercel environments are strict about the exported callable shape.)

handler = DispatcherMiddleware(flask_app, {})

