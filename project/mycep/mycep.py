
from flask import Flask, Blueprint, render_template, jsonify, request, abort, redirect, url_for


mycep = Blueprint('mycep', __name__, template_folder='templates', static_folder='static')

@mycep.route('/', methods=['POST','GET'])
def index():
    
    return render_template('index.html'
    )

