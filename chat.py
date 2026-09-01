from flask import Flask, render_template_string, request, session, redirect
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

MONSTERS = {
    "rat": ("Giant Rat", 8, 18, 8, 28), "spider": ("Cave Spider", 10, 22, 10, 35),
    "goblin": ("Goblin", 12, 26, 14, 42), "zombie": ("Crypt Zombie", 15, 30, 18, 50),
    "bat": ("Vampire Bat", 11, 25, 16, 46), "serpent": ("Venom Serpent", 18, 34, 22, 65),
    "specter": ("Lost Specter", 20, 38, 28, 75), "scorpion": ("Cave Scorpion", 22, 42, 30, 85),
    "troll": ("Stone Troll", 30, 55, 45, 120), "dragon": ("Young Dragon", 45, 75, 100, 260)
}

ART = {
"rat": '<svg viewBox="0 0 240 150"><path d="M52 105C18 120 8 106 31 96" fill="none" stroke="#74665c" stroke-width="9" stroke-linecap="round"/><path d="M57 96C43 57 70 37 117 44c43 6 59 39 35 63-25 25-76 18-95-11z" fill="#74665c" stroke="#211d1a" stroke-width="7"/><circle cx="82" cy="48" r="15" fill="#74665c" stroke="#211d1a" stroke-width="7"/><circle cx="122" cy="48" r="15" fill="#74665c" stroke="#211d1a" stroke-width="7"/><circle cx="137" cy="73" r="5" fill="#111"/><path d="M151 79l19 4" stroke="#e3a3a3" stroke-width="5"/></svg>',
"spider": '<svg viewBox="0 0 240 150"><ellipse cx="120" cy="83" rx="38" ry="46" fill="#44364b" stroke="#19151d" stroke-width="7"/><circle cx="120" cy="42" r="28" fill="#44364b" stroke="#19151d" stroke-width="7"/><g fill="none" stroke="#44364b" stroke-width="10" stroke-linecap="round"><path d="M88 65L36 28M84 83L25 65M86 101L31 116M94 116L55 143M152 65l52-37M156 83l59-18M154 101l55 15M146 116l39 27"/></g><circle cx="110" cy="40" r="4" fill="#d94b4b"/><circle cx="130" cy="40" r="4" fill="#d94b4b"/></svg>',
"goblin": '<svg viewBox="0 0 240 150"><path d="M79 53L29 28l35 43M161 53l50-25-35 43" fill="#62884d" stroke="#26371e" stroke-width="8"/><path d="M76 122C66 92 72 53 120 47c48 6 54 45 44 75-20 20-68 20-88 0z" fill="#62884d" stroke="#26371e" stroke-width="8"/><circle cx="96" cy="73" r="6" fill="#171914"/><circle cx="144" cy="73" r="6" fill="#171914"/><path d="M96 101h48" stroke="#ddd0ad" stroke-width="7"/></svg>',
"zombie": '<svg viewBox="0 0 240 150"><path d="M77 130l-7-55c-4-31 18-54 50-56 32 2 54 25 50 56l-7 55" fill="#718a75" stroke="#28372b" stroke-width="8"/><path d="M82 55L67 27M158 55l16-29" stroke="#718a75" stroke-width="17" stroke-linecap="round"/><circle cx="96" cy="69" r="7" fill="#1b201b"/><circle cx="144" cy="69" r="7" fill="#1b201b"/><path d="M93 99l15 8 12-9 13 9" fill="none" stroke="#20261f" stroke-width="7"/></svg>',
"bat": '<svg viewBox="0 0 240 150"><path d="M117 61C78 21 38 22 8 10c9 34 24 60 59 76-22 1-37 9-49 20 37 10 70 0 102-24 32 24 65 34 102 24-12-11-27-19-49-20 35-16 50-42 59-76-30 12-70 11-109 51z" fill="#493e59" stroke="#201923" stroke-width="8"/><path d="M120 54v66" stroke="#201923" stroke-width="7"/><circle cx="107" cy="59" r="5" fill="#e04d55"/><circle cx="133" cy="59" r="5" fill="#e04d55"/></svg>',
"serpent": '<svg viewBox="0 0 240 150"><path d="M25 116C70 52 106 142 147 91c25-31 45-31 67-43" fill="none" stroke="#587d45" stroke-width="31" stroke-linecap="round"/><path d="M191 49l37-14-13 28" fill="#587d45" stroke="#294020" stroke-width="7"/><circle cx="202" cy="47" r="4" fill="#111"/></svg>',
"specter": '<svg viewBox="0 0 240 150"><path d="M59 132V64c0-48 122-48 122 0v68l-20-14-20 14-21-14-20 14-21-14z" fill="#aabdc8" stroke="#465764" stroke-width="8"/><circle cx="94" cy="70" r="9" fill="#29333b"/><circle cx="146" cy="70" r="9" fill="#29333b"/><path d="M96 99c17 13 31 13 48 0" fill="none" stroke="#465764" stroke-width="7"/></svg>',
"scorpion": '<svg viewBox="0 0 240 150"><ellipse cx="120" cy="90" rx="43" ry="30" fill="#805535" stroke="#382316" stroke-width="8"/><path d="M81 82L30 55 10 72M81 98L29 117 10 103M159 82l51-27 20 17M159 98l52 19 19-14" fill="none" stroke="#805535" stroke-width="13" stroke-linecap="round"/><path d="M160 78C220 37 229 72 193 101" fill="none" stroke="#805535" stroke-width="12"/><path d="M193 101l22 6-15 15" fill="#805535" stroke="#382316" stroke-width="6"/></svg>',
"troll": '<svg viewBox="0 0 240 150"><path d="M68 133C58 96 63 42 120 31c57 11 62 65 52 102" fill="#60715a" stroke="#293529" stroke-width="9"/><path d="M77 54L31 31l35 48M163 54l46-23-35 48" fill="#60715a" stroke="#293529" stroke-width="9"/><circle cx="94" cy="73" r="9" fill="#20231d"/><circle cx="146" cy="73" r="9" fill="#20231d"/><path d="M85 105h70" stroke="#d8c59e" stroke-width="9"/></svg>',
"dragon": '<svg viewBox="0 0 240 150"><path d="M101 111C63 143 29 137 9 112c26 7 45-5 59-31" fill="#8d4138" stroke="#3b1c19" stroke-width="8"/><path d="M88 91C47 70 25 42 10 12c37 4 72 16 101 48 29-32 64-44 101-48-15 30-37 58-78 79" fill="#71312e" stroke="#3b1c19" stroke-width="8"/><path d="M78 112C78 77 96 54 120 54s42 23 42 58c-20 27-64 27-84 0z" fill="#8d4138" stroke="#3b1c19" stroke-width="8"/><path d="M93 57L84 32M147 57l9-25" stroke="#d2a044" stroke-width="9"/><circle cx="101" cy="80" r="6" fill="#f0c44e"/><circle cx="139" cy="80" r="6" fill="#f0c44e"/></svg>'
}

ICONS = {
"health": '<svg viewBox="0 0 64 64"><path d="M32 56S7 41 7 22C7 9 23 4 32 17 41 4 57 9 57 22c0 19-25 34-25 34z" fill="#c94742" stroke="#251917" stroke-width="5"/></svg>',
"gold": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="25" fill="#d9ad3f" stroke="#3b2a16" stroke-width="5"/><path d="M32 15v34M24 24c0-6 16-7 17 1 1 7-17 7-17 15 0 7 16 8 17 0" fill="none" stroke="#79591c" stroke-width="4"/></svg>',
"room": '<svg viewBox="0 0 64 64"><path d="M10 57V19c0-11 44-11 44 0v38" fill="#704a2f" stroke="#241811" stroke-width="6"/><path d="M22 57V25c0-8 20-8 20 0v32" fill="#151515"/><circle cx="37" cy="39" r="3" fill="#d9ad3f"/></svg>',
"sword": '<svg viewBox="0 0 64 64"><path d="M9 8l9-6 27 27-8 8z" fill="#e3e3e3" stroke="#222" stroke-width="4"/><path d="M11 33l22-10 10 10-22 10z" fill="#c79c3e" stroke="#2c2016" stroke-width="4"/><path d="M37 40l9 9-9 9-9-9z" fill="#67462f" stroke="#241810" stroke-width="4"/></svg>',
"potion": '<svg viewBox="0 0 64 64"><path d="M23 18h18v9l8 24c2 7-6 10-17 10S13 58 15 51l8-24z" fill="#9b4050" stroke="#29191b" stroke-width="5"/><path d="M25 7h14v12H25z" fill="#ddd0aa" stroke="#29191b" stroke-width="5"/><path d="M19 43h27" stroke="#e79a9a" stroke-width="4"/></svg>',
"chest": '<svg viewBox="0 0 64 64"><path d="M8 27h48v29H8z" fill="#80502b" stroke="#281a12" stroke-width="5"/><path d="M9 27c1-19 45-19 46 0" fill="#a06535" stroke="#281a12" stroke-width="5"/><rect x="28" y="31" width="9" height="13" rx="2" fill="#d9ad3f"/></svg>',
"trap": '<svg viewBox="0 0 64 64"><path d="M5 54h54v6H5zM11 52l7-32 7 32 7-32 7 32 7-32 7 32" fill="#8b8b8b" stroke="#222" stroke-width="4"/></svg>',
"search": '<svg viewBox="0 0 64 64"><circle cx="27" cy="27" r="18" fill="none" stroke="#e0cda2" stroke-width="6"/><path d="M41 41l16 16" stroke="#e0cda2" stroke-width="7" stroke-linecap="round"/></svg>',
"rest": '<svg viewBox="0 0 64 64"><path d="M7 42h50v13H7z" fill="#704b31" stroke="#251811" stroke-width="5"/><path d="M10 42V29c0-7 12-7 12 0v13M22 36h33c5 0 6-8 0-8H22z" fill="#d6c29c" stroke="#251811" stroke-width="5"/></svg>',
"exit": '<svg viewBox="0 0 64 64"><path d="M9 57V20c0-12 46-12 46 0v37" fill="#67452d" stroke="#211711" stroke-width="6"/><path d="M22 57V26c0-8 20-8 20 0v31" fill="#151515"/><circle cx="38" cy="39" r="3" fill="#d9ad3f"/></svg>',
"skull": '<svg viewBox="0 0 64 64"><path d="M10 30C10 8 54 8 54 30c0 12-7 17-14 20v7H24v-7c-7-3-14-8-14-20z" fill="#d9d0b9" stroke="#28221c" stroke-width="5"/><circle cx="23" cy="30" r="6" fill="#28221c"/><circle cx="41" cy="30" r="6" fill="#28221c"/><path d="M25 44h14" stroke="#28221c" stroke-width="5"/></svg>'
}

def icon(name): return ICONS[name]

def reset_game():
    session.update(health=100, gold=10, room=1, potions=2, monster=None, monster_hp=0, message="You enter the dungeon.", event_icon="room")

def ensure_game():
    if "health" not in session: reset_game()

def spawn_monster():
    kind=random.choices(list(MONSTERS), weights=[25,18,16,12,10,7,4,4,3,1])[0]
    data=MONSTERS[kind]
    session["monster"]=kind
    session["monster_hp"]=random.randint(data[1],data[2])+session["room"]//4
    session["message"]=f"A {data[0]} blocks your path."
    session["event_icon"]="sword"

def explore():
    session["room"]+=1
    roll=random.random()
    if session["room"]%10==0:
        session["monster"]="dragon"; session["monster_hp"]=90+session["room"]
        session["message"]="A DRAGON guards the next chamber!"; session["event_icon"]="sword"
    elif roll<.52: spawn_monster()
    elif roll<.70:
        gold=random.randint(12,35)+session["room"]; session["gold"]+=gold
        session["message"]=f"You found {gold} gold in an old chest."; session["event_icon"]="chest"
    elif roll<.82:
        session["potions"]+=1; session["message"]="You found a healing potion."; session["event_icon"]="potion"
    elif roll<.92:
        damage=random.randint(5,16); session["health"]-=damage
        session["message"]=f"A hidden trap hits you for {damage} damage."; session["event_icon"]="trap"
    else:
        heal=random.randint(10,22); session["health"]=min(100,session["health"]+heal)
        session["message"]=f"A quiet shrine restores {heal} health."; session["event_icon"]="rest"

def search():
    roll=random.random()
    if roll<.45:
        gold=random.randint(4,22); session["gold"]+=gold; session["message"]=f"You search the room and find {gold} hidden gold."; session["event_icon"]="chest"
    elif roll<.70:
        session["potions"]+=1; session["message"]="You discover a forgotten potion behind a stone."; session["event_icon"]="potion"
    elif roll<.88:
        damage=random.randint(4,12); session["health"]-=damage; session["message"]=f"You trigger a hidden mechanism and take {damage} damage."; session["event_icon"]="trap"
    else:
        session["message"]="You find nothing useful. But you hear something moving nearby..."; session["event_icon"]="search"

def fight():
    kind=session.get("monster")
    if not kind: session["message"]="There is nothing here to fight."; return
    name,lo,hi,glo,ghi=MONSTERS[kind]
    damage=random.randint(10,20)+session["room"]//8; session["monster_hp"]-=damage
    if session["monster_hp"]<=0:
        reward=random.randint(glo,ghi)+session["room"]; session["gold"]+=reward; session["monster"]=None; session["monster_hp"]=0
        session["message"]=f"You defeated the {name} and found {reward} gold."; session["event_icon"]="chest"; return
    enemy=random.randint(lo,hi); session["health"]-=enemy
    session["message"]=f"You hit the {name} for {damage}. It hits back for {enemy}."; session["event_icon"]="sword"

def flee():
    if not session.get("monster"): session["message"]="Nothing is chasing you."; return
    if random.random()<.7:
        session["monster"]=None; session["monster_hp"]=0; session["message"]="You escaped into the next corridor."; session["event_icon"]="exit"
    else:
        damage=random.randint(5,15); session["health"]-=damage; session["message"]=f"You stumble while fleeing and take {damage} damage."; session["event_icon"]="trap"

def rest():
    if session["monster"]: session["message"]="You cannot rest while a monster is here."; return
    heal=random.randint(12,25); session["health"]=min(100,session["health"]+heal); session["message"]=f"You rest beside the cold fire and recover {heal} health."; session["event_icon"]="rest"

def use_potion():
    if session["potions"]<=0: session["message"]="Your potion bag is empty."; return
    if session["health"]>=100: session["message"]="You already have full health."; return
    session["potions"]-=1; heal=random.randint(25,40); session["health"]=min(100,session["health"]+heal); session["message"]=f"You drink a potion and recover {heal} health."; session["event_icon"]="potion"

@app.route("/")
def game():
    ensure_game(); action=request.args.get("action")
    actions={"new":reset_game,"explore":explore,"search":search,"fight":fight,"flee":flee,"rest":rest,"potion":use_potion}
    if action in actions: actions[action]()
    if session["health"]<=0:
        session["health"]=0; session["monster"]=None; session["message"]="You collapse in the darkness. The dungeon wins this time."; session["event_icon"]="skull"
    return render_template_string(PAGE, session=session, icon=icon, art=ART.get(session.get("monster")), monster_data=MONSTERS.get(session.get("monster")))

@app.route("/reset")
def reset(): reset_game(); return redirect("/")

PAGE="""
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dungeon of Chaos</title><style>
*{box-sizing:border-box}body{margin:0;background:#090807;color:#e9dfca;font-family:Georgia,serif;min-height:100vh;padding:22px;background-image:radial-gradient(circle at 50% 0,#33261a 0,#090807 55%)}.game{max-width:940px;margin:auto}.title{text-align:center;font-size:46px;letter-spacing:5px;color:#e0b76b;text-shadow:0 4px 0 #2b1b10,0 0 18px #a06b2b;margin:4px 0}.sub{text-align:center;color:#958a78;margin:0 0 20px;font-family:Arial,sans-serif}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px}.stat{background:#171411;border:2px solid #4e3c28;border-radius:12px;padding:9px 12px;display:flex;align-items:center;gap:9px;box-shadow:inset 0 0 15px #080706}.stat .icon{width:32px;height:32px}.icon svg{width:100%;height:100%;display:block}.stat b{display:block;font:700 12px Arial;color:#897d6a;text-transform:uppercase;letter-spacing:1px}.stat span{font:700 19px Arial;color:#eee}.bar{height:9px;background:#302923;border:1px solid #080706;border-radius:8px;margin-top:5px;overflow:hidden}.hp{height:100%;background:#b9443f;transition:width .5s}.room{background:#100e0c;border:3px solid #55432e;border-radius:18px;min-height:440px;position:relative;padding:22px;box-shadow:0 15px 50px #000,inset 0 0 45px #000}.room:before{content:"";position:absolute;inset:12px;border:1px solid #35291e;border-radius:12px;pointer-events:none}.scene{min-height:270px;display:flex;align-items:center;justify-content:center;flex-direction:column}.event-icon{width:72px;height:72px;margin:4px auto 12px}.message{text-align:center;font:22px Arial,sans-serif;color:#d8cdb9;min-height:54px}.monster{width:min(430px,85%);filter:drop-shadow(0 14px 8px #000);animation:idle 2.5s ease-in-out infinite}.monster svg{width:100%;height:auto;display:block}.controls{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:14px}.btn{border:2px solid #5b472f;background:#1d1813;color:#e9dfca;border-radius:10px;padding:12px 18px;font:bold 15px Arial;cursor:pointer;text-decoration:none;min-width:125px;text-align:center;box-shadow:0 5px 0 #080706;transition:.12s}.btn:hover{transform:translateY(-2px);background:#2b2118;border-color:#9b7543}.btn.danger{border-color:#753934}.btn.good{border-color:#587047}.log{margin-top:16px;background:#0d0c0a;border:1px solid #392d21;border-radius:10px;padding:10px 14px;color:#766c5e;font:13px Arial;text-align:center}.footer{text-align:center;color:#554c41;font:12px Arial;margin-top:15px}@keyframes idle{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}@media(max-width:650px){.stats{grid-template-columns:repeat(2,1fr)}.title{font-size:31px}.room{min-height:400px}.btn{min-width:110px;padding:11px 12px}}
</style></head><body><main class="game"><h1 class="title">DUNGEON OF CHAOS</h1><p class="sub">Every room has a story. Not all of them end well.</p><section class="stats"><div class="stat"><div class="icon">{{ icon('health')|safe }}</div><div><b>Health</b><span>{{session.health}} / 100</span><div class="bar"><div class="hp" style="width:{{session.health}}%"></div></div></div></div><div class="stat"><div class="icon">{{ icon('gold')|safe }}</div><div><b>Gold</b><span>{{session.gold}}</span></div></div><div class="stat"><div class="icon">{{ icon('room')|safe }}</div><div><b>Room</b><span>{{session.room}}</span></div></div><div class="stat"><div class="icon">{{ icon('potion')|safe }}</div><div><b>Potions</b><span>{{session.potions}}</span></div></div></section><section class="room"><div class="scene">{% if art %}<div class="monster">{{art|safe}}</div><div class="message"><strong>{{monster_data[0]}}</strong> — {{session.monster_hp}} HP<br>{{session.message}}</div>{% else %}<div class="event-icon">{{icon(session.event_icon)|safe}}</div><div class="message">{{session.message}}</div>{% endif %}</div><div class="controls">{% if session.health<=0 %}<a class="btn danger" href="/?action=new">START OVER</a>{% elif session.monster %}<a class="btn danger" href="/?action=fight">FIGHT</a><a class="btn" href="/?action=flee">FLEE</a><a class="btn" href="/?action=potion">USE POTION</a>{% else %}<a class="btn good" href="/?action=explore">EXPLORE</a><a class="btn" href="/?action=search">SEARCH</a><a class="btn" href="/?action=rest">REST</a><a class="btn" href="/?action=potion">DRINK POTION</a>{% endif %}</div></section><div class="log">Room {{session.room}} • {{'A monster is blocking the way.' if session.monster else 'The corridor is quiet... for now.'}}</div><div class="footer">Reach room 10, 20, 30... to face a dragon.</div></main></body></html>
"""

if __name__ == "__main__": app.run(host="0.0.0.0", port=5001)
