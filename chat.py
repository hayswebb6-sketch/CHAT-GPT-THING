from flask import Flask, render_template_string, request, session, redirect
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

PAGE = """
<!doctype html>
<html>
<head>
<title>Dungeon of Chaos</title>
<style>
body { background:#111; color:#eee; font-family:Arial,sans-serif; text-align:center; padding:30px; }
.box { max-width:700px; margin:auto; padding:30px; border:2px solid #555; border-radius:15px; background:#1b1b1b; }
button { padding:12px 22px; margin:8px; font-size:18px; cursor:pointer; border-radius:8px; }
.stat { font-size:22px; }
.event { font-size:24px; margin:25px; }
</style>
</head>
<body>
<div class="box">
<h1>⚔️ THE DUNGEON OF CHAOS ⚔️</h1>
<p class="stat">❤️ Health: {{ health }} &nbsp; | &nbsp; 💰 Gold: {{ gold }} &nbsp; | &nbsp; 🚪 Room: {{ room }}</p>
{% if message %}<div class="event">{{ message }}</div>{% endif %}
<form method="post">
<button name="choice" value="door">🚪 Open the Door</button>
<button name="choice" value="search">🔎 Search the Room</button>
<button name="choice" value="run">🏃 Run Away</button>
</form>
{% if dead %}<h2>💀 YOU DIED</h2><a href="/reset">Play Again</a>{% endif %}
</div>
</body>
</html>
"""


def new_game():
    session["health"] = 100
    session["gold"] = 10
    session["room"] = 1


@app.route("/", methods=["GET", "POST"])
def game():
    if "health" not in session:
        new_game()

    message = ""
    dead = False

    if request.method == "POST" and session["health"] > 0:
        choice = request.form.get("choice")

        if choice == "door":
            event = random.choice(["monster", "treasure", "trap", "empty"])

            if event == "monster":
                damage = random.randint(10, 30)
                session["health"] -= damage
                message = f"👹 A monster attacks! You lose {damage} HP!"
            elif event == "treasure":
                found = random.randint(5, 40)
                session["gold"] += found
                message = f"💎 You found {found} gold!"
            elif event == "trap":
                damage = random.randint(5, 20)
                session["health"] -= damage
                message = f"🪤 IT'S A TRAP! You lose {damage} HP!"
            else:
                message = "...Nothing happens. Suspicious. 👀"

            session["room"] += 1

        elif choice == "search":
            if random.randint(1, 3) == 1:
                found = random.randint(1, 20)
                session["gold"] += found
                message = f"🔎 You found {found} gold under a rock!"
            else:
                message = "You search everywhere and find absolutely nothing."

        elif choice == "run":
            message = "🏃 You sprint back toward the entrance and escape the dungeon!"

        if session["health"] <= 0:
            session["health"] = 0
            dead = True
            message = "💀 The dungeon has claimed another victim..."

    return render_template_string(PAGE,
        health=session["health"],
        gold=session["gold"],
        room=session["room"],
        message=message,
        dead=dead
    )


@app.route("/reset")
def reset():
    new_game()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
