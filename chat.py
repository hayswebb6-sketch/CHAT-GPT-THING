from flask import Flask, render_template_string, request, session, redirect
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Real vector artwork. No emoji are used for the game UI.
ICONS = {
    "health": '<svg viewBox="0 0 64 64"><path d="M32 56S7 41 7 22C7 9 23 4 32 17 41 4 57 9 57 22c0 19-25 34-25 34z" fill="#c43d38" stroke="#211716" stroke-width="5"/></svg>',
    "gold": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="25" fill="#d6aa3b" stroke="#392815" stroke-width="5"/><circle cx="32" cy="32" r="17" fill="none" stroke="#8b681f" stroke-width="3"/><path d="M32 16v32M24 24c0-6 16-7 17 1 1 7-17 7-17 15 0 7 16 8 17 0" fill="none" stroke="#765518" stroke-width="4"/></svg>',
    "room": '<svg viewBox="0 0 64 64"><path d="M10 57V19c0-11 44-11 44 0v38" fill="#67462e" stroke="#211711" stroke-width="6"/><path d="M22 57V25c0-8 20-8 20 0v32" fill="#171717"/><circle cx="37" cy="39" r="3" fill="#d6aa3b"/></svg>',
    "potion": '<svg viewBox="0 0 64 64"><path d="M23 18h18v9l8 24c2 7-6 10-17 10S13 58 15 51l8-24z" fill="#91404c" stroke="#25191a" stroke-width="5"/><path d="M25 7h14v12H25z" fill="#d8c79f" stroke="#25191a" stroke-width="5"/><path d="M19 43h27" stroke="#d98a8a" stroke-width="4"/></svg>',
    "sword": '<svg viewBox="0 0 64 64"><path d="M10 8l8-6 27 27-8 8z" fill="#ddd" stroke="#242424" stroke-width="4"/><path d="M11 33l22-10 10 10-22 10z" fill="#c49a3b" stroke="#2b2017" stroke-width="4"/><path d="M37 40l9 9-9 9-9-9z" fill="#67452d" stroke="#241810" stroke-width="4"/></svg>',
    "chest": '<svg viewBox="0 0 64 64"><path d="M8 27h48v29H8z" fill="#80502b" stroke="#271a12" stroke-width="5"/><path d="M9 27c1-19 45-19 46 0" fill="#9b6335" stroke="#271a12" stroke-width="5"/><rect x="28" y="31" width="9" height="13" rx="2" fill="#d6aa3b"/></svg>',
    "trap": '<svg viewBox="0 0 64 64"><path d="M5 53h54v6H5zM11 51l7-32 7 32 7-32 7 32 7-32 7 32" fill="#858585" stroke="#202020" stroke-width="4"/></svg>',
    "search": '<svg viewBox="0 0 64 64"><circle cx="27" cy="27" r="18" fill="none" stroke="#d8c79f" stroke-width="6"/><path d="M41 41l16 16" stroke="#d8c79f" stroke-width="7" stroke-linecap="round"/></svg>',
    "rest": '<svg viewBox="0 0 64 64"><path d="M7 42h50v13H7z" fill="#6d4930" stroke="#211711" stroke-width="5"/><path d="M10 42V29c0-7 12-7 12 0v13M22 36h33c5 0 6-8 0-8H22z" fill="#d5c09a" stroke="#211711" stroke-width="5"/></svg>',
    "run": '<svg viewBox="0 0 64 64"><circle cx="39" cy="10" r="7" fill="#d5c09a"/><path d="M35 19l-8 15 13 6 10 13M28 34L13 45M40 40L29 57" fill="none" stroke="#d5c09a" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "scroll": '<svg viewBox="0 0 64 64"><path d="M13 8h39v48H13z" fill="#e5d2a5" stroke="#35271b" stroke-width="5"/><path d="M21 21h23M21 31h23M21 41h17" stroke="#806c4b" stroke-width="4"/></svg>'
}

def icon(name):
    return '<span class="icon">' + ICONS[name] + '</span>'

# Distinct monster silhouettes, not circles-with-eyes.
MONSTERS = {
    "rat": ("Giant Rat", 5, 14, 4, 15, "rat"),
    "spider": ("Cave Spider", 7, 17, 5, 18, "spider"),
    "goblin": ("Goblin", 8, 21, 8, 25, "goblin"),
    "zombie": ("Crypt Zombie", 10, 24, 10, 30, "zombie"),
    "bat": ("Vampire Bat", 6, 18, 7, 28, "bat"),
    "serpent": ("Venom Serpent", 9, 26, 12, 35, "serpent"),
    "specter": ("Lost Specter", 12, 29, 15, 40, "specter"),
    "scorpion": ("Cave Scorpion", 11, 27, 15, 42, "scorpion"),
    "troll": ("Stone Troll", 18, 34, 25, 60, "troll"),
    "dragon": ("Young Dragon", 25, 45, 50, 120, "dragon"),
}

MONSTER_SVG = {
"rat": '<svg viewBox="0 0 220 150"><path d="M45 103c-28 9-39 2-35-5 5-9 27-4 41-7" fill="none" stroke="#756b62" stroke-width="8" stroke-linecap="round"/><path d="M55 93c-9-39 20-61 61-53 34 7 50 32 31 57-18 24-71 24-92-4z" fill="#756b62" stroke="#292522" stroke-width="7"/><circle cx="82" cy="51" r="13" fill="#756b62" stroke="#292522" stroke-width="6"/><circle cx="119" cy="51" r="13" fill="#756b62" stroke="#292522" stroke-width="6"/><circle cx="136" cy="77" r="5" fill="#161616"/><path d="M149 82l18 4" stroke="#e5a5a5" stroke-width="5"/></svg>',
"spider": '<svg viewBox="0 0 220 150"><ellipse cx="110" cy="82" rx="34" ry="42" fill="#44384a" stroke="#1b1720" stroke-width="7"/><circle cx="110" cy="43" r="27" fill="#44384a" stroke="#1b1720" stroke-width="7"/><g fill="none" stroke="#44384a" stroke-width="9" stroke-linecap="round"><path d="M78 66L35 32M76 82L25 67M78 99L31 108M86 112L52 139M142 66l43-34M144 82l51-15M142 99l47 9M134 112l34 27"/></g><circle cx="101" cy="40" r="4" fill="#d44"/><circle cx="119" cy="40" r="4" fill="#d44"/></svg>',
"goblin": '<svg viewBox="0 0 220 150"><path d="M71 57L30 38l29 39M149 57l41-19-29 39" fill="#63844b" stroke="#26371f" stroke-width="7"/><path d="M70 116c-8-27-8-65 40-72 48 7 48 45 40 72-18 22-62 22-80 0z" fill="#63844b" stroke="#26371f" stroke-width="7"/><path d="M82 75h13M125 75h13" stroke="#171714" stroke-width="8"/><path d="M92 98h36" stroke="#d8c39d" stroke-width="6"/></svg>',
"zombie": '<svg viewBox="0 0 220 150"><path d="M70 128l-5-38c-3-28 13-50 45-52 32 2 48 24 45 52l-5 38" fill="#718874" stroke="#26362a" stroke-width="7"/><path d="M78 52l-10-20M142 52l12-21" stroke="#718874" stroke-width="15"/><circle cx="91" cy="67" r="7" fill="#20201c"/><circle cx="128" cy="67" r="7" fill="#20201c"/><path d="M91 94l12 7 9-8 10 7" fill="none" stroke="#20201c" stroke-width="6"/></svg>',
"bat": '<svg viewBox="0 0 220 150"><path d="M106 63C72 22 30 20 10 13c8 32 19 57 51 73-19 2-30 9-40 19 31 8 59 0 78-21 19 21 47 29 78 21-10-10-21-17-40-19 32-16 43-41 51-73-20 7-62 9-96 50z" fill="#443a50" stroke="#1e1824" stroke-width="7"/><path d="M110 56v57" stroke="#1e1824" stroke-width="6"/><circle cx="99" cy="61" r="4" fill="#d44"/><circle cx="121" cy="61" r="4" fill="#d44"/></svg>',
"serpent": '<svg viewBox="0 0 220 150"><path d="M28 117c35-52 71 35 105-10 24-31 45-25 59-45" fill="none" stroke="#567846" stroke-width="28" stroke-linecap="round"/><path d="M182 53l27-11-8 22" fill="#567846" stroke="#263a20" stroke-width="6"/><circle cx="191" cy="52" r="3" fill="#111"/></svg>',
"specter": '<svg viewBox="0 0 220 150"><path d="M55 130V64c0-45 110-45 110 0v66l-18-13-18 13-18-13-18 13-18-13z" fill="#aab9c5" stroke="#465563" stroke-width="7"/><circle cx="88" cy="69" r="8" fill="#29313a"/><circle cx="132" cy="69" r="8" fill="#29313a"/><path d="M91 96c13 10 25 10 38 0" fill="none" stroke="#465563" stroke-width="6"/></svg>',
"scorpion": '<svg viewBox="0 0 220 150"><ellipse cx="109" cy="88" rx="38" ry="28" fill="#795338" stroke="#342216" stroke-width="7"/><path d="M74 81L31 58 12 73M74 94L30 110 11 98M145 81l43-23 19 15M145 94l45 16 19-12" fill="none" stroke="#795338" stroke-width="12" stroke-linecap="round"/><path d="M144 78c57-39 65-4 38 24" fill="none" stroke="#795338" stroke-width="11"/><path d="M180 102l16 4-11 12" fill="#795338" stroke="#342216" stroke-width="5"/></svg>',
"troll": '<svg viewBox="0 0 220 150"><path d="M61 130c-8-28-8-86 49-99 57 13 57 71 49 99" fill="#5d6d58" stroke="#263224" stroke-width="8"/><path d="M72 52L37 35l25 38M148 52l35-17-25 38" fill="#5d6d58" stroke="#263224" stroke-width="8"/><circle cx="88" cy="71" r="8" fill="#20201b"/><circle cx="132" cy="71" r="8" fill="#20201b"/><path d="M82 103h56" stroke="#d2c19c" stroke-width="8"/></svg>',
"dragon": '<svg viewBox="0 0 220 150"><path d="M91 112c-34 27-62 18-78-3 22 5 39-3 52-25" fill="#8d4038" stroke="#381b19" stroke-width="7"/><path d="M77 89C39 71 19 42 8 18c34 4 66 15 91 42 25-27 57-38 91-42-11 24-31 53-69 71" fill="#71322f" stroke="#381b19" stroke-width="7"/><path d="M72 105c0-34 18-55 38-55s38 21 38 55c-17 25-59 25-76 0z" fill="#8d4038" stroke="#381b19" stroke-width="7"/><path d="M87 57l-8-20M133 57l8-20" stroke="#d0a14a" stroke-width="8"/><circle cx="94" cy="79" r="5" fill="#f1c44c"/><circle cx="126" cy="79" r="5" fill="#f1c44c"/></svg>'
}

def monster_art(kind):
    return MONSTER_SVG.get(kind, MONSTER_SVG["rat"])

def new_game():
    session.update(health=100, gold=10, room=1, potions=2)

def monster_event():
    names=list(MONSTERS)
    weights=[24,18,17,12,10,7,4,4,3,1]
    kind=random.choices(names,weights=weights)[0]
    name,lo,hi,glo,ghi,_=MONSTERS[kind]
    damage=random.randint(lo,hi); gold=random.randint(glo,ghi)
    session["health"]-=damage; session["gold"]+=gold
    return kind,name,damage,gold

PAGE="""
<!doctype html><html><head><title>Dungeon of Chaos</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#30251d,#090909 70%);color:#eee;font-family:Arial,sans-serif;padding:24px}.box{max-width:900px;margin:auto;padding:28px;border:2px solid #66533c;border-radius:20px;background:#151515;box-shadow:0 0 35px #000}h1{text-align:center;font-size:42px;margin:4px 0;text-shadow:0 0 12px #b78b4a}.subtitle{text-align:center;color:#aaa;margin-bottom:22px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.stat{background:#222;border:1px solid #555;border-radius:12px;padding:12px;text-align:center;font-weight:bold}.icon{width:34px;height:34px;display:inline-block;vertical-align:middle;margin-right:7px}.icon svg{width:100%;height:100%}.bar{height:9px;background:#333;border-radius:10px;margin-top:7px;overflow:hidden}.hp{height:100%;width:{{health}}%;background:#b33}.event{min-height:260px;margin:22px 0;padding:18px;border:1px solid #444;border-radius:15px;background:#202020;text-align:center}.monster-art{width:min(330px,80vw);height:190px;margin:auto}.monster-art svg{width:100%;height:100%}.monster-label{font-size:27px;font-weight:bold}.monster-sub{color:#999;font-size:14px}.message{font-size:20px;margin-top:8px}.buttons{display:flex;flex-wrap:wrap;justify-content:center}.action{min-width:145px;padding:13px 16px;margin:6px;border-radius:10px;border:1px solid #777;background:#292929;color:#fff;font-size:16px;cursor:pointer}.action:hover{transform:translateY(-2px);background:#444}.action .icon{width:25px;height:25px}.good:hover{background:#205d32}.danger:hover{background:#702020}.magic:hover{background:#50306d}.log{margin-top:20px;padding:13px;background:#101010;border-radius:10px;color:#aaa;font-size:14px}@media(max-width:650px){.stats{grid-template-columns:repeat(2,1fr)}h1{font-size:31px}}
</style></head><body><div class="box"><h1>DUNGEON OF CHAOS</h1><div class="subtitle">Every door is a terrible idea.</div><div class="stats"><div class="stat">{{health}} / 100<div class="bar"><div class="hp"></div></div></div><div class="stat">{{gold}} GOLD</div><div class="stat">ROOM {{room}}</div><div class="stat">{{potions}} POTIONS</div></div><div class="event">{% if monster %}<div class="monster-art">{{monster_svg|safe}}</div><div class="monster-label">{{monster_name}}</div><div class="monster-sub">A creature lurks in the darkness...</div>{% endif %}<div class="message">{{message|safe}}</div></div>{% if dead %}<h2 style="text-align:center">YOU DIED</h2><form action="/reset"><button class="action good">NEW ADVENTURE</button></form>{% elif won %}<h2 style="text-align:center">ADVENTURE COMPLETE!</h2><p style="text-align:center">You escaped with <b>{{gold}} gold</b>.</p><form action="/reset"><button class="action good">NEW ADVENTURE</button></form>{% else %}<div class="buttons"><form method="post"><button class="action" name="choice" value="door">{{door|safe}} EXPLORE</button></form><form method="post"><button class="action" name="choice" value="search">{{search|safe}} SEARCH</button></form><form method="post"><button class="action magic" name="choice" value="potion">{{potion|safe}} POTION</button></form><form method="post"><button class="action" name="choice" value="rest">{{rest|safe}} REST</button></form><form method="post"><button class="action danger" name="choice" value="run">{{run|safe}} ESCAPE</button></form></div>{% endif %}<div class="log">{{scroll|safe}} <b>DUNGEON TIP:</b> Search for supplies, save potions for emergencies, and don't trust suspiciously quiet rooms.</div></div></body></html>
"""

@app.route('/',methods=['GET','POST'])
def game():
    if 'health' not in session:new_game()
    message='Choose your next move...';dead=False;won=False;monster=None;monster_name='';monster_svg=''
    if request.method=='POST' and session['health']>0:
        choice=request.form.get('choice')
        if choice=='door':
            event=random.choices(['monster','treasure','trap','merchant','nothing','boss'],weights=[38,22,14,9,13,4])[0]
            if event=='monster':
                monster,monster_name,damage,reward=monster_event();message=f'You take {damage} damage but defeat it and find {reward} gold!'
            elif event=='treasure':
                found=random.randint(10,60);session['gold']+=found;message=f'{icon("chest")} <b>JACKPOT!</b><br>You found {found} gold!'
            elif event=='trap':
                damage=random.randint(5,20);session['health']-=damage;message=f'{icon("trap")} <b>FLOOR SPIKES!</b><br>You lose {damage} HP!'
            elif event=='merchant':
                if session['gold']>=15:session['gold']-=15;session['potions']+=1;message='A mysterious merchant sells you a potion for 15 gold.'
                else:message='A mysterious merchant sees your empty wallet and walks away.'
            elif event=='boss':
                monster='dragon';monster_name='Dungeon Guardian';damage=random.randint(15,35);reward=random.randint(50,120);session['health']-=damage;session['gold']+=reward;message=f'You take {damage} damage but grab {reward} gold!'
            else:message=random.choice(['The room is completely empty.','You hear footsteps... then realize they are your own.','Nothing happens. The dungeon is judging you.','A candle flickers by itself.'])
            session['room']+=1
            if session['room']>=21 and session['health']>0:won=True;message=f'<b>You reached the surface with {session["gold"]} gold!</b>'
        elif choice=='search':
            roll=random.randint(1,7)
            if roll==1:found=random.randint(15,45);session['gold']+=found;message=f'{icon("chest")} You find a hidden chest containing {found} gold!'
            elif roll==2:session['potions']+=1;message=f'{icon("potion")} You find a dusty potion behind a loose brick!'
            elif roll==3:damage=random.randint(2,8);session['health']-=damage;message=f'Hidden webs catch you! -{damage} HP.'
            elif roll==4:monster,monster_name,damage,reward=monster_event();message=f'It hits you for {damage} damage, but you recover {reward} gold.'
            else:message=random.choice(['You search everywhere. Nothing but suspicious dust.','You find a rusty coin worth 1 gold.','You discover a secret passage that leads back to the same room.']);session['gold']+=1 if 'coin' in message else 0
        elif choice=='potion':
            if session['potions']>0:session['potions']-=1;old=session['health'];session['health']=min(100,session['health']+random.randint(20,40));message=f'{icon("potion")} You recover {session["health"]-old} HP!'
            else:message='You reach for a potion... and remember you have ZERO.'
        elif choice=='rest':
            if random.randint(1,3)==1:damage=random.randint(5,15);session['health']-=damage;message=f'Something attacks you while you rest! -{damage} HP.'
            else:healing=random.randint(8,18);session['health']=min(100,session['health']+healing);message=f'You safely rest and recover {healing} HP.'
        elif choice=='run':won=True;message=f'You escape with {session["gold"]} gold. Cowardice successfully achieved!'
        if session['health']<=0:session['health']=0;dead=True;message='The dungeon has claimed another victim...'
    if monster:monster_svg=monster_art(monster)
    return render_template_string(PAGE,health=session['health'],gold=session['gold'],room=session['room'],potions=session['potions'],message=message,dead=dead,won=won,monster=monster,monster_name=monster_name,monster_svg=monster_svg,door=icon('room'),search=icon('search'),potion=icon('potion'),rest=icon('rest'),run=icon('run'),scroll=icon('scroll'))

@app.route('/reset')
def reset():new_game();return redirect('/')

if __name__=='__main__':app.run(host='0.0.0.0',port=5001)
