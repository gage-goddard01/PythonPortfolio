from flask import Flask, render_template, request
import random
from apps.password_generator import generate_password

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/password_generator", methods=["GET", "POST"])
def password_generator():
    generated_password = None

    if request.method == "POST":
        password_length = request.form["password_length"]
        password_length = int(password_length)
        generated_password= generate_password(password_length)


    return render_template(
        "password_generator.html",
        generated_password = generated_password
    )

@app.route("/rps", methods=["GET", "POST"])
def rps():

    result = None
    player = None
    computer = None

    if request.method == "POST":

        player = request.form["choice"]

        computer = random.choice(
            ["Rock", "Paper", "Scissors"]
        )

        if player == computer:
            result = "It's a tie!"

        elif (
            (player == "Rock" and computer == "Scissors")
            or (player == "Paper" and computer == "Rock")
            or (player == "Scissors" and computer == "Paper")
        ):
            result = "🎉 You Win!"

        else:
            result = "😢 Computer Wins!"

    return render_template(
        "rps.html",
        result=result,
        player=player,
        computer=computer,
    )

@app.route("/cybersecurity")
def cybersecurity():
    return render_template("cybersecurity.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)