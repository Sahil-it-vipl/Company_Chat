import streamlit as st
import os
import time
import sqlite3
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ====== DATABASE SETUP ======
DB_FILE = "chat.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    message TEXT,
    timestamp TEXT
)""")
conn.commit()

UPLOAD_DIR = "shared_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ====== UI CONFIG ======
st.set_page_config(page_title="Purchase Chat & File Share", layout="wide")
st.title("💬 Purchase Chat + 📁 File Sharing")

# Auto refresh chat every 3 seconds
st_autorefresh(interval=3000, key="auto_refresh")

# ====== USERNAME ======
if "username" not in st.session_state or not st.session_state.username:
    st.title("Welcome to Chat 📡")
    name = st.text_input("Enter your name to join chat:")
    if st.button("Join"):
        if name.strip():
            st.session_state.username = name.strip()
            st.rerun()
    st.stop()

username = st.session_state.username

st.sidebar.write(f"🟢 Logged in as: **{username}**")
if st.sidebar.button("Change Name"):
    st.session_state.username = ""
    st.rerun()
username = st.session_state.username

# ====== SIDEBAR (FILE SHARING) ======
st.sidebar.title("📁 File Sharing")

uploaded_file = st.sidebar.file_uploader("Upload a file to share")
if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ File uploaded successfully!")

# List shared files
st.sidebar.subheader("Shared Files:")
for file in os.listdir(UPLOAD_DIR):
    file_path = os.path.join(UPLOAD_DIR, file)
    st.sidebar.download_button(file, open(file_path, "rb"), file)

# ====== CHAT SECTION ======
st.subheader("💬 Chat")

# Display chat messages
c.execute("SELECT username, message, timestamp FROM chat ORDER BY id DESC LIMIT 40")
messages = c.fetchall()
for user, msg, ts in reversed(messages):
    st.write(f"**{user}** [{ts}]: {msg}")


# Send message
message = st.text_input("Type your message...")
if st.button("Send"):
    if message.strip():
        c.execute("INSERT INTO chat (username, message, timestamp) VALUES (?, ?, ?)",
                  (username, message, datetime.now().strftime("%H:%M:%S")))
        conn.commit()
        st.rerun()()
