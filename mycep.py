
from flask import Flask, render_template, jsonify, request, abort, redirect, url_for


app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'mycepproject'


@app.route('/', methods=['POST','GET'])
def index():
    
    return render_template('index.html'
    )

@app.route('/base', methods=['POST','GET'])
def base():
    
    return render_template('base.html'
    )


if __name__ == '__main__':
    app.run(debug=True)