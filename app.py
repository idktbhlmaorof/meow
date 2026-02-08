# app.py
"""
The Heart Heist — multi-stage Streamlit app
Structure:
- app.py
- requirements.txt
- stages/
    - vault.html
    - puzzle.html
    - rain.html
    - finale.html

Run:
  pip install -r requirements.txt
  streamlit run app.py
"""

import streamlit as st
import datetime
import textwrap
import base64
import json
from pathlib import Path

ROOT = Path(__file__).parent
STAGES_DIR = ROOT / "stages"

st.set_page_config(page_title="The Heart Heist — Sneha", page_icon="💘", layout="wide")

# -----------------------
# Helpers
# -----------------------
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

# -----------------------
# Inputs (sender / recipient / accent / date)
# -----------------------
st.title("The Heart Heist — prepare the mission")
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    sender = st.text_input("Sender name", value="Parth")
with col2:
    recipient = st.text_input("Recipient name", value="Sneha")
with col3:
    accent = st.color_picker("Accent color", value="#ff6b8a")
with col4:
    date_choice = st.date_input("Proposed date", value=datetime.date(datetime.datetime.now().year, 2, 14))

st.markdown("---")
st.markdown("Hand your phone to the recipient when you're ready. Each stage is playful — follow the instructions on the screen and then tap **I've finished this stage — Continue** below the frame to proceed.")

# stage list (order)
stages = ["vault", "puzzle", "rain", "finale"]

# session state for current stage
if "stage_idx" not in st.session_state:
    st.session_state.stage_idx = 0

# UI controls: goto, restart
cola, colb, colc = st.columns([1,1,1])
with cola:
    if st.button("Restart mission"):
        st.session_state.stage_idx = 0
with colb:
    st.markdown(f"**Current stage:** {st.session_state.stage_idx+1} / {len(stages)} — **{stages[st.session_state.stage_idx].upper()}**")
with colc:
    if st.button("Jump to finale"):
        st.session_state.stage_idx = len(stages)-1

# prepare ICS
dtstart = datetime.datetime.combine(date_choice, datetime.time(hour=19, minute=0))
ics_uri, ics_text = make_ics_data_uri(f"Valentine Night with {recipient}", f"Valentine Date Night with {recipient} — sent by {sender}.", dtstart)

# Shared JS arrays
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

# load template for current stage
curr_stage = stages[st.session_state.stage_idx]
template = load_stage_template(curr_stage)

# mapping placeholders in template
mapping = {
    "{{SENDER}}": sender,
    "{{RECIPIENT}}": recipient,
    "{{ACCENT}}": accent,
    "{{YOU_URI}}": "",   # we removed uploads; templates use placeholders or defaults
    "{{HER_URI}}": "",
    "{{AUDIO_URL}}": "https://cdn.simplecast.com/audio/6a2bbd/lofi-chill-beats.mp3",
    "{{POEM_WORDS_JSON}}": poem_words_json,
    "{{COMPLIMENTS_JSON}}": compliments_json,
    "{{ICS_URI}}": ics_uri,
    "{{DATE_HUMAN}}": dtstart.strftime("%A, %B %d, %Y at %I:%M %p"),
}

html = inject(template, mapping)

# show the embedded stage
st.components.v1.html(html, height=720, scrolling=True)

# After the user completes the interactive experience in the frame they click the big done button
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


# At the end show downloads & notes
if st.session_state.stage_idx == len(stages)-1:
    st.markdown("---")
    st.write("Final assets:")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download full experience (standalone HTML)", data=html.encode("utf-8"), file_name=f"heart_heist_{recipient}.html", mime="text/html")
    with c2:
        st.download_button("Download .ics calendar file", data=ics_text.encode("utf-8"), file_name=f"valentine_{recipient}.ics", mime="text/calendar")

    st.markdown(
        """
        **Notes**
        - The embedded frames are self-contained and mobile-friendly.
        - Audio starts only after the user presses & holds the scanner on the first stage.
        - No image upload or storage.
        """
    )
