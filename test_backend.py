from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/test')
def test():
    return "✅ Backend received the request successfully!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
