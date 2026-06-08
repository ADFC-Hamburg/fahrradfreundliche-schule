#!/usr/bin/env python3

"""
Creates a flask app.
"""

# Imports
from flask import Flask

from app import routes

# Create Flask app
flaskapp = Flask(__name__, static_folder=None)
flaskapp.config.from_prefixed_env('FLASK')
flaskapp.register_blueprint(routes.pages)

# Start app on script execution
if __name__ == '__main__':
    flaskapp.run(host='0.0.0.0')
