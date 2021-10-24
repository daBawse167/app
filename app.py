from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/box', methods=['GET', 'POST'])
def box():
    message = [x for x in request.form.values()][0]
    return render_template("home.html", message=message)

if __name__ == '__main__':
    app.run(debug=True)
