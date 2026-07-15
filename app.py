from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)