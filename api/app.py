from __future__ import annotations

import os
from typing import Any, Callable

from app import create_app

# Vercel (Serverless Functions) expects an exported callable named `handler`.
# The platform will call it with a request/ctx depending on runtime.
# To maximize compatibility, we expose `handler` as Flask's WSGI app.

flask_app = create_app()

# Some Vercel runtimes wrap the request for WSGI; exposing the Flask app directly
# is often the simplest compatible approach.
handler = flask_app

