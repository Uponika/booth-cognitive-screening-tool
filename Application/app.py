from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__, static_folder="pages")

# Root route → serve index.html
@app.route("/")
def home():
    return send_from_directory("pages", "index.html")

# Mock Email Endpoint
@app.route("/api/send-email", methods=["POST"])
def send_email():
    data = request.json
    doctor_email = data.get("doctor_email")
    patient_data = data.get("patient_data")
    
    # Simulate processing delay and logging
    print(f"------------------------------------------------")
    print(f"[MOCK EMAIL SERVICE] Sending secure report...")
    print(f"To: {doctor_email}")
    print(f"Subject: Cognitive Assessment Report - {patient_data.get('demographics', {}).get('name', 'Patient')}")
    print(f"Attached: Consent Form, Full Report PDF")
    print(f"------------------------------------------------")
    
    return jsonify({"status": "success", "message": f"Report sent to {doctor_email}"})

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
