# app.py
import streamlit as st
from PIL import Image
import io
import base64
import textwrap
import datetime
from string import Template

st.set_page_config(page_title="Sneha — Will you be my Valentine?", page_icon="💘", layout="centered")

# -------------------------
# Styles
# -------------------------
PAGE_CSS = """
<style>
body { background: linear-gradient(180deg,#0b1220 0%, #071024 100%); color: #f2f7fb; }
.big-title { font-family: Georgia, 'Times New Roman', serif; font-size: 34px; color: #ffd6e0; margin-bottom: 6px; }
.subtitle { color: #cfe8ff; opacity: 0.9; margin-bottom: 18px; }
.story { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:18px; border-radius:14px; border:1px solid rgba(255,255,255,0.03); box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
.upload-col { background: rgba(255,255,255,0.01); padding:14px; border-radius:12px; }
.btn-yes { background: linear-gradient(90deg,#ff6b8a,#ffb2c6); color: #071024; border-radius: 12px; padding: 10px 18px; font-weight:700; border:none; }
.btn-no { background: rgba(255,255,255,0.03); color:#f8fafc; border-radius:10px; padding:8px 14px; border:1px solid rgba(255,255,255,0.04); }
.small { color:#c9dbff; opacity:0.9; font-size:13px; }
.footer { color:#9fbfff; opacity:0.7; font-size:12px; margin-top:18px; }
</style>
"""

st.markdown(PAGE_CSS, unsafe_allow_html=True)

# -------------------------
# Helper functions
# -------------------------
def image_to_b64(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    return "data:image/png;base64," + b64

def make_animation_html(b64_a, b64_b, poem_body, sender_name, recipient_name):
    """
    Uses string.Template to avoid f-string brace escaping issues.
    """
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    tpl = Template("""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>For $recipient_name</title>
<style>
  html,body{height:100%;margin:0;background:linear-gradient(180deg,#071024,#02101a);font-family:Georgia,serif;color:#fff;}
  .stage{height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:18px;padding:28px;box-sizing:border-box}
  .card{width:min(900px,96%);background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:18px;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,0.6);position:relative;overflow:hidden;border:1px solid rgba(255,255,255,0.03)}
  .headline{font-size:28px;color:#ffd6e0;margin:0 0 6px 0}
  .poem{color:#e6f3ff;opacity:0.95;line-height:1.45;margin-bottom:18px;font-size:16px}
  .portrait-row{display:flex;gap:20px;align-items:center;justify-content:center}
  .portrait{width:150px;height:150px;border-radius:50%;overflow:hidden;border:6px solid rgba(255,255,255,0.04);box-shadow:0 12px 30px rgba(0,0,0,0.6);transform-origin:center;}
  .portrait img{width:100%;height:100%;object-fit:cover;display:block}
  .merge{transform:translateX(0) scale(1);transition:transform 900ms cubic-bezier(.2,.9,.2,1);}
  .left{transform:translateX(-220px);}
  .right{transform:translateX(220px);}
  .centered-left{transform:translateX(-60px) scale(1.05); transition:transform 900ms cubic-bezier(.2,.9,.2,1);}
  .centered-right{transform:translateX(60px) scale(1.05); transition:transform 900ms cubic-bezier(.2,.9,.2,1);}
  .heart{position:absolute;left:50%;top:16%;transform:translateX(-50%);font-size:64px;opacity:0;transition:opacity 800ms ease, transform 900ms cubic-bezier(.2,.9,.2,1)}
  .heart.show{opacity:1; transform:translateX(-50%) scale(1.06); filter: drop-shadow(0 12px 28px rgba(255,80,130,0.18));}
  .meta{display:flex;justify-content:space-between;align-items:center;margin-top:14px;color:#cfe8ff;opacity:0.95;font-size:13px}
  /* floating hearts */
  .floating{position:absolute;inset:0;pointer-events:none}
  .floating span{position:absolute;font-size:20px;opacity:0.12;animation:float 4s linear infinite}
  @keyframes float{0%{transform:translateY(0) translateX(0) scale(0.9);opacity:0.12}50%{transform:translateY(-60px) translateX(10px) scale(1.05);opacity:0.28}100%{transform:translateY(0) translateX(-20px) scale(0.9);opacity:0.12}}
  /* confetti canvas full-screen */
  canvas.confetti{position:fixed;left:0;top:0;right:0;bottom:0;pointer-events:none;z-index:9999}
  @media (max-width:640px){
    .portrait{width:120px;height:120px}
    .portrait-row{gap:12px}
  }
</style>
</head>
<body>
<div class="stage">
  <div class="card" id="card">
    <div class="headline">For $recipient_name — a tiny story</div>
    <div class="poem">$poem_body</div>

    <div class="portrait-row" id="portraits">
      <div class="portrait left" id="p1"><img src="$b64_a" alt="you"></div>
      <div class="portrait right" id="p2"><img src="$b64_b" alt="sneha"></div>
    </div>

    <div class="meta">
      <div>Made by $sender_name</div>
      <div>$date_str</div>
    </div>

    <div class="heart" id="bigHeart">💞</div>
    <div class="floating" id="floaters">
      <span style="left:8%;top:72%">❤</span>
      <span style="left:22%;top:28%">❤</span>
      <span style="left:72%;top:62%">❤</span>
      <span style="left:86%;top:32%">❤</span>
      <span style="left:48%;top:84%">❤</span>
    </div>
  </div>
</div>

<canvas class="confetti" id="c"></canvas>

<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
<script>
  const p1 = document.getElementById('p1');
  const p2 = document.getElementById('p2');
  const heart = document.getElementById('bigHeart');
  const canvas = document.getElementById('c');
  const confetti = window.confetti.create(canvas, { resize: true, useWorker: true });

  function celebrate() {
    // move portraits closer
    p1.classList.remove('left'); p2.classList.remove('right');
    p1.classList.add('centered-left'); p2.classList.add('centered-right');
    heart.classList.add('show');

    // confetti bursts
    confetti({ particleCount: 40, spread: 60, origin: { x:0.5, y:0.2 } });
    setTimeout(() => confetti({ particleCount: 80, spread: 120, origin: { x:0.5, y:0.1 } }), 400);
    setTimeout(()=> confetti({ particleCount: 120, spread: 160, origin: { x:0.5, y:0.0 } }), 800);
  }

  // wait a beat then celebrate (animation triggered by streamlit when embedding)
  setTimeout(celebrate, 300);
</script>
</body>
</html>""")
    html = tpl.substitute(
        b64_a=b64_a,
        b64_b=b64_b,
        poem_body=poem_body,
        sender_name=sender_name,
        recipient_name=recipient_name,
        date_str=date_str
    )
    return html

def make_downloadable_html_bytes(html_str: str) -> bytes:
    return html_str.encode("utf-8")

# -------------------------
# Page content
# -------------------------
st.markdown(f"<div class='big-title'>Sneha — will you be my valentine?</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>A little story, a small question, and an animation that waits for her answer.</div>", unsafe_allow_html=True)

# Story (poetic + short)
story = textwrap.dedent("""
    There are days when the world loosens its seams:
    the ordinary frays into tiny, luminous moments —
    morning tea that tastes like a memory, a message that feels like a hand,
    and the way your name arrives in my thoughts like an unexpected song.

    Today, I'm brave enough to fold these small moments into a single question.
    """).strip()

st.markdown(f"<div class='story'><em>{story}</em></div>", unsafe_allow_html=True)
st.markdown("<br/>")

# Uploads and inputs
st.markdown("### Prepare the moment")
cols = st.columns([1,1,1])
with cols[0]:
    st.markdown("<div class='upload-col'>Your name</div>", unsafe_allow_html=True)
    sender = st.text_input("Your name (sender)", value="Parth")
with cols[1]:
    st.markdown("<div class='upload-col'>Recipient</div>", unsafe_allow_html=True)
    recipient = st.text_input("Recipient's name", value="Sneha")
with cols[2]:
    st.markdown("<div class='upload-col'>Accent</div>", unsafe_allow_html=True)
    accent = st.color_picker("Accent color (for e-card)", value="#ff6b8a")

st.markdown("<hr/>", unsafe_allow_html=True)

st.markdown("### Upload portraits (optional — or use the placeholders)")
u1, u2 = st.columns(2)
with u1:
    img1 = st.file_uploader("Your photo (square / face)", type=["png","jpg","jpeg"], key="you")
with u2:
    img2 = st.file_uploader("Sneha's photo (recommended)", type=["png","jpg","jpeg"], key="sneha")

# optional custom message / poem
st.markdown("### A short line you want shown when she says *Yes* (poetic recommended)")
line = st.text_input("One-liner (optional)", value="If you say yes, I promise to make you laugh at least three times a week.")

# show preview of portraits
pr_cols = st.columns(2)
with pr_cols[0]:
    st.markdown("**Preview — you**")
    if img1:
        imgA = Image.open(img1).convert("RGBA")
        st.image(imgA, width=220)
    else:
        st.image("https://via.placeholder.com/300x300.png?text=Your+photo", width=220)
with pr_cols[1]:
    st.markdown("**Preview — Sneha**")
    if img2:
        imgB = Image.open(img2).convert("RGBA")
        st.image(imgB, width=220)
    else:
        st.image("https://via.placeholder.com/300x300.png?text=Sneha", width=220)

st.markdown("---")

# The interactive asking area
st.markdown("### Ask her, gently")
st.markdown("Hand your device to her, or send the HTML that opens the animation when she clicks **Yes**. (If she taps **Yes**, the celebration will play.)")
ask_cols = st.columns([1,1,1])
with ask_cols[0]:
    if st.button("Yes — show animation", key="btn_yes"):
        # prepare images (use placeholders if missing)
        if img1:
            A = Image.open(img1).convert("RGBA")
        else:
            A = Image.open(io.BytesIO(base64.b64decode(
                b'iVBORw0KGgoAAAANSUhEUgAAAUAAAABACAYAAABV+Y2sAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QgRBxEmzKXvXgAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAABmElEQVR42u3RAQ0AAAgDINc/9K3hHBgggAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMD8AnwABeZzGywAAAABJRU5ErkJggg=='
            )))
        if img2:
            B = Image.open(img2).convert("RGBA")
        else:
            B = Image.open(io.BytesIO(base64.b64decode(
                b'iVBORw0KGgoAAAANSUhEUgAAAUAAAABACAYAAABV+Y2sAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QgRBxEmzKXvXgAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAABmElEQVR42u3RAQ0AAAgDINc/9K3hHBgggAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMD8AnwABeZzGywAAAABJRU5ErkJggg=='
            )))
        b64a = image_to_b64(A)
        b64b = image_to_b64(B)
        poem = textwrap.fill(f"{line}\n\n— {sender}", width=60)
        html = make_animation_html(b64a, b64b, poem, sender, recipient)
        # Show the animation as an embedded HTML
        st.components.v1.html(html, height=700, scrolling=True)
        # Provide downloadable html
        st.download_button("Download standalone e-card (HTML)", data=make_downloadable_html_bytes(html),
                           file_name=f"for_{recipient.replace(' ','_')}_valentine.html", mime="text/html")
with ask_cols[1]:
    if st.button("Maybe — show a gentle nudge", key="btn_maybe"):
        st.success("A gentle nudge appears on screen: “No pressure — coffee?”")
        st.balloons()
with ask_cols[2]:
    if st.button("No — soft reply", key="btn_no"):
        st.warning("Took the risk. Respect the honesty. Gentle message shown.")
        st.info("Tip: If she says no, you can still say: 'Thanks for hearing me out.' Grow from this. Be human.")

st.markdown("---")
st.markdown("<div class='small'>Pro tip: Hand her your phone/device — the animation is best experienced up close. If you want, I can make the animation autoplay full-screen or include sound.</div>", unsafe_allow_html=True)
st.markdown("<div class='footer'>If you want the app turned into a single-file GitHub Pages HTML or a tiny Flask site, say so and I’ll give the exact files.</div>", unsafe_allow_html=True)
