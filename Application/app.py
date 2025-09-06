from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="pages")

# Root route → serve index.html
@app.route("/")
def home():
    return send_from_directory("pages", "index.html")

# Serve other HTML pages in /pages
@app.route("/<path:filename>")
def serve_html(filename):
    return send_from_directory("pages", filename)

# Serve CSS files
@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory("css", filename)

# Serve JS files
@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory("js", filename)

# Serve Images
@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory("images", filename)

# Serve assets (favicon, etc.)
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("assets", filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
