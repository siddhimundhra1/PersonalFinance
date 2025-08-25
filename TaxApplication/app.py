from flask import Flask, jsonify, request, redirect, render_template

#CONFIGURATION
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
