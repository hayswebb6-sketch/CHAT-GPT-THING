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
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing:border-box; }
body { margin:0; min-height:100vh; background:radial-gradient(circle at top,#30251d,#090909 65%); color:#eee; font-family:Arial,sans-serif; padding:25px; }
.box { max-width:900px; margin:auto; padding:30px; border:2px solid #66533c; border-radius:20px; background:rgba(18,18,18,.96); box-shadow:0 0 35px #000; }
h1 { font-size:44px; margin:5px; text-shadow:0 0 12px #b78b4a; }
.subtitle { color:#aaa; margin-bottom:25px; }
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:20px 0; }
.stat { padding:15px 8px; border:1px solid #555; border-radius:12px; background:#222; font-size:20px; }
.bar { height:12px; background:#333; border-radius:20px; overflow:hidden; margin-top:8px; }
.hp { height:100%; width:{{ health }}%; background:#b33; transition:width .3s; }
.event { min-height:100px; display:flex; align-items:center; justify-content:center; font-size:25px; margin:25px 0; padding:25px; border-radius:15px; background:#202020; border:1px solid #444; }
.buttons { display:flex; flex-wrap:wrap; justify-content:center; }
button { padding:15px 20px; margin:7px; font-size:17px; cursor:pointer; border-radius:10px; border:1px solid #777; background:#292929; color:white; transition:.15s; }
button:hover { transform:translateY(-3px) scale(1.04); background:#444; box-shadow:0 5px 15px #000; }
.good:hover { background:#205d32; } .danger:hover { background:#702020; } .magic:hover { background:#50306d; }
.log { text-align:left; margin-top:25px; padding:15px; background:#111; border-radius:12px; color:#aaa; font-size:14px; }
a { color:#ddd; }
@media(max-width:650px) { .stats { grid-template-columns:repeat(2,1fr); } h1{font-size:32px;} .event{font-size:20px;} }
</style>
</head>
<body>
<div class="box">
<h1>⚔️ DUNGEON OF CHAOS ⚔️</h1>
<div class="subtitle">Every door is a terrible idea.</div>
<div class="stats">
<div class="stat">❤️ {{ health }}/100<div class="bar"><div class="hp"></div></div></div>
<div class="stat">💰 {{ gold }} gold</div>
<div class="stat">🚪 Floor {{ room }}</div>
<div class="stat">🧪 {{ potions }} potion(s)</div>
</div>
<div class="event">{{ message }}</div>
{% if dead %}
<h2>💀 YOU DIED</h2>
<p>The dungeon wins this round.</p>
<form action="/reset"><button class="good">🔄 New Adventure</button></form>
{% elif won %}
<h2>🏆 ADVENTURE COMPLETE!</h2>
<p>You escaped with <b>{{ gold }} gold</b>.</p>
<form action="/reset"><button class="good">🔄 New Adventure</button></form>
{% else %}
<div class="buttons">
<form method="post"><button name="choice" value="door">🚪 Explore</button></form>
<form method="post"><button name="choice" value="search">🔎 Search</button></form>
<form method="post"><button class="magic" name="choice" value="potion">🧪 Drink Potion</button></form>
<form method="post"><button name="choice" value="rest">🛏️ Rest</button></form>
<form method="post"><button class="danger" name="choice" value="run">🏃 Escape</button></form>
</div>
{% endif %}
<div class="log">📜 <b>Dungeon tip:</b> Search for supplies, save potions for emergencies, and don't trust suspiciously quiet rooms.</div>
</div>
</body>
</html>
"""


def new_game():
    session["health"] = 100
    session["gold"] = 10
    session["room"] = 1
    session["potions"] = 2


@app.route("/", methods=["GET", "POST"])
def game():
    if "health" not in session:
        new_game()

    message = "Choose your next move..."
    dead = False
    won = False

    if request.method == "POST" and session["health"] > 0:
        choice = request.form.get("choice")

        if choice == "door":
            event = random.choices(["monster", "treasure", "trap", "merchant", "nothing", "boss"], weights=[30, 25, 15, 10, 15, 5])[0]
            if event == "monster":
                damage = random.randint(8, 25)
                session["health"] -= damage
                message = f"👹 A goblin ambushes you! You take {damage} damage!"
                if random.randint(1, 4) == 1:
                    reward = random.randint(5, 20)
                    session["gold"] += reward
                    message += f" You defeat it and find {reward} gold!"
            elif event == "treasure":
                found = random.randint(10, 60)
                session["gold"] += found
                message = f"💎 JACKPOT! You found {found} gold!"
            elif event == "trap":
                damage = random.randint(5, 20)
                session["health"] -= damage
                message = f"🪤 FLOOR SPIKES! You lose {damage} HP!"
            elif event == "merchant":
                if session["gold"] >= 15:
                    session["gold"] -= 15
                    session["potions"] += 1
                    message = "🧙 A mysterious merchant sells you a potion for 15 gold."
                else:
                    message = "🧙 A merchant appears... but you don't have enough gold."
            elif event == "boss":
                damage = random.randint(15, 35)
                session["health"] -= damage
                reward = random.randint(50, 120)
                session["gold"] += reward
                message = f"🐉 A dungeon guardian attacks! You take {damage} damage but grab {reward} gold!"
            else:
                message = random.choice(["The room is completely empty. Somehow that's worse.", "You hear footsteps... then realize they're your own.", "Nothing happens. The dungeon is judging you. 👁️"])
            session["room"] += 1
            if session["room"] >= 21 and session["health"] > 0:
                won = True
                message = f"🏆 You reached the surface with {session['gold']} gold!"

        elif choice == "search":
            roll = random.randint(1, 5)
            if roll == 1:
                found = random.randint(15, 45)
                session["gold"] += found
                message = f"🔎 You find a hidden chest containing {found} gold!"
            elif roll == 2:
                session["potions"] += 1
                message = "🔎 You find a dusty potion behind a loose brick!"
            elif roll == 3:
                damage = random.randint(2, 8)
                session["health"] -= damage
                message = f"🕷️ You disturb a nest of spiders! -{damage} HP."
            else:
                message = "🔎 You search everywhere. Nothing but suspicious dust."

        elif choice == "potion":
            if session["potions"] > 0:
                session["potions"] -= 1
                healing = random.randint(20, 40)
                old_health = session["health"]
                session["health"] = min(100, session["health"] + healing)
                message = f"🧪 You recover {session['health'] - old_health} HP!"
            else:
                message = "🧪 You reach for a potion... and remember you have ZERO."

        elif choice == "rest":
            if random.randint(1, 3) == 1:
                damage = random.randint(5, 15)
                session["health"] -= damage
                message = f"😴 You rest... but something attacks you! -{damage} HP."
            else:
                healing = random.randint(8, 18)
                session["health"] = min(100, session["health"] + healing)
                message = f"😴 You safely rest and recover {healing} HP."

        elif choice == "run":
            won = True
            message = f"🏃 You escape with {session['gold']} gold. Cowardice successfully achieved!"

        if session["health"] <= 0:
            session["health"] = 0
            dead = True
            message = "💀 The dungeon has claimed another victim..."

    return render_template_string(PAGE, health=session["health"], gold=session["gold"], room=session["room"], potions=session["potions"], message=message, dead=dead, won=won)


@app.route("/reset")
def reset():
    new_game()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
