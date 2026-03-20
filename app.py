from flask import Flask
from os import getenv

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Bot is running! ✅"

if __name__ == "__main__":
    port = int(getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
