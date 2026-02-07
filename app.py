# app.py
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import hashlib
import random
import html
import base64

st.set_page_config(
    page_title="Will you be my Valentine? ♥",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --------------------------
# Styles & helper functions
# --------------------------
CSS = """
<style>
:root{
  --bg1: linear-gradient(120deg,#ff9a9e 0%, #fad0c4 50%, #fad0c4 100%);
  --accent: #ff4b6e;
  --glass: rgba(255,255,255,0.06);
}
[data-testid="stAppViewContainer"]{
  background: radial-gradient(circle at 10% 10%, rgba(255,200,230,0.06), transparent 10%),
              radial-gradient(circle at 90% 90%, rgba(255,150,180,0.04), transparent 10%),
              linear-gradient(120deg,#0f172a, #0b1220 60%);
  color: #f8fafc;
  min-height: 100vh;
}
/* custom card */
.valentine-card{
  border-radius: 18px;
  padding: 20px;
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  box-shadow: 0 6px 30px rgba(0,0,0,0.6);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.03);
}
.big-heart {
  font-size: 90px;
  line-height: 0.8;
  transform: rotate(-10deg);
  filter: drop-shadow(0 6px 18px rgba(255,80,130,0.18));
}
.small-note {
  font-size: 16px;
  color: #f1f5f9;
  opacity: 0.9;
}
.btn-pulse {
  background: linear-gradient(90deg,#ff6b8a,#ffb2c6);
  color: #071024;
  border: none;
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}
.heart-anim {
  position: relative;
  height: 90px;
}
.heart-anim:before,
.heart-anim:after {
  content: "❤";
  position: absolute;
  font-size: 28px;
  opacity: 0.15;
  animation: float 3s ease-in-out infinite;
}
.heart-anim:before { left: 10%; top: 20%;}
.heart-anim:after { left: 75%; top: 40%; animation-delay: 1.2s;}
@keyframes float {
  0% { transform: translateY(0) scale(0.9); opacity:0.12;}
  50% { transform: translateY(-12px) scale(1.05); opacity:0.25;}
  100% { transform: translateY(0) scale(0.9); opacity:0.12;}
}
</style>
"""

def load_image_from_url(url, fallback_color=(250,200,210)):
    try:
        resp = requests.get(url, timeout=6)
        img = Image.open(BytesIO(resp.content)).convert("RGBA")
        return img
    except Exception:
        # return a small blank image
        img = Image.new("RGBA", (800, 400), fallback_color)
        return img

def name_compatibility(a: str, b: str) -> int:
    """Simple deterministic compatibility from two names (0-100)."""
    seed = (a.strip().lower() + "::" + b.strip().lower())
    s = hashlib.sha256(seed.encode()).hexdigest()
    # take first 6 hex digits -> int
    val = int(s[:6], 16)
    return (val % 101)  # 0..100

def make_card_html(sender, recipient, message, bg_url, accent="#ff4b6e"):
    safe_sender = html.escape(sender or "Someone")
    safe_recipient = html.escape(recipient or "You")
    safe_message = html.escape(message or "Will you be my Valentine?")
    escaped_bg = html.escape(bg_url) if bg_url else ""
    html_template = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>💌 A card for {safe_recipient}</title>
        <meta name="viewport" content="width=device-width,initial-scale=1"/>
        <style>
          body {{
            margin:0;
            height:100vh;
            display:flex;
            align-items:center;
            justify-content:center;
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial;
            background: radial-gradient(circle at 10% 20%, rgba(255,200,220,0.07), transparent 10%),
                        linear-gradient(120deg,#020617 0%, #071024 100%);
            color: #f8fafc;
          }}
          .card {{
            width: min(820px, 92%);
            border-radius: 20px;
            padding: 32px;
            background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,255,255,0.04);
            overflow: hidden;
            position: relative;
          }}
          .hero {{
            display:flex;
            gap:20px;
            align-items:center;
          }}
          .hero-img {{
            flex: 0 0 180px;
            height: 180px;
            border-radius:14px;
            background: url('{escaped_bg}') center/cover no-repeat;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
          }}
          .hero-text h1 {{ margin:0; font-size: 32px; color:{accent};}}
          .hero-text p {{ margin:6px 0 0 0; color: #e6eef8; opacity:0.95; }}
          .message {{
            margin-top: 22px;
            font-size:18px;
            line-height:1.45;
            color:#f8fafc;
            background: rgba(255,255,255,0.01);
            padding: 18px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.02);
          }}
          .footer { margin-top:16px; display:flex; justify-content:space-between; align-items:center; color:#bcd7ff; opacity:0.9; }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="hero">
            <div class="hero-img"></div>
            <div class="hero-text">
              <h1>To {safe_recipient},</h1>
              <p>From {safe_sender} — <small>with a fluttering heart</small></p>
            </div>
          </div>
          <div class="message">{safe_message}</div>
          <div class="footer">
            <div>💌 Save this and share it — made with a shy algorithm</div>
            <div>♥ {safe_sender}</div>
          </div>
        </div>
      </body>
    </html>
    """
    return html_template

def html_to_download_bytes(html_str: str):
    return html_str.encode("utf-8")

# --------------------------
# Page layout
# --------------------------
st.markdown(CSS, unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='valentine-card'>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex;align-items:center;gap:16px'>", unsafe_allow_html=True)
        st.markdown("<div class='big-heart'>💘</div>", unsafe_allow_html=True)
        st.markdown("<div><h1 style='margin:0'>Will you be my Valentine?</h1><div class='small-note'>A tiny interactive card maker for bold confessions</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='heart-anim'></div>", unsafe_allow_html=True)

st.markdown("---")

# Sidebar controls
st.sidebar.header("Quick actions")
bg_choice = st.sidebar.selectbox("Choose background", ("Dreamy roses", "Sunset pink", "Soft bokeh", "Custom URL"), index=0)
if bg_choice == "Dreamy roses":
    bg_url = "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?q=80&w=1600&auto=format&fit=crop&ixlib=rb-4.0.3&s=2a5b3e74e4f9b2f7b2b4e2b1b7d2dd6b"
elif bg_choice == "Sunset pink":
    bg_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1600&auto=format&fit=crop&ixlib=rb-4.0.3&s=8f3f2b3d4d2f1f6e5a8b7c7d8e9f0a0b"
elif bg_choice == "Soft bokeh":
    bg_url = "https://images.unsplash.com/photo-1509482560494-4126f3f52c9d?q=80&w=1600&auto=format&fit=crop&ixlib=rb-4.0.3&s=3d88b7a0c9a8b6d1c2e3f4a5b6c7d8e9"
else:
    bg_url = st.sidebar.text_input("Enter image URL (png/jpg):", "")

# Main interactive area
st.header("Design a tiny card")
with st.form("card_form"):
    colA, colB = st.columns(2)
    with colA:
        sender = st.text_input("Your name", value="—")
        recipient = st.text_input("Recipient's name", value="Beloved")
        message = st.text_area("Message (what you want to say)", value="I've been thinking of you. Will you be my Valentine?")
    with colB:
        accent = st.color_picker("Accent color", "#ff4b6e")
        show_border = st.checkbox("Add delicate border", value=True)
        add_signature = st.checkbox("Add signature line", value=True)
    submitted = st.form_submit_button("Generate & preview")

if submitted:
    st.success("Card generated — preview below. You can download as a standalone HTML e-card.")
    card_html = make_card_html(sender, recipient, message, bg_url, accent)
    # preview via components
    st.markdown(card_html, unsafe_allow_html=True)
    st.download_button("Download e-card (HTML)", data=html_to_download_bytes(card_html), file_name=f"valentine_for_{recipient}.html", mime="text/html")
else:
    st.info("Fill the form and press *Generate & preview* to see your card.")

st.markdown("---")

# Confession generator
st.header("Confession studio — the little helpers")
st.write("Use a starter line and tweak. If you're shy, let the generator help.")

starter = st.text_input("Write one line hint (optional)", "")
num_variations = st.slider("How many variations?", 1, 6, 3)
if st.button("Generate confessions"):
    base = starter.strip() or "I've had a crush on you for a while"
    variations = []
    for i in range(num_variations):
        tone = random.choice(["poetic", "playful", "serious", "cheeky", "dreamy"])
        ending = random.choice([
            "— would you like to go out with me?",
            "— can I take you for coffee this weekend?",
            "— will you be my valentine?",
            "— my heart is loud; will you listen?"
        ])
        variations.append(f"{base}, {ending} ({tone})")
    for v in variations:
        st.write("•", v)
    # download all
    all_text = "\n".join(variations)
    st.download_button("Download variations (.txt)", data=all_text, file_name="confessions.txt", mime="text/plain")

st.markdown("---")

# Compatibility meter
st.header("Compatibility meter (silly but deterministic)")
c1, c2 = st.columns([2, 2])
with c1:
    a = st.text_input("Name A", value="You")
with c2:
    b = st.text_input("Name B", value="Me")
if st.button("Check compatibility"):
    score = name_compatibility(a, b)
    st.markdown(f"### ❤️ Compatibility: **{score}%**")
    if score > 80:
        st.balloons()
        st.success("Wow. The algorithm is blushing. Definitely ask them out.")
    elif score > 50:
        st.info("Good vibes. A little courage and a coffee.")
    else:
        st.warning("This is purely playful. Real chemistry doesn't fit into integers.")
    # small shareable note
    st.write(f"Tip: Download a card for {b} and send it!")

st.markdown("---")

# Gallery / Extra pages
st.header("Gallery & inspiration")
gallery_urls = [
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1520975924905-5583f6e2c3e4?q=80&w=1200&auto=format&fit=crop"
]
cols = st.columns(3)
for idx, u in enumerate(gallery_urls):
    try:
        cols[idx].image(u, use_column_width=True, caption=f"Inspiration {idx+1}")
    except Exception:
        cols[idx].write("Image failed to load.")

st.markdown("---")
st.caption("Built with a slightly dramatic heart and a hint of code. If this app makes you too bold, blame the randomness seed.")

# Footer tiny credits
st.markdown(
    """
    <div style="font-size:12px;color:rgba(255,255,255,0.6);margin-top:18px">
      Tip: To deploy on Streamlit Cloud, add this repo and set `app.py` as the main file. See README for more.
    </div>
    """, unsafe_allow_html=True
)
