"""Main file for the client."""

from flask import Blueprint, render_template

# register a client blueprint
client_bp = Blueprint("client", __name__)

client_bp.static_folder = "static"
client_bp.template_folder = "templates"

# ==============================================================================

@client_bp.route("/")
def index():
    """Return the index page."""
    return render_template("index.html")

@client_bp.route("/script.js")
def script():
    """Return the script.js file."""
    return client_bp.send_static_file("script.js")

@client_bp.route("/styles.css")
def styles():
    """Return the styles.css file."""
    return client_bp.send_static_file("styles.css")
