from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files or "filename" not in request.form:
        return jsonify({"error": "Arquivo ou nome ausente"}), 400

    file = request.files["file"]
    filename = request.form["filename"]

    token_resp = requests.post("https://api.dropboxapi.com/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if token_resp.status_code != 200:
        return jsonify({"error": "Erro ao obter access token", "detalhes": token_resp.text}), 500

    access_token = token_resp.json().get("access_token")
    if not access_token:
        return jsonify({"error": "Access token vazio"}), 500

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": str({
            "path": f"/{filename}",
            "mode": "add",
            "autorename": True,
            "mute": False
        }).replace("'", '"')
    }

    upload_resp = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=file.read())
    if upload_resp.status_code == 200:
        return jsonify({"sucesso": True}), 200
    else:
        return jsonify({"error": "Erro ao enviar para o Dropbox", "detalhes": upload_resp.text}), 500

if __name__ == "__main__":
    app.run(debug=True)