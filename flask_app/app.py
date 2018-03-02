import os
from flask import Flask
app = Flask(__name__)

@app.route('/')
def app_root():
    return os.environ.get('APP_NAME', 'no app name')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')