# app.py
"""
Heart Heist — robust multi-stage Streamlit app.
This version auto-creates default 'stages/' HTML files if they are missing,
so you won't get FileNotFoundError when running on a fresh container.
"""
import streamlit as st
from pathlib import Path
import datetime, textwrap, base64, json
import os

st.set_page_config(page_title="The Heart Heist — Sneha", page_icon="💘", layout="wide")

ROOT = Path(__file__).parent
STAGES_DIR = ROOT / "stages"

# -----------------------
# Default HTML templates (only written when files are missing)
# (These are simplified but fully functional versions of the stages)
# -----------------------
DEFAULT_VAULT = r"""<!doctype html>
<html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Vault — The Heart Heist</title>
<style>
:root{--accent:{{ACCENT}};--bg:#071024}
html,body{height:100%;margin:0;background:linear-gradient(180deg,var(--bg),#02101a);font-family:Inter,Arial;color:#fff;display:flex;align-items:center;justify-content:center}
.container{width:100%;max-width:960px;padding:28px;box-sizing:border-box;text-align:center}
.spot{width:320px;height:320px;margin:0 auto;border-radius:50%;background:radial-gradient(circle at 40% 30%, rgba(255,182,193,0.22), rgba(255,182,193,0.06));display:flex;align-items:center;justify-content:center}
.pad{width:160px;height:160px;border-radius:18px;background:linear-gradient(180deg,rgba(255,240,245,0.06),rgba(255,240,245,0.02));display:flex;align-items:center;justify-content:center;flex-direction:column}
.icon{font-size:56px;color:var(--accent)}
.title{margin-top:12px;font-weight:700;color:#ffd6e0}
.scanner{margin:18px auto 6px;width:260px;height:44px;border-radius:999px;background:rgba(255,255,255,0.02);position:relative;overflow:hidden;border:1px solid rgba(255,255,255,0.03);cursor:pointer}
.fill{position:absolute;left:0;top:0;bottom:0;width:0%;background:linear-gradient(90deg,var(--accent),#ffd6e0);height:100%;transition:width 0.06s linear}
.hint{position:relative;z-index:2;padding:10px;color:#fff;font-weight:700}
.log{height:44px;color:#dbeffd;margin-top:8px;min-height:40px}
.helper{margin-top:10px;color:#cfe8ff;opacity:0.9}
</style>
</head>
<body>
  <div class="container" role="main">
    <div class="spot"><div class="pad"><div class="icon">🔒</div><div style="font-size:13px;color:#fff;margin-top:6px">Access Restricted</div><div style="font-size:12px;color:#ffd6e0;margin-top:4px">Authorized Cuteness Only</div></div></div>
    <div class="scanner" id="scanner" title="Press & hold to scan"><div class="fill" id="fill"></div><div class="hint" id="hint">Press & hold to scan</div></div>
    <div class="log" id="log"></div>
    <div class="helper">Hold on the scanner for a second — it's a secret handshake.</div>
  </div>

<script>
const scanner = document.getElementById('scanner'), fill = document.getElementById('fill'), log = document.getElementById('log'), hint = document.getElementById('hint');
let holding=false, progress=0, timer=null;
function startHold(){ if(holding) return; holding=true; progress=0; fill.style.width='0%'; log.textContent='Analyzing smile...'; timer=setInterval(()=>{
  if(!holding) return; progress=Math.min(100, progress+3); fill.style.width = progress + '%';
  if(progress===30) log.textContent='Analyzing vibes... Immaculate.';
  if(progress===60) log.textContent='Analyzing smile... 100% Contagious.';
  if(progress===92) log.textContent='Match found: The girl of my dreams.';
  if(progress>=100){ clearInterval(timer); holding=false; onUnlock(); }
}, 50);}
function cancelHold(){ holding=false; clearInterval(timer); fill.style.width='0%'; log.textContent=''; hint.textContent='Press & hold to scan'; }
function onUnlock(){
  try{ new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=').play(); }catch(e){}
  document.body.style.transition='background 450ms'; document.body.style.background='linear-gradient(180deg,#ffd6e0,#fff0f4)';
  log.textContent = "Vault unlocked. Press 'I've finished this stage — Continue' in the main page.";
  hint.textContent = "Unlocked ✔";
  document.querySelector('.icon').textContent = '💗';
}
scanner.addEventListener('pointerdown',(e)=>{ e.preventDefault(); startHold(); });
scanner.addEventListener('pointerup',(e)=>{ cancelHold(); });
scanner.addEventListener('pointerleave',(e)=>{ cancelHold(); });
scanner.addEventListener('touchstart',(e)=>{ startHold(); }, {passive:true});
scanner.addEventListener('touchend',(e)=>{ cancelHold(); }, {passive:true});
</script>
</body></html>
"""

DEFAULT_PUZZLE = r"""<!doctype html>
<html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Poetry Puzzle</title>
<style>
:root{--accent:{{ACCENT}};--bg:#071024}
html,body{height:100%;margin:0;background:linear-gradient(180deg,var(--bg),#051022);font-family:Inter,Arial;color:#fff;display:flex;align-items:center;justify-content:center}
.wrap{width:100%;max-width:1000px;padding:22px}
.card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:14px;padding:18px;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
.words{display:flex;gap:10px;flex-wrap:wrap}
.word{padding:8px 12px;background:rgba(255,255,255,0.02);border-radius:10px;cursor:grab}
.notepad{width:320px;min-height:120px;border:2px dashed rgba(255,255,255,0.03);border-radius:10px;padding:12px;background:rgba(0,0,0,0.06)}
.continue button{padding:10px 14px;border-radius:12px;background:linear-gradient(90deg,var(--accent),#ffd6e0);border:none;color:#071024;font-weight:800}
.good{box-shadow:0 0 30px rgba(255,200,215,0.35)}
</style></head><body>
<div class="wrap">
  <div class="card">
    <div style="display:flex;justify-content:space-between"><div style="font-weight:800;color:#ffd6e0">Poetry Puzzle</div><div style="color:#cfe8ff">Drag or tap the words into the notepad</div></div>
    <div style="display:flex;gap:18px;margin-top:12px">
      <div class="words" id="wordsArea"></div>
      <div style="width:340px"><div class="notepad" id="notepad" ondragover="event.preventDefault()"></div><div class="continue" style="text-align:right;margin-top:12px"><button id="continueBtn" disabled>Continue</button></div></div>
    </div>
  </div>
</div>

<script>
const WORDS = {{POEM_WORDS_JSON}};
const wordsArea = document.getElementById('wordsArea'), notepad = document.getElementById('notepad'), continueBtn=document.getElementById('continueBtn');
function shuffle(a){ for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]] } return a }
let shuffled = shuffle([...WORDS]);
function render(){ wordsArea.innerHTML=''; shuffled.forEach(w=>{ const el=document.createElement('div'); el.className='word'; el.textContent=w; el.draggable=true;
    el.addEventListener('dragstart',e=>{ e.dataTransfer.setData('text/plain',w); el.classList.add('dragging')});
    el.addEventListener('dragend',()=>el.classList.remove('dragging'));
    el.addEventListener('click', ()=> placeToken(w, el));
    wordsArea.appendChild(el);
  })}
function placeToken(word, sourceEl){ const token=document.createElement('div'); token.className='word'; token.textContent=word; token.draggable=true; token.addEventListener('dragstart',e=>e.dataTransfer.setData('text/plain',word));
  try{ sourceEl.remove(); }catch(e){} notepad.appendChild(token); checkSolved(); }
notepad.addEventListener('dragover', e=>e.preventDefault());
notepad.addEventListener('drop', e=>{ e.preventDefault(); const w=e.dataTransfer.getData('text/plain'); if(!w) return; const children=Array.from(wordsArea.children); const found=children.find(c=>c.textContent===w); if(found) found.remove(); const token=document.createElement('div'); token.className='word'; token.textContent=w; token.draggable=true; token.addEventListener('dragstart',e=>e.dataTransfer.setData('text/plain',w)); notepad.appendChild(token); checkSolved();});
function checkSolved(){ const placed=Array.from(notepad.children).map(x=>x.textContent.trim()); const target=WORDS.map(s=>s.trim()); if(placed.length!==target.length){ continueBtn.disabled=true; notepad.classList.remove('good'); return; } let ok=true; for(let i=0;i<target.length;i++){ if(target[i]!==placed[i]){ ok=false; break } } if(ok){ notepad.classList.add('good'); continueBtn.disabled=false; } else { notepad.classList.remove('good'); continueBtn.disabled=true; } }
continueBtn.addEventListener('click', ()=> { continueBtn.textContent = "Good — now press Continue in the main page"; continueBtn.disabled = true; });
render();
</script>
</body></html>
"""

DEFAULT_RAIN = r"""<!doctype html>
<html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Compliment Rain</title>
<style>
:root{--accent:{{ACCENT}};--bg:#071024}
html,body{height:100%;margin:0;background:linear-gradient(180deg,#0d1a2b,#071024);font-family:Inter,Arial;color:#fff;overflow:hidden}
.stage{width:95vw;height:85vh;background:linear-gradient(180deg,#fff3fb06,transparent);border-radius:14px;padding:10px;position:relative;overflow:hidden;margin:auto}
.reason-list{position:absolute;top:12px;left:12px;background:rgba(7,16,36,0.6);padding:10px;border-radius:8px;max-width:260px}
.reason-list div{padding:6px 8px;border-radius:6px;background:rgba(255,255,255,0.02);margin-bottom:6px}
.character{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);width:120px;text-align:center;z-index:30}
.character img{width:120px;height:120px;border-radius:999px;border:6px solid rgba(255,255,255,0.04)}
.fall-item{position:absolute;font-size:26px;pointer-events:none}
.hint{position:absolute;right:12px;top:12px;color:#cfe8ff}
</style></head><body>
<div class="stage" id="stage">
  <div class="reason-list" id="reasons"><strong>Reasons I like you</strong></div>
  <div class="hint">Catch 5 stars to proceed</div>
  <div class="character" id="character"><img src="https://via.placeholder.com/300x300.png?text=Me" alt="Me"><div style="font-size:12px;margin-top:6px;color:#fff">Move me to catch stars</div></div>
</div>
<script>
const COMPLIMENTS = {{COMPLIMENTS_JSON}};
const stage = document.getElementById('stage'), character = document.getElementById('character'), reasons = document.getElementById('reasons');
let caught=0, pool=[], active=true, required=5;
function spawn(){ if(!active) return; const types=['💖','🌟','🌸','✨']; const t=types[Math.floor(Math.random()*types.length)]; const el=document.createElement('div'); el.className='fall-item'; el.textContent=t; el.style.left=(5+Math.random()*85)+'%'; el.style.top='-6%'; stage.appendChild(el); pool.push(el); const duration=3500+Math.random()*2500; const start=performance.now();
  function frame(now){ const p=(now-start)/duration; if(p>=1){ try{el.remove()}catch(e){} pool=pool.filter(x=>x!==el); return; } el.style.top=(p*100)+'%'; const ri=el.getBoundingClientRect(), rc=character.getBoundingClientRect(); const overlapX=(ri.left+ri.width/2)>rc.left && (ri.left+ri.width/2)<(rc.left+rc.width); const overlapY=(ri.top+ri.height/2)>rc.top && (ri.top+ri.height/2)<(rc.top+rc.height); if(overlapX && overlapY){ handleCatch(el.textContent); try{el.remove()}catch(e){} pool=pool.filter(x=>x!==el); return; } requestAnimationFrame(frame); } requestAnimationFrame(frame); setTimeout(spawn,600+Math.random()*600); }
function handleCatch(symbol){ if(symbol==='🌟'){ const node=document.createElement('div'); node.textContent=`Caught Star #${caught+1}: ${COMPLIMENTS[Math.min(caught,COMPLIMENTS.length-1)]}`; reasons.appendChild(node); caught+=1; if(caught>=required){ active=false; pool.forEach(x=>{try{x.remove()}catch(e){}}); const hint=document.createElement('div'); hint.textContent='Great! Press Continue in the main page.'; hint.style.marginTop='8px'; hint.style.color='#ffd6e0'; reasons.appendChild(hint); } } else { const node=document.createElement('div'); node.textContent=symbol; reasons.appendChild(node); if(reasons.children.length>8) reasons.removeChild(reasons.children[1]); } }
function moveChar(x){ const rect=stage.getBoundingClientRect(); const cx=Math.max(rect.left+20, Math.min(x, rect.right-20)); const pct=(cx-rect.left)/rect.width; character.style.left=(pct*100)+'%'; character.style.transform='translateX(-50%)'; }
document.addEventListener('pointermove', (e)=> moveChar(e.clientX)); document.addEventListener('touchmove', (e)=>{ if(e.touches && e.touches[0]) moveChar(e.touches[0].clientX); }, {passive:true});
spawn();
</script>
</body></html>
"""

DEFAULT_FINALE = r"""<!doctype html>
<html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Finale</title>
<style>
:root{--accent:{{ACCENT}};--bg:#071024}
html,body{height:100%;margin:0;background:linear-gradient(180deg,#071024,#02101a);font-family:Inter,Arial;color:#fff;display:flex;align-items:center;justify-content:center}
.wrap{width:100%;max-width:900px;padding:18px;text-align:center}
.envelope{width:420px;height:260px;border-radius:12px;background:linear-gradient(180deg,#ffdfe6,#ffd6e0);display:flex;align-items:center;justify-content:center;position:relative;cursor:pointer;box-shadow:0 30px 80px rgba(0,0,0,0.6)}
.card{position:absolute;top:100%;left:50%;transform:translate(-50%,0);width:360px;height:200px;background:white;border-radius:10px;padding:18px;color:#071024;display:flex;flex-direction:column;justify-content:center;align-items:center;transition:top 500ms}
.card.show{top:18%}
.bigq{font-weight:800;margin-top:8px;color:var(--accent);display:none}
.btns{display:flex;gap:14px;margin-top:12px}
.yes{padding:12px 20px;border-radius:12px;background:linear-gradient(90deg,#ff6b8a,#ffb2c6);color:#071024;border:none;font-weight:800;cursor:pointer}
.no{padding:8px 12px;border-radius:10px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);cursor:pointer}
.ticket{position:fixed;bottom:-160px;left:50%;transform:translateX(-50%);width:560px;background:linear-gradient(90deg,#ffffff,#ffd6e0);border-radius:12px;padding:18px;color:#071024;box-shadow:0 40px 120px rgba(0,0,0,0.6);transition:bottom 700ms}
.ticket.show{bottom:30px}
</style></head><body>
<div class="wrap">
  <div class="envelope" id="envelope">
    <div style="font-size:32px">💌</div>
    <div style="position:absolute;bottom:8px;right:10px;color:#071024;font-size:12px">Tap to open</div>
    <div class="card" id="cardInside">
      <div style="font-family:'Brush Script MT',cursive;font-size:20px;color:#333">I have a very important question...</div>
      <div class="bigq" id="bigq">Will you be my Valentine?</div>
      <div class="btns" id="btns" style="display:none">
        <button class="yes" id="yes">YES! Absolutely! ❤️</button>
        <button class="no" id="no">No.</button>
      </div>
    </div>
  </div>
</div>
<div class="ticket" id="ticket"><div style="display:flex;justify-content:space-between;align-items:center">
  <div><div style="font-weight:900">ADMIT ONE</div><div style="font-size:20px;font-weight:800;margin-top:6px">Valentine Date Night</div><div style="margin-top:6px">With: <strong>{{RECIPIENT}}</strong></div><div style="margin-top:6px">When: <strong>{{DATE_HUMAN}}</strong></div></div>
  <div style="text-align:right"><div style="font-size:12px;color:#555">Dress code</div><div style="font-weight:700;margin-top:6px">Lookin' gorgeous as always</div></div>
</div><div style="margin-top:12px;display:flex;gap:12px;justify-content:flex-end"><a id="downloadIcs" href="{{ICS_URI}}" download="valentine_{{RECIPIENT}}.ics" style="padding:8px 12px;border-radius:8px;background:rgba(7,16,36,0.85);color:#fff;text-decoration:none">Save to Calendar</a></div></div>

<script>
const envelope=document.getElementById('envelope'), card=document.getElementById('cardInside'), bigq=document.getElementById('bigq'), btns=document.getElementById('btns'), yes=document.getElementById('yes'), no=document.getElementById('no'), ticket=document.getElementById('ticket');
envelope.addEventListener('click', ()=>{ card.classList.add('show'); setTimeout(()=>{ bigq.style.display='block'; setTimeout(()=>{ btns.style.display='flex'; },400); },430); });
let dodge=0, dodging=false;
function dodgeNo(e){ if(dodging) return; dodging=true; dodge++; const env=envelope.getBoundingClientRect(); const x=Math.random()*(env.width-80)+env.left+window.scrollX; const y=Math.random()*(env.height-40)+env.top+window.scrollY; no.style.position='absolute'; no.style.left=(x-env.left)+'px'; no.style.top=(y-env.top)+'px'; setTimeout(()=>{ dodging=false; },220); if(dodge>=4){ no.textContent='YES!'; no.className='yes'; no.onclick=accept; } }
no.addEventListener('mouseenter', dodgeNo); no.addEventListener('touchstart', dodgeNo);
function accept(){ try{ const c=document.createElement('canvas'); document.body.appendChild(c); const confettiScript=document.createElement('script'); confettiScript.src='https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js'; confettiScript.onload=()=>{ window.confetti({ particleCount: 120, spread: 160, origin: { x: 0.5, y: 0.2 } }); }; document.head.appendChild(confettiScript); }catch(e){} ticket.classList.add('show'); }
yes.addEventListener('click', accept);
</script>
</body></html>
"""

# -----------------------
# Utility: Ensure stages directory & files exist (create defaults only when missing)
# -----------------------
def ensure_stage_files():
    STAGES_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    files = {
        "vault.html": DEFAULT_VAULT,
        "puzzle.html": DEFAULT_PUZZLE,
        "rain.html": DEFAULT_RAIN,
        "finale.html": DEFAULT_FINALE,
    }
    for name, content in files.items():
        path = STAGES_DIR / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(str(path.name))
    return created

# create missing stage templates (safe; does not overwrite existing files)
created_files = ensure_stage_files()
if created_files:
    st.info(f"Created missing stage templates: {', '.join(created_files)} (you can edit them in `stages/`).")
else:
    st.write("Meow")

# -----------------------
# Helpers used by app
# -----------------------
def load_stage_template(name: str) -> str:
    path = STAGES_DIR / f"{name}.html"
    if not path.exists():
        raise FileNotFoundError(f"Stage template not found: {path}")
    return path.read_text(encoding="utf-8")

def inject(template: str, mapping: dict) -> str:
    html = template
    for k, v in mapping.items():
        html = html.replace(k, v)
    return html

def make_ics_data_uri(title, description, dtstart, duration_minutes=120, location="To Be Announced"):
    dtend = dtstart + datetime.timedelta(minutes=duration_minutes)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    dtstamp = now_utc.strftime("%Y%m%dT%H%M%SZ")
    uid = f"heartheist-{int(now_utc.timestamp())}@meow"
    ics = textwrap.dedent(f"""\
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//HeartHeist//EN
    BEGIN:VEVENT
    UID:{uid}
    DTSTAMP:{dtstamp}
    DTSTART:{dtstart.strftime('%Y%m%dT%H%M00')}
    DTEND:{dtend.strftime('%Y%m%dT%H%M00')}
    SUMMARY:{title}
    LOCATION:{location}
    DESCRIPTION:{description}
    END:VEVENT
    END:VCALENDAR
    """)
    b64 = base64.b64encode(ics.encode("utf-8")).decode("utf-8")
    return f"data:text/calendar;base64,{b64}", ics

# -----------------------
# UI Inputs & Stage Flow
# -----------------------
st.title("Meow")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    sender = st.text_input("Sender name", value="Parth")
with col2:
    recipient = st.text_input("Recipient name", value="Sneha")
with col3:
    date_choice = st.date_input("Proposed date", value=datetime.date(datetime.datetime.now().year, 2, 14))
st.markdown("---")
st.markdown("Hand your phone to the recipient when you're ready. Do the actions in the frame, then click 'I've finished this stage — Continue' below.")

stages = ["vault", "puzzle", "rain", "finale"]
if "stage_idx" not in st.session_state:
    st.session_state.stage_idx = 0

cola, colb, colc = st.columns([1,1,1])
with cola:
    if st.button("Restart mission"):
        st.session_state.stage_idx = 0
        st.rerun()
with colb:
    st.markdown(f"**Current stage:** {st.session_state.stage_idx+1} / {len(stages)} — **{stages[st.session_state.stage_idx].upper()}**")
with colc:
    if st.button("Jump to finale"):
        st.session_state.stage_idx = len(stages)-1
        st.rerun()

# prepare data to inject
poem_line = "In a world of noise, you are my favourite melody."
poem_words = poem_line.split()
compliments = [
    "Your laugh",
    "The way you listen",
    "Your kind heart",
    "Your style",
    "How you make time for people",
    "Your curiosity",
    "That grin at 2 AM"
]
poem_words_json = json.dumps(poem_words)
compliments_json = json.dumps(compliments)
AUDIO_URL = "https://cdn.simplecast.com/audio/6a2bbd/lofi-chill-beats.mp3"
dtstart = datetime.datetime.combine(date_choice, datetime.time(hour=19, minute=0))
ics_data_uri, ics_text = make_ics_data_uri(f"Valentine Date Night with {recipient}", f"Valentine Date Night with {recipient} — sent by {sender}.", dtstart)

# load current stage
curr_stage = stages[st.session_state.stage_idx]
try:
    template = load_stage_template(curr_stage)
except FileNotFoundError as e:
    st.error(f"Stage template not found: {e}. I attempted to create defaults; check `stages/`.")
    raise

mapping = {
    "{{SENDER}}": sender,
    "{{RECIPIENT}}": recipient,
    "{{ACCENT}}": accent,
    "{{AUDIO_URL}}": AUDIO_URL,
    "{{POEM_WORDS_JSON}}": poem_words_json,
    "{{COMPLIMENTS_JSON}}": compliments_json,
    "{{ICS_URI}}": ics_data_uri,
    "{{DATE_HUMAN}}": dtstart.strftime("%A, %B %d, %Y at %I:%M %p"),
}

html = inject(template, mapping)

st.components.v1.html(html, height=720, scrolling=True)

st.markdown("---")
col_done, col_skip = st.columns([2,1])
with col_done:
    if st.button("I've finished this stage — Continue"):
        if st.session_state.stage_idx < len(stages)-1:
            st.session_state.stage_idx += 1
            st.rerun()
        else:
            st.success("Mission complete — you reached the finale.")
with col_skip:
    if st.button("Skip this stage"):
        if st.session_state.stage_idx < len(stages)-1:
            st.session_state.stage_idx += 1
            st.rerun()

# finale downloads
if st.session_state.stage_idx == len(stages)-1:
    st.markdown("---")
    st.write("Final assets:")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download final HTML (stage)", data=html.encode("utf-8"), file_name=f"heart_heist_{recipient}.html", mime="text/html")
    with c2:
        st.download_button("Download .ics calendar file", data=ics_text.encode("utf-8"), file_name=f"valentine_{recipient}.ics", mime="text/calendar")
    st.markdown("No photo uploads are enabled. Edit templates in `stages/` if you want to customize visuals.")
