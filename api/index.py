from flask import Flask, abort, jsonify, request, make_response, Response, send_file
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
import os
import requests
from .static import COMMAND_IDS


app = Flask(__name__)
PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FEEDBACK_CHANNEL_ID = os.getenv("DISCORD_FEEDBACK_CHANNEL_ID")

@app.route("/api/interactions", methods=["POST"])
def interactions():
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    message = timestamp.encode() + request.data
    try:
        verify_key.verify(message, bytes.fromhex(signature))
    except BadSignatureError:
        abort(401, "Incorrect Signature")

    content = request.json
    data = content.get("data", {})

    # ping
    if content["type"] == 1:
        return jsonify({
            "type": 1
        })
    if data.get("id"):
        command_id = data["id"]
        if command_id == COMMAND_IDS["send"]:
            message = f'{data["options"][0]["value"]}\n'
            file=None
            if data.get("resolved"):
                attachments = [v for v in data["resolved"]["attachments"].values()]
                file_link = attachments[0]["url"]
                filename = attachments[0]["filename"]
                r = requests.get(file_link)
                img_b = r.content
                file = {"file": (filename, img_b)}
            url = f"https://discord.com/api/v10/channels/{content['channel_id']}/messages"
            headers = {
                "Authorization": f"Bot {BOT_TOKEN}"
            }
            r = requests.post(url, headers=headers, data={"content": message}, files=file)
            status = r.status_code
            if status != requests.codes.created and status != requests.codes.ok:
                return jsonify({"type": 4, "data": {"content": f"Error: {r.json()}", "flags": 64}})
            return jsonify({"type": 4, "data": {"content": "メッセージを送信しました", "flags": 64}})
        if command_id == COMMAND_IDS["feedback"]:
            message = f'# {data["options"][0]["value"]}\n>>> {data["options"][1]["value"]}\n'
            file=None
            if data.get("resolved"):
                attachments = [v for v in data["resolved"]["attachments"].values()]
                file_link = attachments[0]["url"]
                filename = attachments[0]["filename"]
                r = requests.get(file_link)
                img_b = r.content
                file = {"file": (filename, img_b)}
            url = f"https://discord.com/api/v10/channels/{FEEDBACK_CHANNEL_ID}/messages"
            headers = {
                "Authorization": f"Bot {BOT_TOKEN}"
            }
            r = requests.post(url, headers=headers, data={"content": message}, files=file)
            status = r.status_code
            if status != requests.codes.created and status != requests.codes.ok:
                return jsonify({"type": 4, "data": {"content": f"Error: {r.json()}", "flags": 64}})
            return jsonify({"type": 4, "data": {"content": "フィードバックを送信しました。\nThank You for Your FeedBack❤", "flags": 64}})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
