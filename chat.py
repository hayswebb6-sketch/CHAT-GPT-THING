from flask import Flask, render_template_string, request, session, redirect
import random, secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

MONSTERS = {
    "rat": ("Giant Rat", 8, 18, 8, 28),
    "spider": ("Cave Spider", 10, 22, 10, 35),
    "goblin": ("Goblin Raider", 12, 26, 14, 42),
    "zombie": ("Crypt Zombie", 15, 30, 18, 50),
    "bat": ("Vampire Bat", 11, 25, 16, 46),
    "serpent": ("Venom Serpent", 18, 34, 22, 65),
    "wraith": ("Lost Wraith", 20, 38, 28, 75),
    "scorpion": ("Cave Scorpion", 22, 42, 30, 85),
    "troll": ("Stone Troll", 30, 55, 45, 120),
    "dragon": ("Ancient Dragon", 48, 78, 120, 300),
    "mimic": ("Mimic", 18, 36, 35, 100),
}

WEAPONS = [
    ("Rusty Sword", 2, "A sword that has seen better days.", "iron_sword.svg"),
    ("Iron Sword", 8, "Reliable and surprisingly sharp.", "iron_sword.svg"),
    ("Steel Sword", 15, "A proper adventurer's blade.", "iron_sword.svg"),
    ("Sharpened Sword", 24, "Someone spent a LOT of time sharpening this.", "iron_sword.svg"),
    ("Iron Cleaver", 32, "Ugly. Heavy. Extremely effective.", "cleaver.svg"),
    ("Flame Blade", 42, "Has a small fire problem. The enemy has a larger one.", "flame_blade.svg"),
    ("Dragon Fang", 58, "Carved from something that really did not want to be carved.", "flame_blade.svg"),
]
WEAPON_BY_NAME = {w[0]: w for w in WEAPONS}


def reset_game():
    session.clear()
    session.update(health=100, gold=20, room=1, potions=2, monster=None, monster_hp=0,
                   message="You enter the dungeon. Something moves in the dark.",
                   xp=0, level=1, combo=0, best_combo=0, weapon="Rusty Sword", attack_bonus=2,
                   map_seen=[1], kills=0, run_gold=20)


def ensure_game():
    if "health" not in session:
        reset_game()


def max_health():
    return 100 + (session.get("level", 1) - 1) * 8


def xp_needed():
    return 35 + session.get("level", 1) * 25


def gain_xp(amount):
    session["xp"] += amount
    while session["xp"] >= xp_needed():
        session["xp"] -= xp_needed()
        session["level"] += 1
        session["health"] = min(max_health(), session["health"] + 30)
        session["message"] += f" LEVEL UP! You reached level {session['level']}!"


def spawn_monster(force=None):
    if force:
        kind = force
    else:
        kind = random.choices(list(MONSTERS), weights=[24,17,16,12,10,7,4,4,3,1,5])[0]
    name, lo, hi, _, _ = MONSTERS[kind]
    session["monster"] = kind
    session["monster_hp"] = random.randint(lo, hi) + session["room"] // 3
    session["message"] = f"A {name} blocks your path."


def explore():
    if session.get("monster"):
        session["message"] = "The monster is still standing in your way."
        return
    session["room"] += 1
    session["map_seen"].append(session["room"])
    session["combo"] = 0
    roll = random.random()
    if session["room"] % 10 == 0:
        spawn_monster("dragon")
        session["monster_hp"] = 140 + session["room"] * 3
        session["message"] = "BOSS CHAMBER — an Ancient Dragon lands in front of you!"
    elif roll < .47:
        spawn_monster()
    elif roll < .61:
        amount = random.randint(15, 42) + session["room"]
        session["gold"] += amount; session["run_gold"] += amount
        session["message"] = f"You crack open a chest and find {amount} gold."
    elif roll < .72:
        session["potions"] += 1
        session["message"] = "A potion glows faintly on a stone altar."
    elif roll < .82:
        damage = random.randint(5, 16)
        session["health"] -= damage
        session["message"] = f"A hidden spike trap hits you for {damage} damage."
    elif roll < .90:
        heal = random.randint(12, 25)
        session["health"] = min(max_health(), session["health"] + heal)
        session["message"] = f"A strange shrine restores {heal} health."
    else:
        search()


def search():
    if session.get("monster"):
        session["message"] = "You cannot search while something is trying to eat you."
        return
    roll = random.random()
    if roll < .30:
        amount = random.randint(8, 30) + session["room"]
        session["gold"] += amount; session["run_gold"] += amount
        session["message"] = f"You find {amount} gold behind a loose brick."
    elif roll < .47:
        session["potions"] += 1
        session["message"] = "You find a dusty potion in a forgotten satchel."
    elif roll < .73:
        current = session["attack_bonus"]
        candidates = [w for w in WEAPONS if w[1] > current]
        if candidates:
            weapon = random.choice(candidates)
            session["weapon"] = weapon[0]
            session["attack_bonus"] = weapon[1]
            session["message"] = f"WEAPON FOUND: {weapon[0]} — +{weapon[1]} ATTACK!"
        else:
            amount = random.randint(20, 60)
            session["gold"] += amount; session["run_gold"] += amount
            session["message"] = f"You find {amount} gold, but your weapon is already excellent."
    elif roll < .86:
        damage = random.randint(4, 13)
        session["health"] -= damage
        session["message"] = f"Your hand triggers a mechanism. You take {damage} damage."
    else:
        session["message"] = "You discover a sealed door covered in ancient writing."


def fight():
    kind = session.get("monster")
    if not kind:
        session["message"] = "There is nothing here to fight."
        return
    name, lo, hi, glo, ghi = MONSTERS[kind]
    damage = random.randint(9, 17) + session.get("level", 1) // 3 + session.get("attack_bonus", 0)
    critical = random.random() < .12
    if critical:
        damage *= 2
    session["monster_hp"] -= damage
    session["combo"] += 1
    session["best_combo"] = max(session["best_combo"], session["combo"])
    if session["monster_hp"] <= 0:
        reward = random.randint(glo, ghi) + session["room"] + session["combo"] * 4
        session["gold"] += reward; session["run_gold"] += reward
        session["kills"] += 1
        gain_xp(18 + session["room"] // 2)
        session["monster"] = None; session["monster_hp"] = 0
        session["message"] = f"{name} defeated! +{reward} gold • +XP • Combo {session['combo']}"
        if random.random() < .22:
            session["potions"] += 1
            session["message"] += " You found a potion."
        return
    enemy = random.randint(lo, hi) + session["room"] // 10
    if kind == "serpent" and random.random() < .28:
        enemy += 7
        session["message"] = f"The serpent's venom burns for {enemy} damage!"
    elif kind == "mimic" and random.random() < .22:
        stolen = min(session["gold"], random.randint(5, 25))
        session["gold"] -= stolen
        session["message"] = f"The Mimic steals {stolen} gold and bites for {enemy}!"
    elif kind == "dragon" and random.random() < .25:
        enemy += 15
        session["message"] = f"The Ancient Dragon breathes fire for {enemy} damage!"
    else:
        session["message"] = f"You hit the {name} for {damage}{' — CRITICAL!' if critical else ''}. It hits for {enemy}."
    session["health"] -= enemy


def flee():
    if not session.get("monster"):
        session["message"] = "Nothing is chasing you."
        return
    if random.random() < .72:
        session["monster"] = None; session["monster_hp"] = 0; session["combo"] = 0
        session["message"] = "You sprint away and hear claws scraping behind you."
    else:
        damage = random.randint(5, 16)
        session["health"] -= damage
        session["message"] = f"You trip while fleeing and take {damage} damage."


def rest():
    if session.get("monster"):
        session["message"] = "You cannot rest while a monster is here."
        return
    heal = random.randint(12, 25)
    session["health"] = min(max_health(), session["health"] + heal)
    session["message"] = f"You rest beside a cold campfire and recover {heal} health."


def use_potion():
    if session["potions"] <= 0:
        session["message"] = "Your potion bag is empty."
        return
    if session["health"] >= max_health():
        session["message"] = "Your health is already full."
        return
    session["potions"] -= 1
    heal = random.randint(25, 42)
    session["health"] = min(max_health(), session["health"] + heal)
    session["message"] = f"You drink a potion and recover {heal} health."


@app.route("/")
def game():
    ensure_game()
    action = request.args.get("action")
    actions = {"new": reset_game, "explore": explore, "search": search,
               "fight": fight, "flee": flee, "rest": rest, "potion": use_potion}
    if action in actions:
        actions[action]()
    if session["health"] <= 0:
        session["health"] = 0
        session["monster"] = None
        session["message"] = "You collapse in the darkness. The dungeon wins this time."
    weapon = WEAPON_BY_NAME.get(session.get("weapon"), WEAPONS[0])
    return render_template_string(PAGE, session=session, monster_data=MONSTERS.get(session.get("monster")),
                                  max_health=max_health, xp_needed=xp_needed, weapon=weapon)


@app.route("/reset")
def reset():
    reset_game()
    return redirect("/")


PAGE = """
<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dungeon of Chaos</title><style>
*{box-sizing:border-box}body{margin:0;background:#080706;color:#eadfc9;font-family:Georgia,serif;min-height:100vh;padding:22px;background-image:radial-gradient(circle at 50% 0,#382718 0,#080706 60%)}
.game{max-width:1000px;margin:auto}.title{text-align:center;font-size:46px;letter-spacing:5px;color:#e1b768;text-shadow:0 4px #2b1b10,0 0 18px #a06b2b;margin:4px 0}.sub{text-align:center;color:#958a78;margin:0 0 18px;font:14px Arial}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:9px;margin-bottom:12px}.stat{background:#171411;border:2px solid #4e3c28;border-radius:12px;padding:10px;min-height:66px}.stat b{display:block;font:700 10px Arial;color:#897d6a;text-transform:uppercase;letter-spacing:1px}.stat span{display:block;font:700 18px Arial;color:#eee;margin-top:4px}.bar{height:7px;background:#302923;border-radius:8px;margin-top:6px;overflow:hidden}.hp{height:100%;background:#b9443f;transition:.3s}.xp{height:100%;background:#bd9342;transition:.3s}
.room{background:#100e0c;border:3px solid #55432e;border-radius:18px;min-height:510px;padding:22px;box-shadow:0 15px 50px #000,inset 0 0 45px #000}.scene{min-height:305px;display:flex;align-items:center;justify-content:center;flex-direction:column}.monster{width:min(460px,88%);filter:drop-shadow(0 16px 8px #000);animation:float 2.4s ease-in-out infinite}.monster img{width:100%;height:auto;display:block}.message{text-align:center;font:19px Arial;color:#d8cdb9;min-height:60px;max-width:800px}.mhp{width:min(430px,82%);height:14px;background:#291a19;border:2px solid #5a342d;border-radius:8px;overflow:hidden;margin:8px}.mhp div{height:100%;background:#a43e39}
.event{width:90px;height:90px;border:2px solid #604b32;border-radius:16px;background:#19140f;display:flex;align-items:center;justify-content:center;font:bold 34px Arial;color:#d9ad3f;margin-bottom:16px}.controls{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:12px}.btn{border:2px solid #5b472f;background:#1d1813;color:#e9dfca;border-radius:10px;padding:12px 17px;font:bold 14px Arial;cursor:pointer;text-decoration:none;min-width:125px;text-align:center;box-shadow:0 5px #080706;transition:.12s}.btn:hover{transform:translateY(-2px);background:#2b2118;border-color:#b08345}.danger{border-color:#753934}.good{border-color:#587047}
.weapon{margin-top:13px;background:#120f0d;border:2px solid #5a452d;border-radius:14px;padding:12px;display:flex;align-items:center;gap:14px}.weapon img{width:72px;height:72px}.weapon-name{font:bold 17px Arial}.attack{font:bold 28px Arial;color:#e7b84e;margin:2px 0}.weapon-desc{font:12px Arial;color:#8e8476}.map{margin-top:13px;background:#0d0c0a;border:1px solid #392d21;border-radius:12px;padding:10px}.maptitle{font:bold 11px Arial;color:#766c5e;text-transform:uppercase;letter-spacing:2px;text-align:center;margin-bottom:8px}.maprow{display:flex;justify-content:center;gap:4px;flex-wrap:wrap}.tile{width:29px;height:29px;border:1px solid #4b3b2a;background:#17130f;border-radius:5px;display:flex;align-items:center;justify-content:center;font:bold 10px Arial;color:#6f6253}.current{border-color:#d4a44a;color:#e8c46f;background:#2a2116;box-shadow:0 0 9px #8a5d27}.boss{border-color:#8c3e38;color:#df7770}.log{text-align:center;color:#766c5e;font:12px Arial;margin-top:10px}.footer{text-align:center;color:#554c41;font:12px Arial;margin-top:10px}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}@media(max-width:760px){.stats{grid-template-columns:repeat(3,1fr)}.title{font-size:32px}}@media(max-width:480px){.stats{grid-template-columns:repeat(2,1fr)}.room{padding:12px}.btn{min-width:105px}}
</style></head><body><main class="game"><h1 class="title">DUNGEON OF CHAOS</h1><p class="sub">Go deeper. Get stronger. Try not to become skeleton furniture.</p>
<section class="stats"><div class="stat"><b>Health</b><span>{{session.health}} / {{max_health()}}</span><div class="bar"><div class="hp" style="width:{{[session.health/max_health()*100,100]|min}}%"></div></div></div><div class="stat"><b>Gold</b><span>{{session.gold}}</span></div><div class="stat"><b>Room</b><span>{{session.room}}</span></div><div class="stat"><b>Potions</b><span>{{session.potions}}</span></div><div class="stat"><b>Level {{session.level}}</b><span>{{session.xp}} XP</span><div class="bar"><div class="xp" style="width:{{[session.xp/xp_needed()*100,100]|min}}%"></div></div></div></section>
<section class="room"><div class="scene">{% if session.health<=0 %}<div class="event">X</div>{% elif session.monster %}<div class="monster"><img src="{{url_for('static',filename='art/'+session.monster+'.svg')}}" alt="{{monster_data[0]}}"></div><div class="mhp"><div style="width:{{[session.monster_hp/(session.monster_hp+40)*100,100]|min}}%"></div></div>{% else %}<div class="event">{{'!' if 'trap' in session.message.lower() else '+'}}</div>{% endif %}<div class="message">{% if session.monster %}<strong>{{monster_data[0]}}</strong> — {{session.monster_hp}} HP<br>{% endif %}{{session.message}}</div></div>
<div class="controls">{% if session.health<=0 %}<a class="btn danger" href="/?action=new">START NEW RUN</a>{% elif session.monster %}<a class="btn danger" href="/?action=fight">FIGHT</a><a class="btn" href="/?action=flee">FLEE</a><a class="btn" href="/?action=potion">USE POTION</a>{% else %}<a class="btn good" href="/?action=explore">EXPLORE</a><a class="btn" href="/?action=search">SEARCH</a><a class="btn" href="/?action=rest">REST</a><a class="btn" href="/?action=potion">DRINK POTION</a>{% endif %}</div></section>
<section class="weapon"><img src="{{url_for('static',filename='art/'+weapon[3])}}" alt="{{weapon[0]}}"><div><div class="weapon-name">{{weapon[0]}}</div><div class="attack">+{{weapon[1]}} ATTACK</div><div class="weapon-desc">{{weapon[2]}}</div></div></section>
<section class="map"><div class="maptitle">Dungeon trail</div><div class="maprow">{% for r in session.map_seen[-20:] %}<div class="tile {% if r==session.room %}current{% endif %} {% if r%10==0 %}boss{% endif %}">{{r}}</div>{% endfor %}</div></section>
<div class="log">Enemies defeated: {{session.kills}} • Current combo: {{session.combo}} • Best combo: {{session.best_combo}} • Run gold: {{session.run_gold}}</div><div class="footer">Every 10th room is a boss chamber. Better weapons can be discovered by searching.</div>
</main></body></html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
