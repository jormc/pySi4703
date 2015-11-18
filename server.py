from si4703 import si4703
from flask import Flask

radio = si4703.si4703()
radio.init()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)