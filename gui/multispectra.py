from app import app

from flask import render_template


@app.route('/gui/multispectra', methods=['GET'])
def multispectraPage():
    return render_template('multispectra.html')