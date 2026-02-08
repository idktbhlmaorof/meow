# app.py
# The Heart Heist — interactive "Will you be my Valentine?" experience
# Single-file Streamlit app that embeds a full HTML/JS interactive experience.
#
# Requirements:
#   pip install streamlit pillow
#
# Usage:
#   streamlit run app.py
#
# Notes:
#  - The heavy-lifting interactive experience is implemented in an embedded HTML/JS blob.
#  - We use string.Template to avoid f-string brace-escaping issues.
#  - The audio is started after the initial user gesture (the "scan") so modern browsers allow sound.
#  - An .ics calendar file is generated server-side and embedded into the HTML as a base64 data URI
#    so the "Save to Calendar" button downloads the event to the user's device.
#
# Author: small, slightly dramatic algorithm
# (Edit poem, compliments, and date/time values below as you like.)

import streamlit as st
from string import Template
from PIL import Image
import io
import base64
import datetime
import textwrap

st.set_page_config(
    page_title="The Heart Heist — Sneha",
    page_icon="💘",
    layout="wide",
)

# -----------------------
# Helper utilities
# -----------------------
def image_file_to_data_uri(file) -> str:
    """Return data URI (base64) for an uploaded PIL image or file-like object."""
    if file is None:
        return ""
    # If file is an UploadedFile (streamlit), read bytes
    try:
        raw = file.read()
    except Exception:
        # If it's already bytes
        raw = file
    b64 = base64.b64encode(raw).decode("utf-8")
    # attempt to detect image type from file name
    mime = "image/png"
    if hasattr(file, "name") and file.name.lower().endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    return f"data:{mime};base64,{b64}"

def pil_image_to_data_uri(img: Image.Image) -> str:
    """Convert PIL image to PNG data URI."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def make_ics_data_uri(
    title="Valentine Date Night",
    description="Valentine Date Night — an evening together.",
    dtstart=None,
    duration_minutes=120,
    location="To Be Announced",
):
    """Generate a simple .ics file and return as data URI (base64)."""
    if dtstart is None:
        # default to next Feb 14 at 19:00 local (use 2026 if current year >)
        year = datetime.datetime.now().year
        # if today's date past Feb 14 this year, use next year
        feb14 = datetime.datetime(year=year, month=2, day=14)
        if datetime.datetime.now() > feb14:
            year += 1
        dtstart = datetime.datetime(year=year, month=2, day=14, hour=19, minute=0)
    dtend = dtstart + datetime.timedelta(minutes=duration_minutes)
    dtstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"heartheist-{int(datetime.datetime.utcnow().timestamp())}@meow"
    # Use floating times (no TZ) to keep it simple for phone calendar imports.
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
# Small UI to collect inputs (sender/recipient/images/customizations)
# -----------------------
st.markdown(
    """
    <div style="font-family:Georgia,serif;color:#ffd6e0;font-size:28px;margin-bottom:6px">
      The Heart Heist — a playful secret for someone special
    </div>
    <div style="color:#cfe8ff;margin-bottom:18px">Theme: soft pink & red, treasure-hunt aesthetic. Hand the phone to Sneha :)</div>
    """,
    unsafe_allow_html=True,
)

cols = st.columns([1, 1, 1, 1])
with cols[0]:
    sender = st.text_input("Your name (sender)", value="Parth")
with cols[1]:
    recipient = st.text_input("Recipient's name", value="Sneha")
with cols[2]:
    # let user pick accent color
    accent_color = st.color_picker("Accent color", value="#ff6b8a")
with cols[3]:
    # date for ticket
    date_choice = st.date_input("Date for the ticket", value=datetime.date(datetime.datetime.now().year, 2, 14))

st.markdown("---")
st.markdown("### Optional: Upload two photos to appear in the finale (left = you, right = her)")
img_cols = st.columns(2)
with img_cols[0]:
    up_you = st.file_uploader("Your photo (optional)", type=["png", "jpg", "jpeg"], key="you")
with img_cols[1]:
    up_her = st.file_uploader("Her photo (optional)", type=["png", "jpg", "jpeg"], key="her")

# create data URIs (if missing, placeholders from web)
you_uri = image_file_to_data_uri(up_you) or "https://via.placeholder.com/300x300.png?text=You"
her_uri = image_file_to_data_uri(up_her) or "https://via.placeholder.com/300x300.png?text=Sneha"

# generate ICS for chosen date at 19:00
dtstart = datetime.datetime.combine(date_choice, datetime.time(hour=19, minute=0))
ics_data_uri, ics_text = make_ics_data_uri(
    title=f"Valentine Date Night with {recipient}",
    description=f"Valentine Date Night with {recipient} — sent by {sender}.",
    dtstart=dtstart,
    duration_minutes=120,
    location="To Be Announced",
)

st.markdown("---")
st.markdown(
    """
    <div style="padding:12px;border-radius:10px;background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005));border:1px solid rgba(255,255,255,0.03)">
      When Sneha opens this page, she will interact with a playful "vault" that unlocks the question.
      Press the big button below to open the experience in a wide embedded view. Hand her the device and ask her to press and hold the scanner.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# The interactive HTML/JS experience (Template)
# -----------------------
# Poem pieces (you can edit)
poem_line = "In a world of noise, you are my favourite melody."
# We'll break into words for a drag-and-drop puzzle
poem_words = poem_line.split()
# compliments list
compliments = [
    "Your laugh",
    "The way you listen",
    "Your kind heart",
    "Your style",
    "How you make time for people",
    "Your curiosity",
    "That grin at 2 AM"
]
# Keep only a few compliments (first 8 or so)
compliments = compliments[:7]

# The embedded audio (we'll use a small lo-fi mp3 hosted online). It will start after user gesture.
# You can replace this with a different mp3 link or upload functionality if needed.
AUDIO_URL = "https://cdn.simplecast.com/audio/6a2bbd/lofi-chill-beats.mp3"  # placeholder: may be blocked in some deployments
# If autoplay is blocked, the script starts audio after the click-hold completes.

html_template = Template(r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>The Heart Heist — For $recipient</title>
  <style>
    :root{
      --bg-dark: #071024;
      --soft-pink: $accent;
      --card: rgba(255,255,255,0.02);
      --glass: rgba(255,255,255,0.03);
    }
    html,body{height:100%;margin:0;background:linear-gradient(180deg,var(--bg-dark),#02101a);font-family:Inter, -apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial;color:#fff;overflow:hidden}
    .center{display:flex;align-items:center;justify-content:center;height:100vh;width:100vw}
    /* Landing: Locked Vault */
    .vault-stage{display:flex;flex-direction:column;align-items:center;gap:18px}
    .spotlight{width:320px;height:320px;border-radius:50%;background:radial-gradient(circle at 40% 30%, rgba(255,182,193,0.22), rgba(255,182,193,0.06)),linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.0));display:flex;align-items:center;justify-content:center;box-shadow:0 30px 80px rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.02)}
    .padlock{width:160px;height:160px;border-radius:20%;background:linear-gradient(180deg, rgba(255,200,215,0.08), rgba(255,200,215,0.03));display:flex;align-items:center;justify-content:center;flex-direction:column;backdrop-filter: blur(2px);position:relative}
    .heart-icon{font-size:64px; color:var(--soft-pink); filter: drop-shadow(0 10px 30px rgba(255,80,130,0.12));}
    .lock-text{margin-top:8px;color:#f8f8ff;opacity:0.95}
    .scanner{margin-top:12px;width:220px;height:36px;border-radius:999px;background:linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;border:1px solid rgba(255,255,255,0.03);cursor:pointer}
    .scan-fill{position:absolute;left:0;top:0;bottom:0;width:0%;background:linear-gradient(90deg, rgba(255,107,138,0.9), rgba(255,179,198,0.6));height:100%;transition:width 0.05s linear}
    .scan-hint{position:relative;z-index:2;color:#fff;font-weight:600;font-size:14px}
    .analyze-log{margin-top:12px;min-height:36px;color:#dbeffd;opacity:0.95;font-size:13px;text-align:center}
    /* The inner stages will be absolutely positioned and faded in */
    .stage-wrapper{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none}
    .stage{width:100%;height:100%;display:flex;align-items:center;justify-content:center;pointer-events:auto;opacity:0;transform:scale(0.98);transition:opacity 600ms ease, transform 600ms ease}
    .stage.show{opacity:1;transform:scale(1)}
    /* Level 1: Poetry Puzzle */
    .puzzle-area{width:min(900px,92%);height:min(520px,88%);background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:18px;padding:22px;box-shadow:0 30px 100px rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.03);display:flex;flex-direction:column;gap:12px}
    .notepad{flex:0 0 160px;background:rgba(255,255,255,0.01);border-radius:10px;padding:12px;border:1px dashed rgba(255,255,255,0.03);min-height:80px}
    .words{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
    .word{padding:8px 12px;background:rgba(255,255,255,0.02);border-radius:10px;border:1px solid rgba(255,255,255,0.03);cursor:grab;user-select:none}
    .word.dragging{opacity:0.8;transform:scale(1.03)}
    .notebook-center{display:flex;gap:18px;align-items:center;justify-content:center;flex:1}
    .continue-btn{align-self:flex-end;padding:10px 14px;border-radius:12px;background:linear-gradient(90deg, #ffd6e0, var(--soft-pink));color:#071024;font-weight:700;border:none;cursor:pointer;display:none}
    .continue-btn.show{display:inline-block}
    /* Level 2: Compliment Rain */
    .rain-stage{width:90vw;height:80vh;position:relative;background:linear-gradient(180deg,#fceffc22,transparent);border-radius:14px;overflow:hidden}
    .character{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);width:120px;text-align:center}
    .character img{width:120px;height:120px;border-radius:999px;border:6px solid rgba(255,255,255,0.04);box-shadow:0 20px 60px rgba(0,0,0,0.5)}
    .umbrella{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);width:160px;height:90px;border-radius:12px}
    .fall-item{position:absolute;font-size:22px;pointer-events:none}
    .reason-list{position:absolute;top:14px;left:14px;background:rgba(7,16,36,0.6);padding:10px;border-radius:8px;max-width:260px}
    .reason-list div{padding:6px 8px;border-radius:6px;background:rgba(255,255,255,0.02);margin-bottom:6px;color:#fff}
    /* Finale: Envelope */
    .finale{display:flex;flex-direction:column;align-items:center;gap:10px}
    .envelope{width:420px;height:260px;border-radius:12px;background:linear-gradient(180deg,#ffdfe6, #ffd6e0);display:flex;align-items:center;justify-content:center;position:relative;box-shadow:0 30px 80px rgba(0,0,0,0.6);cursor:pointer;overflow:hidden}
    .card-inside{position:absolute;top:100%;left:50%;transform:translate(-50%,0);width:360px;height:200px;background:white;border-radius:10px;padding:18px;color:#071024;display:flex;flex-direction:column;justify-content:center;align-items:center;box-shadow:0 30px 80px rgba(0,0,0,0.25);transition:top 550ms cubic-bezier(.2,.9,.2,1)}
    .card-inside.show{top:20%}
    .btns{display:flex;gap:18px;margin-top:12px;align-items:center}
    .yes-btn{padding:14px 24px;border-radius:14px;background:linear-gradient(90deg,#ff6b8a,#ffb2c6);color:#071024;font-weight:800;border:none;font-size:18px;cursor:pointer;box-shadow:0 12px 30px rgba(255,70,120,0.12)}
    .no-btn{padding:10px 14px;border-radius:10px;background:rgba(255,255,255,0.02);color:#cfe8ff;border:1px solid rgba(255,255,255,0.03);cursor:pointer;position:relative}
    .ticket{position:fixed;bottom:-160px;left:50%;transform:translateX(-50%);width:560px;background:linear-gradient(90deg,#ffffff,#ffd6e0);border-radius:12px;padding:18px;color:#071024;box-shadow:0 40px 120px rgba(0,0,0,0.6);transition:bottom 700ms ease}
    .ticket.show{bottom:30px}
    .confetti-canvas{position:fixed;left:0;top:0;right:0;bottom:0;pointer-events:none;z-index:9999}
    /* helper */
    .hidden{display:none}
    @media (max-width:720px){
      .spotlight{width:260px;height:260px}
      .padlock{width:140px;height:140px}
      .envelope{width:320px;height:200px}
      .card-inside{width:280px}
      .ticket{width:92%}
    }
  </style>
</head>
<body>
  <div id="app" class="center">
    <!-- Landing Vault -->
    <div id="vault" class="vault-stage">
      <div class="spotlight">
        <div class="padlock" aria-hidden="true">
          <div class="heart-icon">🔒</div>
          <div class="lock-text">Access Restricted:<br/><strong>Authorized Cuteness Only</strong></div>
        </div>
      </div>

      <div class="scanner" id="scanner" title="Press & hold to scan">
        <div class="scan-fill" id="scanFill"></div>
        <div class="scan-hint" id="scanHint">Press and hold to scan fingerprint</div>
      </div>

      <div class="analyze-log" id="analyzeLog"> </div>
    </div>

    <!-- Stage wrapper: all inner stages -->
    <div class="stage-wrapper">
      <!-- Level 1: Poetry Puzzle -->
      <div id="puzzleStage" class="stage">
        <div class="puzzle-area" role="application" aria-label="Poetry puzzle">
          <div style="display:flex;align-items:center;justify-content:space-between">
            <div style="font-weight:700;color:#ffd6e0">Poetry Puzzle — piece together the line</div>
            <div style="color:#cfe8ff">Drag the drifting words into the notepad</div>
          </div>

          <div style="display:flex;gap:18px;align-items:flex-start;margin-top:12px;flex:1">
            <div style="flex:1">
              <div id="driftWords" class="words" aria-live="polite"></div>
            </div>
            <div style="width:320px;display:flex;flex-direction:column;gap:10px;align-items:center">
              <div class="notepad" id="notepad" ondragover="event.preventDefault()"></div>
              <button id="continuePuzzle" class="continue-btn">✈ Continue</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Level 2: Compliment Rain -->
      <div id="rainStage" class="stage">
        <div class="rain-stage" id="rainStageInner">
          <div class="reason-list" id="reasonList"><strong>Reasons I like you</strong></div>
          <div class="character" id="character">
            <img src="$you_uri" alt="you"/>
            <div style="font-size:12px;margin-top:6px;color:#fff;opacity:0.9">Move me to catch stars</div>
          </div>
        </div>
      </div>

      <!-- Finale: Envelope + Question -->
      <div id="finaleStage" class="stage">
        <div class="finale">
          <div class="envelope" id="envelope">
            <div style="font-weight:700;color:#071024">💌</div>
            <div style="position:absolute;bottom:10px;right:12px;color:#071024;font-size:12px;opacity:0.9">Tap to open</div>
            <div class="card-inside" id="cardInside">
              <div style="font-family: 'Brush Script MT', 'Segoe Script', cursive;font-size:22px;color:#333">I have a very important question...</div>
              <div id="bigQuestion" style="font-size:22px;font-weight:800;margin-top:6px;color:#ff6b8a;display:none">Will you be my Valentine?</div>
              <div class="btns" id="finalBtns" style="display:none">
                <button class="yes-btn" id="yesBtn">YES! Absolutely! ❤️</button>
                <button class="no-btn" id="noBtn">No.</button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Ticket (hidden until acceptance) -->
    <div class="ticket" id="ticket">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div style="font-weight:900">ADMIT ONE</div>
          <div style="font-size:20px;font-weight:800;margin-top:6px">Valentine Date Night</div>
          <div style="margin-top:6px">With: <strong>$recipient</strong></div>
          <div style="margin-top:6px">When: <strong>$date_human</strong></div>
        </div>
        <div style="text-align:right">
          <div style="font-size:12px;color:#555">Dress code</div>
          <div style="font-weight:700;margin-top:6px">Lookin' gorgeous as always</div>
        </div>
      </div>
      <div style="margin-top:12px;display:flex;gap:12px;justify-content:flex-end">
        <a id="downloadIcs" href="$ics_uri" download="valentine_$recipient.ics" style="padding:8px 12px;border-radius:8px;background:rgba(7,16,36,0.85);color:#fff;text-decoration:none">Save to Calendar</a>
        <button id="sharePhotos" style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff6b8a,#ffb2c6);border:none;color:#071024;font-weight:700">Share photos</button>
      </div>
    </div>

    <canvas class="confetti-canvas" id="confCanvas"></canvas>
  </div>

  <!-- audio element (will be started after scan completes) -->
  <audio id="bgAudio" src="$audio_url" preload="auto" loop></audio>

  <!-- external libraries -->
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>

  <script>
    /***** small helpers *****/
    const $ = (id)=>document.getElementById(id);
    const sleep = (ms)=>new Promise(r=>setTimeout(r, ms));

    /***** Stage management *****/
    const vault = $('vault');
    const scanFill = $('scanFill');
    const scanHint = $('scanHint');
    const analyzeLog = $('analyzeLog');

    const stagePuzzle = $('puzzleStage');
    const stageRain = $('rainStage');
    const stageFinale = $('finaleStage');

    const continuePuzzleBtn = $('continuePuzzle');
    const notepad = $('notepad');
    const driftWords = $('driftWords');

    const rainStageInner = $('rainStageInner');
    const reasonList = $('reasonList');
    const character = $('character');

    const envelope = $('envelope');
    const cardInside = $('cardInside');
    const bigQuestion = $('bigQuestion');
    const finalBtns = $('finalBtns');
    const yesBtn = $('yesBtn');
    const noBtn = $('noBtn');

    const ticket = $('ticket');
    const confCanvas = $('confCanvas');

    // fill the drifting words (shuffled)
    const poemWords = $poem_words; // injected list
    function shuffle(a){ for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]] } return a }
    let shuffled = shuffle([...poemWords]);
    function renderWords(){
      driftWords.innerHTML = '';
      shuffled.forEach((w, idx)=>{
        const span = document.createElement('div');
        span.className='word';
        span.draggable=true;
        span.textContent = w;
        span.dataset.index = idx;
        // drag events
        span.addEventListener('dragstart', (e)=>{
          e.dataTransfer.setData('text/plain', w);
          span.classList.add('dragging');
        });
        span.addEventListener('dragend', ()=>span.classList.remove('dragging'));
        // also allow click-to-place on touch
        span.addEventListener('click', ()=>{
          placeWord(w, span);
        });
        driftWords.appendChild(span);
      })
    }
    function placeWord(word, element){
      // create token in notepad
      const token = document.createElement('div');
      token.className='word';
      token.textContent = word;
      token.draggable = true;
      token.addEventListener('dragstart', (e)=>{ e.dataTransfer.setData('text/plain', word) });
      // remove original
      try{ element.remove() }catch(e){}
      notepad.appendChild(token);
      checkPoemSolved();
    }

    notepad.addEventListener('dragover', (e)=>e.preventDefault());
    notepad.addEventListener('drop', (e)=>{
      e.preventDefault();
      const w = e.dataTransfer.getData('text/plain');
      if(!w) return;
      // find and remove from driftWords
      const children = Array.from(driftWords.children);
      const found = children.find(c => c.textContent === w);
      if(found) found.remove();
      // append to notepad
      const token = document.createElement('div');
      token.className='word';
      token.textContent = w;
      token.draggable = true;
      token.addEventListener('dragstart', (e)=>{ e.dataTransfer.setData('text/plain', w) });
      notepad.appendChild(token);
      checkPoemSolved();
    });

    function checkPoemSolved(){
      // poem target = original poemWords order
      const placed = Array.from(notepad.children).map(x=>x.textContent.trim());
      const target = poemWords.map(s=>s.trim());
      if(placed.length === target.length){
        // compare sequences
        let ok = true;
        for(let i=0;i<target.length;i++){
          if(target[i] !== placed[i]){ ok=false; break }
        }
        if(ok){
          // glow and reveal continue
          notepad.style.boxShadow = '0 0 30px rgba(255,200,215,0.45)';
          continuePuzzleBtn.classList.add('show');
        } else {
          notepad.style.boxShadow = '';
          continuePuzzleBtn.classList.remove('show');
        }
      } else {
        notepad.style.boxShadow = '';
        continuePuzzleBtn.classList.remove('show');
      }
    }

    // puzzle continue -> move to rain stage
    continuePuzzleBtn.addEventListener('click', ()=>{
      // animate puzzle out, show rain stage
      stagePuzzle.classList.remove('show');
      setTimeout(()=>{ stageRain.classList.add('show'); startRain(); }, 520);
    });

    /***** Scan (press & hold) logic *****/
    const scanner = $('scanner');
    let holdTimer = null;
    let progress = 0;
    let holding = false;
    const audio = document.getElementById('bgAudio');
    let audioStarted = false;

    scanner.addEventListener('pointerdown', (e)=>{
      e.preventDefault();
      holding = true;
      scanHint.textContent = 'Scanning...';
      progress = 0;
      scanFill.style.width = '0%';
      analyzeLog.textContent = 'Analyzing smile...';
      holdTimer = setInterval(()=>{
        if(!holding) return;
        progress = Math.min(100, progress + 2);
        scanFill.style.width = progress + '%';
        // intermittent messages
        if(progress === 30) analyzeLog.textContent = 'Analyzing vibes... Immaculate.';
        if(progress === 60) analyzeLog.textContent = 'Analyzing smile... 100% Contagious.';
        if(progress === 92) analyzeLog.textContent = 'Match found: The girl of my dreams.';
        if(progress >= 100){
          clearInterval(holdTimer);
          holding = false;
          // open vault
          openVault();
        }
      }, 40);
    });
    document.addEventListener('pointerup', (e)=>{ holding = false; clearInterval(holdTimer); if(progress < 100){ scanHint.textContent = 'Press and hold to scan fingerprint'; scanFill.style.width = '0%'; analyzeLog.textContent = '' }});

    async function openVault(){
      // small click sound (synth)
      try{ new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=').play() }catch(e){}
      // animate heart lock -> open and show puzzle
      document.querySelector('.padlock .heart-icon').textContent = '💗';
      await sleep(450);
      // show puzzle
      vault.style.display = 'none';
      // start audio (user gesture done)
      try{ if(!audioStarted){ audio.play().catch(()=>{}); audioStarted=true } }catch(e){}
      // reveal puzzle stage
      stagePuzzle.classList.add('show');
      // render words
      renderWords();
    }

    /***** Rain stage: falling items and catching *****/
    const fallPool = [];
    let caughtStars = 0;
    const requiredStars = 5;
    let rainActive = false;
    function startRain(){
      rainActive = true;
      // spawn items periodically
      spawnLoop();
      // track pointer to move character
      document.addEventListener('pointermove', pointerMove);
      // for touch on mobile, also use touchmove
      document.addEventListener('touchmove', pointerMove);
    }
    function pointerMove(e){
      let clientX = (e.touches && e.touches[0]) ? e.touches[0].clientX : e.clientX;
      // set character center to clientX within stage bounds
      const rect = rainStageInner.getBoundingClientRect();
      let x = Math.max(rect.left + 20, Math.min(clientX, rect.right - 20));
      const pct = (x - rect.left) / rect.width;
      character.style.left = (pct*100) + '%';
      character.style.transform = 'translateX(-50%)';
    }
    function spawnLoop(){
      if(!rainActive) return;
      spawnItem();
      setTimeout(spawnLoop, 700 + Math.random()*400);
    }
    function spawnItem(){
      const types = ['💖','🌟','🌸','✨'];
      const type = types[Math.floor(Math.random()*types.length)];
      const el = document.createElement('div');
      el.className='fall-item';
      el.textContent = type;
      el.style.left = (5 + Math.random()*90) + '%';
      el.style.top = '-8%';
      el.dataset.type = type;
      rainStageInner.appendChild(el);
      fallPool.push(el);
      // animate falling
      const speed = 4 + Math.random()*3; // seconds
      const start = performance.now();
      function frame(now){
        const t = (now - start) / (speed*1000);
        if(t >= 1){
          // reached bottom -> remove
          try{ el.remove() }catch(e){}
          const idx = fallPool.indexOf(el);
          if(idx>=0) fallPool.splice(idx,1);
          return;
        }
        // compute position
        el.style.top = (t*100) + '%';
        // check collision with character (simple)
        const rectItem = el.getBoundingClientRect();
        const rectChar = character.getBoundingClientRect();
        const overlapX = (rectItem.left + rectItem.width/2) > rectChar.left && (rectItem.left + rectItem.width/2) < (rectChar.left + rectChar.width);
        const overlapY = (rectItem.top + rectItem.height/2) > rectChar.top && (rectItem.top + rectItem.height/2) < (rectChar.top + rectChar.height);
        if(overlapX && overlapY){
          // caught
          handleCatch(el.dataset.type);
          try{ el.remove() }catch(e){}
          const idx = fallPool.indexOf(el);
          if(idx>=0) fallPool.splice(idx,1);
          return;
        }
        requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
    function handleCatch(type){
      if(type === '🌟'){
        // show reason
        const idx = Math.min(caughtStars, $compliments.length - 1);
        const reason = $compliments[idx] || "You brightened my day";
        const node = document.createElement('div'); node.textContent = `Caught Star #${caughtStars+1}: ${reason}`;
        reasonList.appendChild(node);
        caughtStars += 1;
        if(caughtStars >= requiredStars){
          // clear rain and proceed to finale
          rainActive = false;
          // remove falling elements
          fallPool.forEach(x=>{ try{x.remove()}catch(e){} });
          stageRain.classList.remove('show');
          setTimeout(()=>{ stageFinale.classList.add('show'); }, 600);
        }
      } else {
        // other items simply show a tiny sparkle
        const node = document.createElement('div'); node.textContent = `${type}`;
        node.style.opacity = 0.9; node.style.fontSize='18px';
        reasonList.appendChild(node);
        // prune after some items
        if(reasonList.children.length > 7) reasonList.removeChild(reasonList.children[1]);
      }
    }

    /***** Finale: envelope and buttons *****/
    envelope.addEventListener('click', ()=>{
      cardInside.classList.add('show');
      setTimeout(()=>{ document.querySelector('#cardInside div:nth-child(1)').style.opacity = 0.3; bigQuestion.style.display='block'; setTimeout(()=>{ finalBtns.style.display='flex'; }, 500); }, 550);
    });

    // No button dodge & eventual conversion
    let dodgeCount = 0;
    let dodging = false;
    function dodgeNoButton(e){
      if(dodging) return;
      dodging = true;
      dodgeCount++;
      // move to random location within envelope area
      const envRect = envelope.getBoundingClientRect();
      const nx = Math.random() * (envRect.width - 80) + envRect.left + window.scrollX;
      const ny = Math.random() * (envRect.height - 40) + envRect.top + window.scrollY;
      noBtn.style.position = 'absolute';
      noBtn.style.left = (nx - envRect.left) + 'px';
      noBtn.style.top = (ny - envRect.top) + 'px';
      setTimeout(()=>{ dodging=false; }, 220);
      // after a few dodges, transform into YES
      if(dodgeCount >= 5){
        // convert to yes
        noBtn.textContent = 'YES!';
        noBtn.className = 'yes-btn';
        noBtn.onclick = acceptYes;
      }
    }
    noBtn.addEventListener('mouseenter', dodgeNoButton);
    noBtn.addEventListener('touchstart', dodgeNoButton);

    // if she clicks Yes
    function acceptYes(){
      // confetti and show ticket
      const myConfetti = confetti.create(confCanvas, {resize:true, useWorker:true});
      myConfetti({particleCount: 80, spread: 140, origin:{x:0.5, y:0.2}});
      setTimeout(()=> myConfetti({particleCount: 200, spread: 220, origin:{x:0.5, y:0.1}}), 300);
      ticket.classList.add('show');
      // reveal photos in ticket/share if available
      // sharePhotos button could open a download of an image or trigger anything.
    }
    yesBtn.addEventListener('click', acceptYes);

    // share photos: simple animation to show images (uses inlined URIs)
    $('sharePhotos').addEventListener('click', ()=>{
      const popup = document.createElement('div');
      popup.style.position='fixed'; popup.style.left='50%'; popup.style.top='50%'; popup.style.transform='translate(-50%,-50%)'; popup.style.padding='12px';
      popup.style.background='linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))'; popup.style.border='1px solid rgba(255,255,255,0.03)'; popup.style.borderRadius='10px';
      const i1 = document.createElement('img'); i1.src = '$you_uri'; i1.style.width='140px'; i1.style.height='140px'; i1.style.borderRadius='10px'; i1.style.marginRight='8px';
      const i2 = document.createElement('img'); i2.src = '$her_uri'; i2.style.width='140px'; i2.style.height='140px'; i2.style.borderRadius='10px';
      popup.appendChild(i1); popup.appendChild(i2);
      const close = document.createElement('button'); close.textContent='Close'; close.style.display='block'; close.style.marginTop='10px';
      close.onclick = ()=>popup.remove();
      popup.appendChild(close);
      document.body.appendChild(popup);
    });

    // small confetti helper
    const confetti = window.confetti || null;

    /***** Initialization: inject poem words and compliments (from Python) *****/
    (function init(){
      // inject poemWords array into JS variable space already done by templating
      // show initial stage (vault only)
      document.querySelectorAll('.stage').forEach(s=>s.classList.remove('show'));
      vault.style.display = 'flex';
      // make sure wrapper stages hidden
      stagePuzzle.classList.remove('show');
      stageRain.classList.remove('show');
      stageFinale.classList.remove('show');
      // when puzzle solved, show continue -> handled elsewhere
    })();

    /***** For direct testing, expose some globals to window *****/
    window._HEIST = {
      renderWords,
      acceptYes,
      startRain
    };
  </script>
</body>
</html>
""")

# Prepare variables to substitute in template
# Escape JS arrays: poem words as a JS array literal; compliments as JS array literal
def js_array_literal(py_list):
    safe = [str(x).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"') for x in py_list]
    items = ",".join([f"'{s}'" for s in safe])
    return f"[{items}]"

substitutions = {
    "recipient": recipient.replace('"', "'"),
    "accent": accent_color,
    "you_uri": you_uri,
    "her_uri": her_uri,
    "audio_url": AUDIO_URL,
    "poem_words": js_array_literal(poem_words),
    "compliments": js_array_literal(compliments),
    "ics_uri": ics_data_uri,
    "date_human": dtstart.strftime("%A, %B %d, %Y at %I:%M %p"),
    # embed small arrays for JS consumption
    "$poem_words": js_array_literal(poem_words),  # used in template as literal constant
    "$compliments": js_array_literal(compliments),
}

# NOTE: Template substitution uses $var names. Our template expects $recipient, $accent, etc.
# But also contains JS variables like $poem_words; ensure we pass them in as keys without the $.
# Python's Template will replace $recipient with value of substitutions['recipient'].
# Create a mapping that Template.substitute accepts (keys without $).
mapping = {
    "recipient": substitutions["recipient"],
    "accent": substitutions["accent"],
    "you_uri": substitutions["you_uri"],
    "her_uri": substitutions["her_uri"],
    "audio_url": substitutions["audio_url"],
    "ics_uri": substitutions["ics_uri"],
    "date_human": substitutions["date_human"],
    # embed raw JS arrays into the HTML by replacing placeholder tokens after substitution:
    # We will substitute $poem_words_text and $compliments_text markers and then replace them in final HTML.
    "poem_words": substitutions["poem_words"],
    "compliments": substitutions["compliments"],
}

# Perform substitution
html = html_template.substitute(mapping)

# Our template used tokens $poem_words and $compliments inside JS, but to avoid accidental Template
# parsing conflicts we included them in the mapping. If any $... remained, substitute direct string replacement:
html = html.replace("$poem_words", substitutions["poem_words"])
html = html.replace("$compliments", substitutions["compliments"])

# Finally embed the JS variables for poem words and compliments by defining them early in the script:
# The template already referenced a JS variable $poem_words; we will ensure it's defined by injecting a small line.
# (Above replacements should have created them as literal arrays in place.)

# -----------------------
# Render the embedded experience
# -----------------------
# Recommend a tall height for the embedded component
st.components.v1.html(html, height=780, scrolling=True)

# Also provide direct download of a standalone .html file (optional)
st.markdown("---")
st.markdown("**Extras:**")
col1, col2 = st.columns([1, 1])
with col1:
    st.download_button(
        "Download standalone experience (HTML)",
        data=html.encode("utf-8"),
        file_name=f"heart_heist_for_{recipient.replace(' ','_')}.html",
        mime="text/html",
    )
with col2:
    st.download_button(
        "Download .ics calendar file (for your phone)",
        data=ics_text.encode("utf-8"),
        file_name=f"valentine_{recipient.replace(' ','_')}.ics",
        mime="text/calendar",
    )

st.markdown(
    """
    <div style="margin-top:8px;color:#cfe8ff;font-size:13px">
      Tip: Ask her to open this on your phone and press & hold the scanner. Browsers often require a user gesture to play sound;
      the hold gesture will start the background music and make the experience fully immersive.
    </div>
    """,
    unsafe_allow_html=True,
)
