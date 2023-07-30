from flask import Flask
import pika

app = Flask(__name__)

@app.route('/')
def index():
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)