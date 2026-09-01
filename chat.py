from flask import Flask, render_template_string, request, session, redirect
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

MONSTERS = {
    "rat": ("Giant Rat", 8, 18, 8, 28, "A scarred rat with teeth like tiny daggers."),
    "spider": ("Cave Spider", 10, 22, 10, 35, "Eight legs skitter across the stone."),
    "goblin": ("Goblin Raider", 12, 26, 14, 42, "A green raider raises a battered blade."),
    "zombie": ("Crypt Zombie", 15, 30, 18, 50, "An ancient corpse crawls from the dust."),
    "bat": ("Vampire Bat", 11, 25, 16, 46, "A huge bat dives from the darkness."),
    "serpent": ("Venom Serpent", 18, 34, 22, 65, "A venomous serpent coils around the doorway."),
    "specter": ("Lost Specter", 20, 38, 28, 75, "A pale spirit flickers between worlds."),
    "scorpion": ("Cave Scorpion", 22, 42, 30, 85, "Its pincers click as its tail rises."),
    "troll": ("Stone Troll", 30, 55, 45, 120, "A massive troll blocks the corridor."),
    "dragon": ("Ancient Dragon", 48, 78, 120, 300, "An enormous dragon wakes beneath the mountain.")
}

# All artwork is inline SVG: no emoji are needed by the game.
ART = {
"rat": '<svg viewBox="0 0 300 190"><path d="M80 132C40 153 18 132 48 116" fill="none" stroke="#77685e" stroke-width="11" stroke-linecap="round"/><path d="M77 125C55 83 84 52 142 58c53 6 73 48 43 78-30 29-89 22-108-11z" fill="#77685e" stroke="#211d1a" stroke-width="8"/><circle cx="103" cy="61" r="20" fill="#9a786e" stroke="#211d1a" stroke-width="8"/><circle cx="151" cy="61" r="20" fill="#9a786e" stroke="#211d1a" stroke-width="8"/><circle cx="173" cy="91" r="6"/><path d="M181 99l25 6M82 125l-12 29M135 136l-4 32M169 128l13 27" stroke="#211d1a" stroke-width="8" stroke-linecap="round"/></svg>',
"spider": '<svg viewBox="0 0 300 190"><ellipse cx="150" cy="108" rx="47" ry="57" fill="#493a52" stroke="#18141c" stroke-width="8"/><path d="M150 42c-27 0-38 24-32 45h64c6-21-5-45-32-45z" fill="#493a52" stroke="#18141c" stroke-width="8"/><g fill="none" stroke="#493a52" stroke-width="13" stroke-linecap="round"><path d="M115 76L48 31M109 96L29 73M108 119L32 132M119 139L65 169M185 76l67-45M191 96l80-23M192 119l76 13M181 139l54 30"/></g><g fill="#d84c57"><circle cx="139" cy="67" r="5"/><circle cx="161" cy="67" r="5"/></g></svg>',
"goblin": '<svg viewBox="0 0 300 190"><path d="M105 71L35 38l51 61M195 71l70-33-51 61" fill="#668b50" stroke="#26391f" stroke-width="9"/><path d="M95 159C80 116 91 62 150 55c59 7 70 61 55 104-27 23-83 23-110 0z" fill="#668b50" stroke="#26391f" stroke-width="9"/><path d="M118 91h10M172 91h10" stroke="#181b16" stroke-width="12" stroke-linecap="round"/><path d="M117 126c22 15 44 15 66 0" fill="none" stroke="#262016" stroke-width="8"/><path d="M105 159l-22 22M195 159l22 22" stroke="#26391f" stroke-width="13" stroke-linecap="round"/></svg>',
"zombie": '<svg viewBox="0 0 300 190"><path d="M92 178L83 96C78 53 108 31 150 29c42 2 72 24 67 67l-9 82" fill="#728a75" stroke="#28372c" stroke-width="9"/><path d="M101 70L73 35M199 70l28-35" stroke="#728a75" stroke-width="19" stroke-linecap="round"/><circle cx="122" cy="78" r="9" fill="#1b211b"/><circle cx="178" cy="78" r="9" fill="#1b211b"/><path d="M119 116l18 9 13-10 14 10 17-9" fill="none" stroke="#20271f" stroke-width="8"/><path d="M107 175l-14 12M193 175l14 12" stroke="#28372c" stroke-width="12"/></svg>',
"bat": '<svg viewBox="0 0 300 190"><path d="M145 75C104 32 53 31 13 14c10 45 31 77 72 94-27 1-47 12-62 27 47 11 88-2 127-31 39 29 80 42 127 31-15-15-35-26-62-27 41-17 62-49 72-94-40 17-91 18-132 61z" fill="#514364" stroke="#211923" stroke-width="9"/><path d="M150 67v87" stroke="#211923" stroke-width="9"/><circle cx="132" cy="72" r="6" fill="#e74e59"/><circle cx="168" cy="72" r="6" fill="#e74e59"/><path d="M137 91l13 13 13-13" fill="none" stroke="#211923" stroke-width="6"/></svg>',
"serpent": '<svg viewBox="0 0 300 190"><path d="M25 151C76 69 112 175 164 109c28-36 55-38 99-51" fill="none" stroke="#5c8449" stroke-width="36" stroke-linecap="round"/><path d="M241 58l43-17-17 33" fill="#5c8449" stroke="#294020" stroke-width="8"/><circle cx="253" cy="54" r="5"/><path d="M273 57l15 3M273 57l14-6" stroke="#d34c4c" stroke-width="4"/></svg>',
"specter": '<svg viewBox="0 0 300 190"><path d="M72 171V82c0-61 156-61 156 0v89l-26-18-26 18-26-18-26 18-26-18z" fill="#aec1cc" stroke="#465864" stroke-width="9"/><circle cx="117" cy="89" r="11" fill="#29343b"/><circle cx="183" cy="89" r="11" fill="#29343b"/><path d="M119 126c22 16 40 16 62 0" fill="none" stroke="#465864" stroke-width="8"/><path d="M96 171v14M204 171v14" stroke="#aec1cc" stroke-width="13"/></svg>',
"scorpion": '<svg viewBox="0 0 300 190"><ellipse cx="150" cy="116" rx="53" ry="36" fill="#865a36" stroke="#382316" stroke-width="9"/><path d="M98 105L38 72 13 91M98 126L37 153 13 134M202 105l60-33 25 19M202 126l61 27 24-19" fill="none" stroke="#865a36" stroke-width="15" stroke-linecap="round"/><path d="M194 99C266 46 285 79 239 119" fill="none" stroke="#865a36" stroke-width="14"/><path d="M239 119l29 8-20 21" fill="#865a36" stroke="#382316" stroke-width="7"/></svg>',
"troll": '<svg viewBox="0 0 300 190"><path d="M83 177C67 130 75 54 150 40c75 14 83 90 67 137" fill="#63755d" stroke="#29362b" stroke-width="10"/><path d="M99 68L36 35l47 63M201 68l63-33-47 63" fill="#63755d" stroke="#29362b" stroke-width="10"/><circle cx="116" cy="92" r="11" fill="#20251e"/><circle cx="184" cy="92" r="11" fill="#20251e"/><path d="M102 130h96" stroke="#dfcea5" stroke-width="12"/><path d="M98 177l-20 13M202 177l20 13" stroke="#29362b" stroke-width="15"/></svg>',
"dragon": '<svg viewBox="0 0 300 190"><path d="M121 137C75 176 35 169 12 137c31 8 54-6 72-37" fill="#913f38" stroke="#3a1b18" stroke-width="9"/><path d="M106 113C57 88 30 53 13 12c45 5 85 20 118 59 33-39 73-54 118-59-17 41-44 76-93 101" fill="#71312e" stroke="#3a1b18" stroke-width="9"/><path d="M96 141C96 94 118 67 150 67s54 27 54 74c-25 34-83 34-108 0z" fill="#913f38" stroke="#3a1b18" stroke-width="9"/><path d="M117 72l-11-31M183 72l11-31" stroke="#d4a346" stroke-width="11"/><circle cx="126" cy="99" r="7" fill="#f3c84e"/><circle cx="174" cy="99" r="7" fill="#f3c84e"/><path d="M137 125h26" stroke="#d4a346" stroke-width="6"/></svg>'
}

ICONS = {
"health": '<svg viewBox="0 0 64 64"><path d="M32 56S7 41 7 22C7 9 23 4 32 17 41 4 57 9 57 22c0 19-25 34-25 34z" fill="#c94742" stroke="#251917" stroke-width="5"/></svg>',
"gold": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="25" fill="#d9ad3f" stroke="#3b2a16" stroke-width="5"/><path d="M32 15v34M24 24c0-6 16-7 17 1 1 7-17 7-17 15 0 7 16 8 17 0" fill="none" stroke="#79591c" stroke-width="4"/></svg>',
"room": '<svg viewBox="0 0 64 64"><path d="M10 57V19c0-11 44-11 44 0v38" fill="#704a2f" stroke="#241811" stroke-width="6"/><path d="M22 57V25c0-8 20-8 20 0v32" fill="#151515"/><circle cx="37" cy="39" r="3" fill="#d9ad3f"/></svg>',
"potion": '<svg viewBox="0 0 64 64"><path d="M23 18h18v9l8 24c2 7-6 10-17 10S13 58 15 51l8-24z" fill="#9b4050" stroke="#29191b" stroke-width="5"/><path d="M25 7h14v12H25z" fill="#ddd0aa" stroke="#29191b" stroke-width="5"/><path d="M19 43h27" stroke="#e79a9a" stroke-width="4"/></svg>',
"sword": '<svg viewBox="0 0 64 64"><path d="M9 8l9-6 27 27-8 8z" fill="#e3e3e3" stroke="#222" stroke-width="4"/><path d="M11 33l22-10 10 10-22 10z" fill="#c79c3e" stroke="#2c2016" stroke-width="4"/><path d="M37 40l9 9-9 9-9-9z" fill="#67462f" stroke="#241810" stroke-width="4"/></svg>',
"chest": '<svg viewBox="0 0 64 64"><path d="M8 27h48v29H8z" fill="#80502b" stroke="#281a12" stroke-width="5"/><path d="M9 27c1-19 45-19 46 0" fill="#a06535" stroke="#281a12" stroke-width="5"/><rect x="28" y="31" width="9" height="13" rx="2" fill="#d9ad3f"/></svg>',
"trap": '<svg viewBox="0 0 64 64"><path d="M5 54h54v6H5zM11 52l7-32 7 32 7-32 7 32 7-32 7 32" fill="#8b8b8b" stroke="#222" stroke-width="4"/></svg>',
"search": '<svg viewBox="0 0 64 64"><circle cx="27" cy="27" r="18" fill="none" stroke="#e0cda2" stroke-width="6"/><path d="M41 41l16 16" stroke="#e0cda2" stroke-width="7" stroke-linecap="round"/></svg>',
"rest": '<svg viewBox="0 0 64 64"><path d="M7 42h50v13H7z" fill="#704b31" stroke="#251811" stroke-width="5"/><path d="M10 42V29c0-7 12-7 12 0v13M22 36h33c5 0 6-8 0-8H22z" fill="#d6c29c" stroke="#251811" stroke-width="5"/></svg>',
"exit": '<svg viewBox="0 0 64 64"><path d="M9 57V20c0-12 46-12 46 0v37" fill="#67452d" stroke="#211711" stroke-width="6"/><path d="M22 57V26c0-8 20-8 20 0v31" fill="#151515"/><circle cx="38" cy="39" r="3" fill="#d9ad3f"/></svg>',
"skull": '<svg viewBox="0 0 64 64"><path d="M10 30C10 8 54 8 54 30c0 12-7 17-14 20v7H24v-7c-7-3-14-8-14-20z" fill="#d9d0b9" stroke="#28221c" stroke-width="5"/><circle cx="23" cy="30" r="6" fill="#28221c"/><circle cx="41" cy="30" r="6" fill="#28221c"/><path d="M25 44h14" stroke="#28221c" stroke-width="5"/></svg>'
}

def icon(name):
    return ICONS.get(name, ICONS["room"])

def reset_game():
    session.update(health=100, gold=10, room=1, potions=2, xp=0, level=1,
                   monster=None, monster_hp=0, message="You enter the dungeon.", event_icon="room", log=[])

def ensure_game():
    if "health" not in session:
        reset_game()

def add_log(text):
    log=session.get("log", [])
    log.append(text)
    session["log"]=log[-5:]

def spawn_monster(boss=False):
    choices=[k for k in MONSTERS if k != "dragon"]
    kind="dragon" if boss else random.choices(choices, weights=[25,18,16,12,10,7,4,4,3])[0]
    name,lo,hi,_,_,desc=MONSTERS[kind]
    session["monster"]=kind
    session["monster_hp"]=random.randint(lo,hi)+session["room"]//3
    session["message"]=f"{name}: {desc}"
    session["event_icon"]="sword"

def level_check():
    needed=session["level"]*100
    if session["xp"]>=needed:
        session["xp"]-=needed
        session["level"]+=1
        session["health"]=min(100+session["level"]*8, session["health"]+25)
        session["message"] += f" You reached level {session['level']}!"

def explore():
    session["room"]+=1
    roll=random.random()
    if session["room"]%10==0:
        spawn_monster(True)
        session["message"]="BOSS CHAMBER. " + session["message"]
        add_log(f"Room {session['room']}: boss encounter")
    elif roll<.52:
        spawn_monster()
        add_log(f"Room {session['room']}: monster")
    elif roll<.68:
        gold=random.randint(12,35)+session["room"]
        session["gold"]+=gold; session["message"]=f"A chest contains {gold} gold."; session["event_icon"]="chest"; add_log(f"Found {gold} gold")
    elif roll<.78:
        session["potions"]+=1; session["message"]="You discover a healing potion."; session["event_icon"]="potion"; add_log("Found a potion")
    elif roll<.89:
        damage=random.randint(5,16); session["health"]-=damage; session["message"]=f"A floor trap hits you for {damage} damage."; session["event_icon"]="trap"; add_log(f"Trap: -{damage} HP")
    else:
        heal=random.randint(10,22); session["health"]=min(100+session["level"]*8,session["health"]+heal); session["message"]=f"A shrine restores {heal} health."; session["event_icon"]="rest"; add_log(f"Shrine: +{heal} HP")

def search():
    roll=random.random()
    if roll<.42:
        gold=random.randint(4,22)+session["room"]//2; session["gold"]+=gold; session["message"]=f"You find {gold} hidden gold."; session["event_icon"]="chest"; add_log(f"Search: +{gold} gold")
    elif roll<.64:
        session["potions"]+=1; session["message"]="You find a dusty potion behind a loose stone."; session["event_icon"]="potion"; add_log("Search: potion")
    elif roll<.82:
        damage=random.randint(4,12); session["health"]-=damage; session["message"]=f"Your hand hits a hidden mechanism. You take {damage} damage."; session["event_icon"]="trap"; add_log(f"Search trap: -{damage} HP")
    else:
        session["message"]="Nothing useful. You hear footsteps somewhere ahead."; session["event_icon"]="search"; add_log("Search: nothing")

def fight():
    kind=session.get("monster")
    if not kind: session["message"]="There is nothing here to fight."; return
    name,lo,hi,glo,ghi,_=MONSTERS[kind]
    damage=random.randint(12,22)+session["level"]*2
    session["monster_hp"]-=damage
    if session["monster_hp"]<=0:
        reward=random.randint(glo,ghi)+session["room"]
        xp=random.randint(35,65)+session["room"]
        session["gold"]+=reward; session["xp"]+=xp; session["monster"]=None; session["monster_hp"]=0
        session["message"]=f"You defeated the {name}! +{reward} gold, +{xp} XP."; session["event_icon"]="chest"; add_log(f"Defeated {name}")
        level_check(); return
    enemy=random.randint(lo,hi)+session["room"]//10
    session["health"]-=enemy
    session["message"]=f"You strike for {damage}. The {name} hits back for {enemy}."; session["event_icon"]="sword"; add_log(f"Combat: -{enemy} HP")

def flee():
    if not session.get("monster"): session["message"]="Nothing is chasing you."; return
    if random.random()<.72:
        session["monster"]=None; session["monster_hp"]=0; session["message"]="You escape down a side corridor."; session["event_icon"]="exit"; add_log("Escaped")
    else:
        damage=random.randint(5,15); session["health"]-=damage; session["message"]=f"You stumble while fleeing and take {damage} damage."; session["event_icon"]="trap"

def rest():
    if session.get("monster"): session["message"]="You cannot rest while a monster is here."; return
    heal=random.randint(12,25)+session["level"]
    session["health"]=min(100+session["level"]*8,session["health"]+heal); session["message"]=f"You rest beside a cold fire and recover {heal} health."; session["event_icon"]="rest"; add_log(f"Rest: +{heal} HP")

def use_potion():
    if session["potions"]<=0: session["message"]="Your potion bag is empty."; return
    max_hp=100+session["level"]*8
    if session["health"]>=max_hp: session["message"]="Your health is already full."; return
    session["potions"]-=1; heal=random.randint(25,40); session["health"]=min(max_hp,session["health"]+heal); session["message"]=f"You drink a potion and recover {heal} health."; session["event_icon"]="potion"

def new_game():
    reset_game()
    session["message"]="A new expedition begins."

@app.route("/")
def game():
    ensure_game()
    action=request.args.get("action")
    actions={"new":new_game,"explore":explore,"search":search,"fight":fight,"flee":flee,"rest":rest,"potion":use_potion}
    if action in actions: actions[action]()
    max_hp=100+session["level"]*8
    if session["health"]<=0:
        session["health"]=0; session["monster"]=None; session["message"]="You collapse in the darkness. Your expedition is over."; session["event_icon"]="skull"
    return render_template_string(PAGE, session=session, icon=icon, art=ART.get(session.get("monster")), monster_data=MONSTERS.get(session.get("monster")), max_hp=max_hp)

@app.route("/reset")
def reset():
    reset_game(); return redirect("/")

PAGE="""
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dungeon of Chaos</title><style>
*{box-sizing:border-box}body{margin:0;background:#070706;color:#e8dfcf;font-family:Georgia,serif;min-height:100vh;padding:20px;background-image:radial-gradient(circle at 50% -10%,#44311e 0,#15110d 35%,#070706 72%)}.game{max-width:980px;margin:auto}.title{text-align:center;font-size:44px;letter-spacing:6px;color:#e4b969;text-shadow:0 4px 0 #27180d,0 0 24px #8c5d28;margin:2px 0}.sub{text-align:center;color:#8d8170;margin:0 0 18px;font:13px Arial;letter-spacing:1px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-bottom:13px}.stat{background:linear-gradient(145deg,#1b1712,#100e0b);border:2px solid #4e3d29;border-radius:12px;padding:9px 11px;display:flex;align-items:center;gap:9px;box-shadow:inset 0 0 18px #050403}.stat .icon{width:34px;height:34px;flex:none}.stat b{display:block;font:700 11px Arial;color:#8d806d;letter-spacing:1px;text-transform:uppercase}.stat span{font:700 18px Arial;color:#eee}.bar{height:7px;background:#312923;border-radius:8px;margin-top:5px;overflow:hidden}.hp{height:100%;background:#bd4943;transition:width .45s}.xpbar{height:5px;background:#302a20;border-radius:8px;margin-top:4px;overflow:hidden}.xp{height:100%;background:#a57a36;transition:width .45s}.room{background:radial-gradient(circle at 50% 35%,#1e1914,#0c0a08 70%);border:3px solid #5b472e;border-radius:18px;min-height:510px;position:relative;padding:22px;box-shadow:0 16px 55px #000,inset 0 0 60px #000}.room:before{content:"";position:absolute;inset:11px;border:1px solid #382b20;border-radius:11px;pointer-events:none}.scene{min-height:340px;display:flex;align-items:center;justify-content:center;flex-direction:column}.event-icon{width:80px;height:80px;margin:8px auto 12px;filter:drop-shadow(0 8px 5px #000)}.icon svg,.event-icon svg{width:100%;height:100%;display:block}.monster{width:min(510px,90%);filter:drop-shadow(0 18px 10px #000);animation:idle 2.2s ease-in-out infinite}.monster svg{width:100%;height:auto;display:block}.monster:has(svg[viewBox="0 0 300 190"]){animation:idle 2.2s ease-in-out infinite}.message{text-align:center;font:18px Arial,sans-serif;color:#d8cebd;min-height:54px;max-width:720px;line-height:1.45}.message strong{color:#e4b969;font-size:25px}.monsterhp{width:min(430px,80%);height:10px;background:#281d19;border:1px solid #50322c;border-radius:10px;overflow:hidden;margin:10px auto}.monsterhp div{height:100%;background:#8d3d3d;transition:width .3s}.controls{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:15px}.btn{border:2px solid #58452f;background:#1b1712;color:#e9dfca;border-radius:10px;padding:12px 18px;font:bold 14px Arial;cursor:pointer;text-decoration:none;min-width:128px;text-align:center;box-shadow:0 5px 0 #070605;transition:.13s}.btn:hover{transform:translateY(-2px);background:#2b2118;border-color:#b1884e}.btn.good{border-color:#5e7548}.btn.danger{border-color:#793b36}.btn.blue{border-color:#465d70}.btn:active{transform:translateY(3px);box-shadow:0 2px 0 #070605}.log{margin-top:13px;background:#0d0b09;border:1px solid #382b20;border-radius:10px;padding:10px 14px;color:#70675c;font:12px Arial;text-align:center;min-height:39px}.log span{margin:0 7px}.dead{color:#c95a53;font:bold 25px Georgia;margin-bottom:5px}.footer{text-align:center;color:#50483f;font:11px Arial;margin-top:12px}.boss{color:#c9584f;font:bold 13px Arial;letter-spacing:2px;margin-bottom:3px}@keyframes idle{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-7px) scale(1.015)}}@media(max-width:680px){body{padding:10px}.stats{grid-template-columns:repeat(2,1fr)}.title{font-size:29px;letter-spacing:3px}.room{min-height:500px;padding:15px}.btn{min-width:112px;padding:11px 9px}.scene{min-height:335px}}
</style></head><body><main class="game"><h1 class="title">DUNGEON OF CHAOS</h1><p class="sub">DESCEND. SURVIVE. GET RICH. TRY NOT TO BECOME SKELETON FURNITURE.</p><section class="stats"><div class="stat"><div class="icon">{{icon('health')|safe}}</div><div><b>Health</b><span>{{session.health}} / {{max_hp}}</span><div class="bar"><div class="hp" style="width:{{(session.health/max_hp*100)|round}}%"></div></div></div></div><div class="stat"><div class="icon">{{icon('gold')|safe}}</div><div><b>Gold</b><span>{{session.gold}}</span></div></div><div class="stat"><div class="icon">{{icon('room')|safe}}</div><div><b>Room</b><span>{{session.room}}</span></div></div><div class="stat"><div class="icon">{{icon('potion')|safe}}</div><div><b>Level {{session.level}}</b><span>{{session.xp}} / {{session.level*100}} XP</span><div class="xpbar"><div class="xp" style="width:{{(session.xp/(session.level*100)*100)|round}}%"></div></div></div></div></section><section class="room"><div class="scene">{% if session.health<=0 %}<div class="event-icon">{{icon('skull')|safe}}</div><div class="dead">EXPEDITION FAILED</div><div class="message">{{session.message}}<br>You reached room {{session.room}} with {{session.gold}} gold.</div>{% elif art %}{% if session.monster=='dragon' %}<div class="boss">BOSS ENCOUNTER</div>{% endif %}<div class="monster">{{art|safe}}</div><div class="message"><strong>{{monster_data[0]}}</strong><br>{{monster_data[5]}}</div><div class="monsterhp"><div style="width:{{([session.monster_hp,0]|max / ([monster_data[2]+session.room//3,1]|max)*100)|round}}%"></div></div><div class="message" style="font-size:14px;color:#958a79">{{session.monster_hp}} HP</div>{% else %}<div class="event-icon">{{icon(session.event_icon)|safe}}</div><div class="message">{{session.message}}</div>{% endif %}</div><div class="controls">{% if session.health<=0 %}<a class="btn danger" href="/?action=new">NEW EXPEDITION</a>{% elif session.monster %}<a class="btn danger" href="/?action=fight">FIGHT</a><a class="btn" href="/?action=flee">FLEE</a><a class="btn blue" href="/?action=potion">USE POTION</a>{% else %}<a class="btn good" href="/?action=explore">EXPLORE</a><a class="btn" href="/?action=search">SEARCH</a><a class="btn" href="/?action=rest">REST</a><a class="btn blue" href="/?action=potion">DRINK POTION</a>{% endif %}</div></section><div class="log">{% for item in session.log %}<span>{{item}}</span>{% endfor %}</div><div class="footer">Every 10th room contains a boss. Defeating monsters earns XP and unlocks stronger health.</div></main></body></html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
