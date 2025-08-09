from flask import Flask, request, jsonify, render_template
import secrets
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_secret'

# Simple in-memory license storage: { license_key: {status, expires_at} }
licenses = {}

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/api/generate', methods=['POST'])
def generate_license():
    admin_pass = request.args.get('admin_pass')
    if admin_pass != app.config['SECRET_KEY']:
        return jsonify({"error": "Unauthorized"}), 401
    
    license_key = secrets.token_hex(16).upper()
    expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
    
    licenses[license_key] = {
        "status": "active",
        "expires_at": expires_at
    }
    return jsonify({"license": license_key, "expires": expires_at.isoformat()})

@app.route('/api/verify', methods=['GET'])
def verify_license():
    key = request.args.get('key')
    if not key:
        return jsonify({"status": "error", "message": "No key provided"}), 400
    
    license = licenses.get(key)
    if license:
        if license["expires_at"] > datetime.datetime.now():
            return jsonify({"status": "valid"})
        else:
            return jsonify({"status": "expired"})
    return jsonify({"status": "invalid"})

if __name__ == '__main__':
    app.run(debug=True)
