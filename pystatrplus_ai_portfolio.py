import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime, timedelta
import os
import tempfile
import json
import base64
from io import BytesIO
import time
import hashlib

# Configuration Files
CONFIG_FILE = "branding_presets.json"
ADMIN_CONFIG_FILE = "admin_settings.json"

def load_presets():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_presets(presets):
    with open(CONFIG_FILE, "w") as f:
        json.dump(presets, f, indent=2)

def load_admin_settings():
    if os.path.exists(ADMIN_CONFIG_FILE):
        with open(ADMIN_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"client_pdf_theme": "Light"}

def save_admin_settings(settings):
    with open(ADMIN_CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# Simplified authentication
def simple_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username: str, password: str):
    if "password_overrides" not in st.session_state:
        st.session_state.password_overrides = {}

    # Load admin settings for expiry policy
    admin_settings = load_admin_settings()
    expiry_hours = admin_settings.get("override_expiry_hours", 24)
    max_age = expiry_hours * 3600  # seconds

    users = {
        "alierwai": {
            "password": simple_hash(st.secrets["users"]["alierwai_password"]),
            "role": "admin",
            "name": "Alier Kergany"
        },
        "client1": {
            "password": simple_hash(st.secrets["users"]["client1_password"]),
            "role": "client",
            "name": "Client One"
        },
        "client2": {
            "password": simple_hash(st.secrets["users"]["client2_password"]),
            "role": "client",
            "name": "Client Two"
        }
    }

    override_used = False
    nnow = datetime.now()

    if username in st.session_state.password_overrides:
        entry = st.session_state.password_overrides[username]
        age = (now - entry["timestamp"]).total_seconds()

        if age <= max_age:
            # Override is still valid → use it
            users[username]["password"] = simple_hash(entry["password"])
            override_used = True
        else:
            # Expired → drop it
            del st.session_state.password_overrides[username]
            if "password_overrides" in admin_settings and username in admin_settings["password_overrides"]:
                del admin_settings["password_overrides"][username]
                save_admin_settings(admin_settings)

    # Validate credentials
    if username in users and users[username]["password"] == simple_hash(password):
        users[username]["override_used"] = override_used
        return users[username]

    return None


def check_session_timeout():
    current_time = time.time()
    if "last_activity" in st.session_state:
        if current_time - st.session_state["last_activity"] > 900:  # 15 minutes
            st.session_state.clear()
            st.rerun()
    st.session_state["last_activity"] = current_time

def apply_custom_css():
    st.markdown("""
    
    <style>
    /* Futuristic animated background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e3a8a, #2563eb, #38bdf8);
        background-size: 400% 400%;
        animation: gradientShift 18s ease infinite;
        font-family: 'Poppins', sans-serif;
        color: #f1f5f9;
    }
    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Headers */
    .main-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(18px);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        text-align: center;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFD700, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: 1px;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #38BDF8;
        font-weight: 300;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(56,189,248,0.7);
    }

    /* Section Cards (Glassmorphism) */
    ./* Client Dashboard Cards */
    .client-container {
        background: rgba(30, 58, 138, 0.85); /* Deep Blue with transparency */
        border: 1px solid rgba(56, 189, 248, 0.6); /* Cyan border */
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.35); /* Subtle glow */
        transition: all 0.3s ease;
    }
    .client-container:hover {
        box-shadow: 0 0 28px rgba(255, 215, 0, 0.7); /* Gold glow on hover */
        transform: translateY(-3px);
    }

    /* Client section headers inside cards */
    .client-container h3, 
    .client-container h2 {
        color: #FFD700 !important; /* Gold titles */
        font-weight: 700;
        text-shadow: 0 0 6px rgba(255, 215, 0, 0.6);
    }

    /* Inputs inside client cards */
    .client-container input, 
    .client-container textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
    }
    .client-container input:focus, 
    .client-container textarea:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.8) !important;
        outline: none !important;
    }

    /* File Uploader Styling */
    .stFileUploader {
        background: rgba(30, 58, 138, 0.85) !important; /* Deep Blue background */
        border: 1px solid rgba(56, 189, 248, 0.6) !important; /* Cyan border */
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.25) !important;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        box-shadow: 0 0 22px rgba(255, 215, 0, 0.7) !important; /* Gold glow on hover */
        border-color: #FFD700 !important;
    }
    .stFileUploader label {
        color: #FFD700 !important; /* Gold text for labels */
        font-weight: 600 !important;
    }
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed rgba(56, 189, 248, 0.6) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    .stFileUploader div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #FFD700 !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.7) !important;
    }

    /* Unified Buttons */
    .stButton button, .stDownloadButton button {
        background: linear-gradient(135deg, #38BDF8, #2563EB) !important; /* Cyan gradient */
        color: #fff !important;
        font-weight: 600 !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background: linear-gradient(135deg, #FFD700, #FFA500) !important; /* Gold gradient */
        border-color: #FFD700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.7) !important;
        transform: translateY(-2px) !important;
    }
    .stButton button:active, .stDownloadButton button:active {
        transform: scale(0.97) !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5) !important;
    }

    /* Sidebar Radio & Checkbox Styling */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    /* Radio/Checkbox inputs */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
    section[data-testid="stSidebar"] .stCheckbox input[type="checkbox"] {
        accent-color: #38BDF8 !important; /* Cyan checkmark */
    }

    /* Sidebar Slider Styling */
    section[data-testid="stSidebar"] .stSlider [role="slider"] {
        background: #38BDF8 !important;   /* cyan handle */
        border: 2px solid #FFD700 !important; /* gold border */
        box-shadow: 0 0 10px rgba(56,189,248,0.8) !important;
    }

    section[data-testid="stSidebar"] .stSlider [role="slider"]:hover {
        background: #FFD700 !important;  /* gold handle on hover */
        border-color: #38BDF8 !important;
        box-shadow: 0 0 14px rgba(255,215,0,0.9) !important;
    }

    /* Slider track */
    section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
        background: linear-gradient(90deg, #38BDF8, #FFD700) !important;
        height: 6px !important;
        border-radius: 3px;
    }


    /* Glow effect on hover */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover,
    section[data-testid="stSidebar"] .stCheckbox:hover {
        text-shadow: 0 0 6px rgba(56,189,248,0.8) !important;
        color: #FFD700 !important; /* Gold glow text */
    }


    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        color: #f1f5f9 !important;
        border: 1px solid rgba(56, 189, 248, 0.6);
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #FFD700, #facc15);
        color: #1e3a8a !important;
        box-shadow: 0 0 16px rgba(255, 215, 0, 0.8);
        transform: translateY(-2px);
    }

    /* Sidebar radio & checkbox labels */
    section[data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:hover label,
    section[data-testid="stSidebar"] div[role="checkbox"] > div:hover label {
        color: #FFD700 !important;
        text-shadow: 0 0 6px rgba(255, 215, 0, 0.7);
    }

    /* Sidebar sliders */
    section[data-testid="stSidebar"] .stSlider [role="slider"] {
        background: #FFD700 !important; /* gold handle */
        border: 2px solid #38BDF8 !important; /* cyan border */
    }
    section[data-testid="stSidebar"] .stSlider > div[role="presentation"] {
        background: linear-gradient(90deg, #1e3a8a, #38BDF8) !important; /* track */
    }

    /* Sidebar Text Input Styling */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="password"],
    section[data-testid="stSidebar"] input[type="email"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        padding: 8px 10px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease-in-out !important;
    }

    /* Focused state (glow) */
    section[data-testid="stSidebar"] input[type="text"]:focus,
    section[data-testid="stSidebar"] input[type="password"]:focus,
    section[data-testid="stSidebar"] input[type="email"]:focus {
        outline: none !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.9) !important;
    }


    /* Client dashboard section headers */
    .client-container h3, 
    .client-container h2 {
        color: #FFD700 !important;   /* bright yellow */
        text-shadow: 0 0 6px rgba(56, 189, 248, 0.6); /* cyan glow */
        font-weight: 700;
        margin-bottom: 0.75rem;
    }


    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FFD700;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 400;
    }

    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tabs: text colors */
    .stTabs [role="tab"]{
      color:#FFD700 !important;         /* default = gold */
      font-weight:600;
      box-shadow:none !important;       /* nuke any built-in underline via shadow */
      border-bottom:none !important;
    }
    .stTabs [role="tab"]:hover{
      color:#38BDF8 !important;         /* hover = cyan */
      text-shadow:0 0 6px rgba(56,189,248,.7);
    }
    .stTabs [role="tab"][aria-selected="true"]{
      color:#38BDF8 !important;         /* active = cyan text */
    }

    /* Streamlit/BaseWeb moving highlight bar (the underline) */
    .stTabs [data-baseweb="tab-highlight"]{
      background-color:#FFD700 !important;   /* gold bar */
      height:3px !important;
      border-radius:3px !important;
    }

    /* Fallbacks for newer/older builds that don’t expose data-baseweb */
    .stTabs [class*="tab-highlight"], 
    .stTabs [class*="TabsHighlight"],
    .stTabs div[role="tablist"] > div:last-child{
      background-color:#FFD700 !important;
      height:3px !important;
      border-radius:3px !important;
    }

    /* Remove any bottom border on the tab strip itself */
    .stTabs [role="tablist"]{
      border-bottom:none !important;
    }


    /* Hyperlinks inside app */
    a {
        color: #38BDF8 !important;   /* cyan links */
        text-decoration: none !important;
        font-weight: 500;
    }
    a:hover {
        color: #FFD700 !important;   /* yellow on hover */
        text-shadow: 0 0 8px rgba(255,215,0,0.7);
    }

    /* Scenario Analysis & General Table Styling */
    .stTable table {
        border-collapse: collapse !important;
        width: 100% !important;
        border: 1px solid rgba(56,189,248,0.4) !important; /* cyan border */
        border-radius: 12px !important;
        overflow: hidden !important;
        font-size: 0.95rem !important;
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.6) !important; /* glassy dark navy */
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 0 18px rgba(56,189,248,0.3) !important;
    }

    /* Table headers */
    .stTable th {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #FFD700 !important;
        text-align: center !important;
        padding: 10px !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #FFD700 !important;
    }

    /* Table rows */
    .stTable td {
        padding: 8px 10px !important;
        text-align: center !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Alternate row background */
    .stTable tr:nth-child(even) td {
        background: rgba(56,189,248,0.08) !important;
    }

    /* Hover effect */
    .stTable tr:hover td {
        background: rgba(255, 215, 0, 0.12) !important;
        color: #FFD700 !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Success box → Cyan glow */
    .stAlert[data-baseweb="notification"][kind="success"] {
        background: rgba(56,189,248,0.1) !important;
        border: 1px solid #38BDF8 !important;
        color: #38BDF8 !important;
        border-radius: 12px !important;
        box-shadow: 0 0 12px rgba(56,189,248,0.6) !important;
        font-weight: 600 !important;
    }

    /* Error box → Gold warning */
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: rgba(255, 215, 0, 0.1) !important;
        border: 1px solid #FFD700 !important;
        color: #FFD700 !important;
        border-radius: 12px !important;
        box-shadow: 0 0 12px rgba(255,215,0,0.6) !important;
        font-weight: 600 !important;
    }

    /* Warning box → Yellow glow (softer than error) */
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: rgba(250, 204, 21, 0.1) !important;
        border: 1px solid #facc15 !important;
        color: #facc15 !important;
        border-radius: 12px !important;
        box-shadow: 0 0 12px rgba(250, 204, 21, 0.6) !important;
        font-weight: 600 !important;
    }

    /* Info box → Neutral cyan */
    .stAlert[data-baseweb="notification"][kind="info"] {
        background: rgba(15, 23, 42, 0.6) !important; /* dark navy glass */
        border: 1px solid #38BDF8 !important;
        color: #38BDF8 !important;
        border-radius: 12px !important;
        box-shadow: 0 0 12px rgba(56,189,248,0.4) !important;
        font-weight: 500 !important;
    }

    /* Keyframes for glowing pulse */
    @keyframes pulseGlow {
        0% { text-shadow: 0 0 6px rgba(56,189,248,0.6); }
        50% { text-shadow: 0 0 16px rgba(255,215,0,0.9); }
        100% { text-shadow: 0 0 6px rgba(56,189,248,0.6); }
    }

    /* 🔹 Success → 🚀 (bright yellow background) */
    .stAlert[data-baseweb="notification"][kind="success"] {
        background: rgba(255, 215, 0, 0.15) !important; /* soft gold */
        border-left: 4px solid #FFD700 !important;
        border-radius: 10px !important;
        color: #FFD700 !important;
    }
    .stAlert[data-baseweb="notification"][kind="success"] [data-testid="stMarkdownContainer"] p:first-child:before {
        content: "🚀 " !important;
        font-size: 1.2rem;
        margin-right: 6px;
        animation: pulseGlow 2s infinite ease-in-out;
    }

    /* 🔹 Error → ❌ (deep red background) */
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: rgba(220, 38, 38, 0.15) !important; /* soft red */
        border-left: 4px solid #DC2626 !important;
        border-radius: 10px !important;
        color: #f87171 !important;
    }
    .stAlert[data-baseweb="notification"][kind="error"] [data-testid="stMarkdownContainer"] p:first-child:before {
        content: "❌ " !important;
        font-size: 1.2rem;
        margin-right: 6px;
        animation: pulseGlow 2s infinite ease-in-out;
    }

    /* 🔹 Warning → ⚡ (orange-gold background) */
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: rgba(251, 191, 36, 0.15) !important; /* amber */
        border-left: 4px solid #fbbf24 !important;
        border-radius: 10px !important;
        color: #facc15 !important;
    }
    .stAlert[data-baseweb="notification"][kind="warning"] [data-testid="stMarkdownContainer"] p:first-child:before {
        content: "⚡ " !important;
        font-size: 1.2rem;
        margin-right: 6px;
        animation: pulseGlow 2s infinite ease-in-out;
    }

    /* 🔹 Info → 🔑 (cyan background) */
    .stAlert[data-baseweb="notification"][kind="info"] {
        background: rgba(56, 189, 248, 0.15) !important; /* cyan */
        border-left: 4px solid #38BDF8 !important;
        border-radius: 10px !important;
        color: #38BDF8 !important;
    }
    .stAlert[data-baseweb="notification"][kind="info"] [data-testid="stMarkdownContainer"] p:first-child:before {
        content: "🔑 " !important;
        font-size: 1.2rem;
        margin-right: 6px;
        animation: pulseGlow 2s infinite ease-in-out;
    }

    /* Unified alert card style */
    .stAlert[data-baseweb="notification"] {
        width: 100% !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
        border-radius: 16px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        box-shadow: 0 0 20px rgba(56,189,248,0.25) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s ease-in-out !important;
    }

    /* On hover, make alerts glow brighter */
    .stAlert[data-baseweb="notification"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 28px rgba(255, 215, 0, 0.5) !important;
    }

    /* Inner text spacing */
    .stAlert [data-testid="stMarkdownContainer"] {
        line-height: 1.6 !important;
    }

    /* Buttons inside alert boxes */
    .stAlert button {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        margin-top: 0.5rem !important;
        box-shadow: 0 0 12px rgba(56,189,248,0.6) !important;
        transition: all 0.3s ease-in-out !important;
    }

    /* Hover effect */
    .stAlert button:hover {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.8) !important;
        transform: translateY(-2px) scale(1.02);
    }

    /* Global Streamlit buttons */
    .stButton > button {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        margin: 0.5rem 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.6) !important;
        transition: all 0.25s ease-in-out !important;
    }

    /* Hover effect */
    .stButton > button:hover {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        box-shadow: 0 0 24px rgba(255,215,0,0.9) !important;
        transform: translateY(-2px) scale(1.03);
    }

    /* Disabled button state */
    .stButton > button:disabled {
        background: rgba(148,163,184,0.3) !important;
        color: rgba(241,245,249,0.6) !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }

    /* Tabs with cyan/gold glow */
    .stTabs [role="tab"] {
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 10px !important;
        transition: all 0.3s ease-in-out !important;
        color: #FFD700 !important; /* default gold */
    }

    /* Hover effect */
    .stTabs [role="tab"]:hover {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.7) !important;
    }

    /* Active tab */
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        box-shadow: 0 0 24px rgba(255,215,0,0.9) !important;
        transform: translateY(-2px);
    }

    /* Underline highlight bar → hidden (we use glow instead) */
    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent !important;
    }
    /* Tabs with cyan/gold glow */
    .stTabs [role="tab"] {
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 10px !important;
        transition: all 0.3s ease-in-out !important;
        color: #FFD700 !important; /* default gold */
    }

    /* Hover effect */
    .stTabs [role="tab"]:hover {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.7) !important;
    }

    /* Active tab */
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        box-shadow: 0 0 24px rgba(255,215,0,0.9) !important;
        transform: translateY(-2px);
    }

    /* Underline highlight bar → hidden (we use glow instead) */
    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent !important;
    }


    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Download Button Styling */
    .stDownloadButton button {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #f1f5f9 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 0 10px rgba(56,189,248,0.6) !important;
    }

    /* Sidebar Radio Buttons - PyStatR+ Glow */
    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 600 !important;
        text-transform: uppercase !important;
        color: #FFD700 !important; /* gold text */
        margin-bottom: 0.5rem !important;
    }

    /* ========================= */
    /* ✅ Checkboxes - PyStatR+ Glow */
    /* ========================= */
    [data-testid="stSidebar"] .stCheckbox label {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 500 !important;
        color: #e5e7eb !important;
        transition: all 0.3s ease-in-out !important;
        cursor: pointer;
    }

    [data-testid="stSidebar"] .stCheckbox label:hover {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.6) !important;
    }

    [data-testid="stSidebar"] .stCheckbox input:checked + div {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        border-radius: 6px !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.8) !important;
    }

    /* ========================= */
    /* 🎚️ Sliders - PyStatR+ Glow */
    /* ========================= */
    [data-testid="stSidebar"] .stSlider > div {
        padding: 0.8rem !important;
        border-radius: 12px !important;
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }

    [data-testid="stSidebar"] .stSlider .st-bb {
        background: linear-gradient(90deg, #38BDF8, #FFD700) !important;
        height: 6px !important;
        border-radius: 4px !important;
        box-shadow: 0 0 10px rgba(56,189,248,0.6), 0 0 15px rgba(255,215,0,0.7) !important;
    }

    [data-testid="stSidebar"] .stSlider .st-at {
        background: #38BDF8 !important; /* unfilled portion */
        opacity: 0.3 !important;
    }

    [data-testid="stSidebar"] .stSlider .st-af {
        background: #FFD700 !important; /* handle active */
        border: 2px solid #1E3A8A !important;
        box-shadow: 0 0 10px rgba(255,215,0,0.9) !important;
    }

    /* ========================= */
    /* ⬇️ Selectboxes - PyStatR+ Glow */
    /* ========================= */
    [data-testid="stSidebar"] .stSelectbox > div {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        padding: 0.6rem !important;
        color: #e5e7eb !important;
        transition: all 0.3s ease-in-out !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div:hover {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.6) !important;
        color: #fff !important;
    }

    /* Dropdown menu itself */
    [data-testid="stSidebar"] .stSelectbox [role="listbox"] {
        background: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
    }

    [data-testid="stSidebar"] .stSelectbox [role="option"][aria-selected="true"] {
        background: linear-gradient(90deg, #38BDF8, #FFD700) !important;
        color: #fff !important;
        font-weight: 600 !important;
    }

    /* ========================= */
    /* 📝 Text Inputs - PyStatR+ Glow */
    /* ========================= */
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        color: #e5e7eb !important;
        transition: all 0.3s ease-in-out !important;
    }

    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 14px rgba(255,215,0,0.8) !important;
        outline: none !important;
        color: #fff !important;
    }


    /* Radio options */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(15, 23, 42, 0.4) !important; /* dark glass */
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 500 !important;
        color: #e5e7eb !important; /* light gray text */
        transition: all 0.3s ease-in-out !important;
        cursor: pointer;
    }

    /* Hover effect */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.6) !important;
    }

    /* Active / Selected */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.8) !important;
        font-weight: 700 !important;
        transform: translateY(-1px);
    }


    /* Hover effect */
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #FFD700, #38BDF8) !important;
        color: #0f172a !important;  /* dark ink text for contrast */
        border-color: #38BDF8 !important;
        box-shadow: 0 0 18px rgba(255,215,0,0.9) !important;
        transform: translateY(-2px) scale(1.03);
    }

    /* ================================== */
    /* 🌟 Sidebar Glow Theme — PyStatR+   */
    /* ================================== */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 0 20px rgba(56,189,248,0.25) !important;
    }

    /* === Sidebar Headers === */
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFD700 !important; /* Gold headings */
        text-shadow: 0 0 8px rgba(255,215,0,0.6) !important;
    }

    /* === Radios === */
    [data-testid="stSidebar"] .stRadio [role="radio"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease-in-out !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"]:hover {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 10px rgba(56,189,248,0.7) !important;
    }
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] {
        background: linear-gradient(90deg, #38BDF8, #FFD700) !important;
        color: #fff !important;
        font-weight: 600 !important;
    }

    /* === Checkboxes === */
    [data-testid="stSidebar"] .stCheckbox {
        padding: 0.4rem 0.2rem !important;
        border-radius: 8px !important;
        transition: background 0.3s ease-in-out !important;
    }
    [data-testid="stSidebar"] .stCheckbox:hover {
        background: rgba(56,189,248,0.15) !important;
    }
    [data-testid="stSidebar"] .stCheckbox input:checked ~ div {
        color: #FFD700 !important;
        font-weight: 600 !important;
    }

    /* === Sliders === */
    [data-testid="stSidebar"] .stSlider [role="slider"] {
        background: #FFD700 !important; /* Gold knob */
        border: 2px solid #38BDF8 !important;
        box-shadow: 0 0 12px rgba(56,189,248,0.6) !important;
    }
    [data-testid="stSidebar"] .stSlider [role="slider"]:hover {
        box-shadow: 0 0 18px rgba(255,215,0,0.8) !important;
    }
    [data-testid="stSidebar"] .stSlider [role="slider"]::-webkit-slider-runnable-track {
        background: linear-gradient(90deg, #38BDF8, #FFD700) !important;
        border-radius: 6px !important;
    }

    /* === Selectboxes === */
    [data-testid="stSidebar"] .stSelectbox > div {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        padding: 0.6rem !important;
        color: #e5e7eb !important;
        transition: all 0.3s ease-in-out !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div:hover {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.6) !important;
        color: #fff !important;
    }
    [data-testid="stSidebar"] .stSelectbox [role="listbox"] {
        background: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stSelectbox [role="option"][aria-selected="true"] {
        background: linear-gradient(90deg, #38BDF8, #FFD700) !important;
        color: #fff !important;
        font-weight: 600 !important;
    }

    /* === Text Inputs === */
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        color: #e5e7eb !important;
        transition: all 0.3s ease-in-out !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 14px rgba(255,215,0,0.8) !important;
        outline: none !important;
        color: #fff !important;
    }

    /* Slider track */
    .stSlider > div[data-baseweb="slider"] > div {
        background: linear-gradient(90deg, #1E3A8A, #2563EB); /* deep blue gradient */
        border-radius: 8px;
        height: 10px;
    }
    
    /* Slider handle (thumb) */
    .stSlider > div[data-baseweb="slider"] > div > div[role="slider"] {
        background-color: #38BDF8 !important; /* cyan */
        border: 2px solid #FFD700 !important; /* gold outline */
        box-shadow: 0 0 10px rgba(56,189,248,0.7);
        transition: all 0.3s ease;
    }
    
    /* Hover/focus glow */
    .stSlider > div[data-baseweb="slider"] > div > div[role="slider"]:hover,
    .stSlider > div[data-baseweb="slider"] > div > div[role="slider"]:focus {
        box-shadow: 0 0 15px rgba(255,215,0,0.8); /* gold glow */
        transform: scale(1.1); /* subtle zoom */
    }
    
    /* Value label above slider */
    .stSlider label, .stSlider span {
        color: #FFFFFF !important; /* white text */
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)


def create_metric_cards():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">4.9⭐</div>
            <div class="metric-label">Expert Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">15K+</div>
            <div class="metric-label">Portfolios Crafted</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">98%</div>
            <div class="metric-label">Client Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">⚡ AI</div>
            <div class="metric-label">Powered Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

def add_images_to_story(story, images):
    temp_files = []
    if images:
        for img_file in images:
            try:
                img_file.seek(0)
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(img_file.name)[1]) as tmp:
                    tmp.write(img_file.read())
                    tmp_path = tmp.name
                    temp_files.append(tmp_path)
                story.append(Image(tmp_path, width=300, height=200))
                story.append(Spacer(1, 12))
            except Exception as e:
                st.warning(f"Could not process image {img_file.name}: {str(e)}")
    return temp_files

def add_watermark(canvas_obj, doc, theme="Light", logo_path=None):
    canvas_obj.saveState()
    
    # Faint color for text fallback
    if theme == "Dark":
        wm_color = colors.Color(1, 1, 1, alpha=0.08)  # faint white
    else:
        wm_color = colors.Color(0.1, 0.2, 0.5, alpha=0.08)  # faint navy
    
    if logo_path and os.path.exists(logo_path):
        # Semi-transparent logo watermark
        from reportlab.lib.utils import ImageReader
        logo = ImageReader(logo_path)
        canvas_obj.translate(150, 250)
        canvas_obj.rotate(30)
        canvas_obj.drawImage(
            logo,
            0, 0,
            width=300, height=300,
            mask='auto'
        )
    else:
        # Fallback text watermark
        canvas_obj.setFont("Helvetica-Bold", 60)
        canvas_obj.setFillColor(wm_color)
        canvas_obj.translate(300, 400)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, "PyStatRPlus")
    
    canvas_obj.restoreState()


def generate_pdf(filename, theme="Light", **kwargs):
    temp_files = []
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Futuristic Theme Colors
        if theme == "Dark":
            text_color_main = colors.HexColor("#F8FAFC")
            title_color = colors.HexColor("#FFD700")       # gold
            heading_color = colors.HexColor("#38BDF8")     # cyan
            accent_color = colors.HexColor("#FFD700")
        else:  # Light theme
            text_color_main = colors.HexColor("#1A365D")
            title_color = colors.HexColor("#1E3A8A")       # deep blue
            heading_color = colors.HexColor("#38BDF8")     # cyan
            accent_color = colors.HexColor("#FFD700")      # gold
        
        # Title Style
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles['Title'],
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=title_color,
            alignment=TA_CENTER,
            spaceAfter=30,
            leading=32
        )
        
        # Section Heading Style
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles['Heading2'],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=heading_color,
            spaceBefore=24,
            spaceAfter=12,
            borderWidth=1,
            borderColor=accent_color,
            borderPadding=4,
            leading=20
        )
        
        # Body Text
        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles['Normal'],
            fontName="Helvetica",
            fontSize=12,
            textColor=text_color_main,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=16
        )
        
        # --- Cover Page ---
        story.append(Spacer(1, 80))
        
        if kwargs.get("logo"):
            try:
                logo_bytes = base64.b64decode(kwargs["logo"])
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo_bytes)
                    tmp_path = tmp.name
                    temp_files.append(tmp_path)
                story.append(Image(tmp_path, width=150, height=150))
                story.append(Spacer(1, 50))
            except:
                pass
        
        story.append(Paragraph(kwargs.get("project_title", "AI Consulting Portfolio"), title_style))
        story.append(Paragraph("Professional Consulting Portfolio", heading_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Prepared by: {kwargs.get('name', 'AI Consultant')}", body_style))
        
        if kwargs.get("date"):
            if hasattr(kwargs["date"], 'strftime'):
                date_str = kwargs["date"].strftime('%B %d, %Y')
            else:
                date_str = str(kwargs["date"])
            story.append(Paragraph(f"Date: {date_str}", body_style))
        
        story.append(Spacer(1, 60))
        
        # Divider + Tagline Footer on Cover
        divider_color = colors.HexColor("#38BDF8") if theme == "Light" else colors.HexColor("#FFD700")
        divider = Table(
            [[""]],
            colWidths=[450],
            rowHeights=[6],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), divider_color),
                ("LINEBELOW", (0, 0), (-1, -1), 0, divider_color),
            ])
        )
        story.append(divider)
        story.append(Spacer(1, 20))
        footer_text = Paragraph(
            "🚀 Elevating Expertise into Professional Impact — Powered by PyStatR+",
            ParagraphStyle(
                "Footer",
                fontName="Helvetica-Oblique",
                fontSize=10,
                textColor=divider_color,
                alignment=TA_CENTER,
                spaceBefore=10
            )
        )
        story.append(footer_text)
        story.append(PageBreak())
        
        # --- Content Sections ---
        sections = [
            ("Executive Summary", "exec_summary"),
            ("Strategic Opportunities", "opportunities"),
            ("Risk Assessment", "risks"),
            ("Scenario Analysis", "scenarios"),
            ("Professional Insights", "reflection"),
            ("Design Case Study", "logo_text")
        ]
        
        for title, key in sections:
            if kwargs.get(key):
                story.append(Paragraph(title, heading_style))
                
                if key in ["opportunities", "risks"]:
                    items = [line.strip() for line in kwargs[key].split("\n") if line.strip()]
                    for item in items:
                        story.append(Paragraph(f"• {item}", body_style))
                elif key == "scenarios":
                    lines = [line for line in kwargs[key].split("\n") if "|" in line]
                    if lines:
                        table_data = [["Option", "Investment", "Benefits", "Risks", "Recommendation"]]
                        for line in lines:
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) >= 5:
                                table_data.append(parts[:5])
                        
                        if len(table_data) > 1:
                            table = Table(table_data, colWidths=[80, 70, 120, 120, 100])
                            table.setStyle(TableStyle([
                                ("BACKGROUND", (0, 0), (-1, 0), heading_color),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 10),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke if theme=="Light" else colors.HexColor("#1E293B")),
                                ("GRID", (0, 0), (-1, -1), 1, accent_color),
                            ]))
                            story.append(table)
                else:
                    story.append(Paragraph(kwargs[key], body_style))
                
                # Section Images
                image_key = f"{key}_images"
                if kwargs.get(image_key):
                    img_temp_files = add_images_to_story(story, kwargs[image_key])
                    temp_files.extend(img_temp_files)
                
                story.append(Spacer(1, 20))
        
        # --- Closing Page ---
        story.append(PageBreak())
        
        closing_divider_color = colors.HexColor("#38BDF8") if theme == "Light" else colors.HexColor("#FFD700")
        closing_divider = Table(
            [[""]],
            colWidths=[450],
            rowHeights=[6],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), closing_divider_color),
                ("LINEBELOW", (0, 0), (-1, -1), 0, closing_divider_color),
            ])
        )
        story.append(Spacer(1, 200))
        story.append(closing_divider)
        story.append(Spacer(1, 30))
        
        closing_text = Paragraph(
            "🙏 Thank you for reviewing this portfolio.<br/>For inquiries, collaborations, or consulting engagements, please contact your PyStatR+ consultant.",
            ParagraphStyle(
                "ClosingText",
                fontName="Helvetica",
                fontSize=12,
                textColor=text_color_main,
                alignment=TA_CENTER,
                leading=16,
                spaceBefore=20
            )
        )
        story.append(closing_text)
        story.append(Spacer(1, 40))
        
        closing_footer = Paragraph(
            "🚀 Elevating Expertise into Professional Impact — Powered by PyStatR+",
            ParagraphStyle(
                "ClosingFooter",
                fontName="Helvetica-Oblique",
                fontSize=10,
                textColor=closing_divider_color,
                alignment=TA_CENTER,
                spaceBefore=20
            )
        )
        story.append(closing_footer)
        
        # --- Prepare watermark logo (if available) ---
        wm_logo_path = None
        if kwargs.get("logo"):
            try:
                logo_bytes = base64.b64decode(kwargs["logo"])
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo_bytes)
                    wm_logo_path = tmp.name
                    temp_files.append(wm_logo_path)
            except:
                pass
        
        # --- Build PDF with watermark ---
        doc.build(
            story,
            onFirstPage=lambda c, d: add_watermark(c, d, theme, wm_logo_path),
            onLaterPages=lambda c, d: add_watermark(c, d, theme, wm_logo_path)
        )
        return True
        
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
        return False
    finally:
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass


def main():
    st.set_page_config(
    page_title="AI Consulting Portfolio Builder",
    page_icon="docs/screenshots/logo.png",  # Path to your PyStatR+ logo
    layout="wide",
    initial_sidebar_state="expanded"
    )

    
    apply_custom_css()
    
    # Load admin settings
    admin_settings = load_admin_settings()

    def cleanup_expired_overrides(admin_settings):
        """Remove expired overrides from session_state and admin_settings.json"""
        if "password_overrides" not in st.session_state:
            return

        expiry_hours = admin_settings.get("override_expiry_hours", 24)
        max_age = expiry_hours * 3600
        now = datetime.now()

        expired_users = []
        for user, entry in list(st.session_state.password_overrides.items()):
            age = (now - entry["timestamp"]).total_seconds()
            if age > max_age:
                expired_users.append(user)
                del st.session_state.password_overrides[user]
                if "password_overrides" in admin_settings and user in admin_settings["password_overrides"]:
                    del admin_settings["password_overrides"][user]

        if expired_users:
            save_admin_settings(admin_settings)
            st.sidebar.warning(
                f"⚠️ Expired overrides removed: {', '.join(expired_users)}"
            )
    # Clean up expired overrides immediately at startup
    cleanup_expired_overrides(admin_settings)

    # Check session timeout
    check_session_timeout()
    
    # Authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🔐 Portfolio Builder Login</h1>
            <p class="subtitle">Access your professional consulting portfolio tools</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("🔐 Secure Access", use_container_width=True):
                user = check_credentials(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = user["role"]
                    st.session_state.user_name = user["name"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Logout button
    if st.sidebar.button("🚪 End Session"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown(
        f"""
        <div style="text-align:center; margin-bottom:1rem;">
            <img src="https://raw.githubusercontent.com/PyStatRPlus/pystatrplus-ai-portfolio/main/docs/screenshots/logo.png" 
                 alt="PyStatR+ Logo" width="120" style="border-radius:12px;" />
        </div>
        """,
        unsafe_allow_html=True
        )

    
    # User info
    st.sidebar.success(f"👋 Welcome **{st.session_state.user_name}** ({st.session_state.user_role.title()})")
    
    # Admin Dashboard
    if st.session_state.user_role == "admin":
        st.sidebar.markdown("### 🛠️ Admin Controls")
        
        # ✅ Unified password panel (moved out of main)
        render_password_panel(admin_settings)

        # Global client settings
        client_pdf_theme = st.sidebar.radio(
            "Default PDF Theme for All Clients",
            ["Light", "Dark"],
            index=0 if admin_settings["client_pdf_theme"] == "Light" else 1
        )
        
        if client_pdf_theme != admin_settings["client_pdf_theme"]:
            admin_settings["client_pdf_theme"] = client_pdf_theme
            save_admin_settings(admin_settings)
            st.sidebar.success(f"✅ Client theme updated to **{client_pdf_theme}**")
        
        # Load presets
        presets = load_presets()
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🚀 AI Consulting Portfolio Builder</h1>
            <p class="subtitle">Turn your expertise into client-ready, professional portfolios powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        create_metric_cards()
        
        # Main tabs
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "✨ Brand Identity Workshop",
            "📝 Strategic Content Composer",
            "👁️ Interactive Portfolio Preview",
            "📄 Professional Export Hub"
        ])
        
        # Initialize session state
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = {}
        
        with tab1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("## ✨ Branding Studio")
            
            # Preset management
            col1, col2 = st.columns([2, 1])
            
            with col1:
                preset_names = list(presets.keys())
                selected_preset = st.selectbox(
                    "🎯 Brand Preset Library",
                    ["Create New"] + preset_names
                )
            
            with col2:
                if selected_preset != "Create New" and selected_preset in presets:
                    st.success(f"✨ Active: {selected_preset}")
                    branding = presets[selected_preset]
                else:
                    branding = {
                        "name": "AI Consultant Pro",
                        "brand_color": "#1E3A8A",
                        "font_choice": "Helvetica",
                        "logo": None,
                        "pdf_theme": "Light"
                    }
            
            # Branding controls
            col1, col2 = st.columns(2)
            
            with col1:
                name_input = st.text_input(
                    "👤 Professional Identity",
                    value=branding.get("name", "")
                )
                
                brand_color = st.color_picker(
                    "🎨 Signature Brand Color",
                    value=branding.get("brand_color", "#1E3A8A")
                )
            
            with col2:
                font_choice = st.selectbox(
                    "🔤 Typography",
                    ["Helvetica", "Times-Roman", "Courier"],
                    index=["Helvetica", "Times-Roman", "Courier"].index(
                        branding.get("font_choice", "Helvetica")
                    )
                )
                
                pdf_theme = st.radio(
                    "🌓 Document Theme",
                    ["Light", "Dark"],
                    index=0 if branding.get("pdf_theme", "Light") == "Light" else 1,
                    horizontal=True
                )
            
            # Logo upload
            st.markdown("### 🏆 Professional Logo")
            cover_logo = None
            logo_upload = st.file_uploader(
                "Upload Your Brand Mark",
                type=["png", "jpg", "jpeg"]
            )
            
            if logo_upload:
                cover_logo = base64.b64encode(logo_upload.read()).decode("utf-8")
                st.image(base64.b64decode(cover_logo), width=200)
            elif branding.get("logo"):
                cover_logo = branding.get("logo")
                st.image(base64.b64decode(cover_logo), width=200)
            
            # Preset management
            st.markdown("### 💎 Brand Preset Manager")
            preset_name_input = st.text_input(
                "Preset Collection Name",
                value=selected_preset if selected_preset != "Create New" else ""
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💎 Save Branding Profile", use_container_width=True):
                    if preset_name_input.strip():
                        presets[preset_name_input] = {
                            "name": name_input,
                            "brand_color": brand_color,
                            "font_choice": font_choice,
                            "logo": cover_logo,
                            "pdf_theme": pdf_theme
                        }
                        save_presets(presets)
                        st.success(f"✨ Brand preset '{preset_name_input}' saved!")
                        st.rerun()
                    else:
                        st.error("⚠️ Please enter a preset name")
            
            with col2:
                if st.button("🗑️ Delete Branding Profile", use_container_width=True):
                    if selected_preset in presets:
                        del presets[selected_preset]
                        save_presets(presets)
                        st.success(f"🗑️ Preset '{selected_preset}' removed")
                        st.rerun()
            
            with col3:
                if st.button("🔄 Reload Preset Library", use_container_width=True):
                    st.rerun()
            
            # Store branding data
            st.session_state.portfolio_data.update({
                "name": name_input,
                "brand_color": brand_color,
                "font_choice": font_choice,
                "logo": cover_logo,
                "pdf_theme": pdf_theme
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("## 📝 Content Builder")
            
            # Project overview
            st.markdown("### 🎯 Project Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                project_title = st.text_input(
                    "🏆 Portfolio Title",
                    value="Generative AI Consulting Training Program"
                )
            
            with col2:
                date = st.date_input("📅 Project Date", datetime.today())
            
            # Content sections
            sections = [
                ("🎯 Executive Summary", "exec_summary"),
                ("🚀 Strategic Opportunities", "opportunities"),
                ("⚠️ Risk Assessment", "risks"),
                ("📊 Scenario Analysis", "scenarios"),
                ("🧠 Professional Insights", "reflection"),
                ("🎨 Design Case Study", "logo_text")
            ]
            
            content_data = {}
            
            for title, key in sections:
                st.markdown(f"### {title}")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if key in ["opportunities", "risks"]:
                        content_data[key] = st.text_area(
                            f"{title} Content",
                            height=120,
                            label_visibility="collapsed"
                        )
                    elif key == "scenarios":
                        content_data[key] = st.text_area(
                            f"{title} Content",
                            value="Strategic Option A | High Investment | 40% Efficiency Gains | Implementation Risk | Highly Recommended\nStrategic Option B | Medium Investment | 25% Cost Savings | Lower Risk Profile | Worth Considering",
                            height=120,
                            label_visibility="collapsed"
                        )
                    else:
                        content_data[key] = st.text_area(
                            f"{title} Content",
                            height=150,
                            label_visibility="collapsed"
                        )
                
                with col2:
                    content_data[f"{key}_images"] = st.file_uploader(
                        f"Images for {title}",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                        key=f"{key}_images",
                        label_visibility="collapsed"
                    )
                    
                    if content_data[f"{key}_images"]:
                        st.success(f"📸 {len(content_data[f'{key}_images'])} image(s)")
            
            # Store content data
            st.session_state.portfolio_data.update(content_data)
            st.session_state.portfolio_data.update({
                "project_title": project_title,
                "date": date
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("## 👁️ Live Preview")
            
            data = st.session_state.portfolio_data
            
            if data.get("logo"):
                try:
                    logo_bytes = base64.b64decode(data["logo"])
                    st.image(logo_bytes, width=150)
                except:
                    pass
            
            st.title(data.get("project_title", "Project Title"))
            st.write(f"**Prepared by:** {data.get('name', 'Your Name')}")
            
            if data.get("date"):
                st.write(f"**Date:** {data['date'].strftime('%B %d, %Y')}")
            
            st.markdown("---")
            
            sections = [
                ("Executive Summary", "exec_summary"),
                ("Strategic Opportunities", "opportunities"),
                ("Risk Assessment", "risks"),
                ("Scenario Analysis", "scenarios"),
                ("Professional Insights", "reflection"),
                ("Design Case Study", "logo_text")
            ]
            
            for title, key in sections:
                if data.get(key):
                    st.subheader(title)
                    
                    if key in ["opportunities", "risks"]:
                        items = [line.strip() for line in data[key].split("\n") if line.strip()]
                        for item in items:
                            st.write(f"• {item}")
                    elif key == "scenarios":
                        rows = [line.split("|") for line in data[key].split("\n") if "|" in line]
                        if rows:
                            headers = ["Option", "Investment", "Benefits", "Risks", "Recommendation"]
                            table_data = [headers] + [[cell.strip() for cell in row] for row in rows if len(row) >= 5]
                            st.table(table_data)
                    else:
                        st.write(data[key])
                    
                    if data.get(f"{key}_images"):
                        st.image(data[f"{key}_images"], width=300)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("## 📄 PDF Export Studio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                export_theme = st.radio(
                    "🎨 Export Theme",
                    ["Light", "Dark"],
                    horizontal=True
                )
            
            with col2:
                st.info("💡 **Pro Tips:**\n\n• Use high-res images\n• Keep content concise\n• Preview before export")
            
            if st.button("🎯 Generate Professional Portfolio", use_container_width=True):
                try:
                    with st.spinner("✨ Creating your portfolio..."):
                        output_file = "admin_portfolio.pdf"
                        
                        pdf_data = st.session_state.portfolio_data.copy()
                        success = generate_pdf(output_file, theme=export_theme, **pdf_data)
                        
                        if success:
                            with open(output_file, "rb") as f:
                                pdf_bytes = f.read()
                            
                            st.success("🎉 Portfolio generated successfully!")
                            st.download_button(
                                "📥 Download Your Portfolio",
                                pdf_bytes,
                                file_name=f"Admin_Portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            os.remove(output_file)
                        
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Client Dashboard
    elif st.session_state.user_role == "client":
        st.sidebar.markdown("### 👤 Client Portal")
        st.sidebar.info("🎨 Your portfolio uses **PyStatR+ branding** automatically")
        
        # Client header
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">👤 Client Portfolio Portal</h1>
            <p class="subtitle">Build a future-ready consulting portfolio with PyStatR+ branding and AI-driven design</p>
        </div>
        """, unsafe_allow_html=True)

        
        # PyStatR+ branding display
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### 🎨 PyStatR+ Branding (Locked)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🎯 Brand Color:** Deep Blue (#1E3A8A)")
            st.markdown('<div style="width: 100%; height: 30px; background: #1E3A8A; border-radius: 5px;"></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("**✨ Accent Color:** Bright Yellow (#FFD700)")
            st.markdown('<div style="width: 100%; height: 30px; background: #FFD700; border-radius: 5px;"></div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown("**🔤 Typography:** Helvetica")
            st.markdown('<div style="font-family: Helvetica; font-weight: 600; color: #1E3A8A;">Sample Text</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Project information
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### 🎯 Project Information")
        
        col1, col2 = st.columns(2)
        with col1:
            project_title = st.text_input("🏆 Project Title", "Consulting Engagement")
        with col2:
            date = st.date_input("📅 Date")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content sections
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### 📝 Portfolio Content")
        
        exec_summary = st.text_area("🎯 Executive Summary", height=150, 
                                    placeholder="Provide a compelling overview of your project's impact and value")
        
        col1, col2 = st.columns(2)
        with col1:
            opportunities = st.text_area("🚀 Strategic Opportunities", height=120,
                                       placeholder="List key opportunities that drive value (one per line)")
        with col2:
            risks = st.text_area("⚠️ Risk Assessment", height=120,
                                placeholder="Identify potential risks and mitigation strategies (one per line)")
        
        scenarios = st.text_area("📊 Scenario Analysis", 
                                value="Primary Strategy | High Investment | 35% ROI | Moderate Risk | Recommended\nAlternative Approach | Medium Investment | 20% ROI | Lower Risk | Consider",
                                height=100,
                                placeholder="Format: Option | Investment | Benefits | Risks | Recommendation")
        
        reflection = st.text_area("🧠 Professional Insights", height=150,
                                 placeholder="Share your key learnings and strategic recommendations")
        
        logo_text = st.text_area("🎨 Design Case Study", height=150,
                                placeholder="Document your creative process and design decisions")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # File uploads
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### 📸 Visual Assets (Optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            exec_images = st.file_uploader("Executive Summary Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            or_images = st.file_uploader("Opportunities & Risks Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            scen_images = st.file_uploader("Scenario Analysis Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        with col2:
            reflection_images = st.file_uploader("Professional Insights Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            logo_images = st.file_uploader("Design Case Study Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Preview and export
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### 👀 Preview & Export")
        
        # Get client theme from admin settings
        client_pdf_theme = admin_settings.get("client_pdf_theme", "Light")
        
        st.info(f"🎨 Your portfolio will automatically use **PyStatR+ branding** with **{client_pdf_theme} theme** as configured by your consultant.")
        
        if st.button("🎯 Generate Portfolio PDF", use_container_width=True):
            try:
                with st.spinner("✨ Creating your professional portfolio..."):
                    output_file = "client_portfolio.pdf"
                    
                    # Prepare client data with FORCED PyStatR+ branding
                    client_data = {
                        "project_title": project_title,
                        "date": date,
                        "name": f"Client Portfolio - {st.session_state.user_name}",
                        "brand_color": "#1E3A8A",      # Deep Blue (FORCED)
                        "font_choice": "Helvetica",    # FORCED
                        "exec_summary": exec_summary,
                        "opportunities": opportunities,
                        "risks": risks,
                        "scenarios": scenarios,
                        "reflection": reflection,
                        "logo_text": logo_text,
                        "exec_summary_images": exec_images,
                        "opportunities_images": or_images,
                        "risks_images": or_images,  # Note: using same images for both
                        "scenarios_images": scen_images,
                        "reflection_images": reflection_images,
                        "logo_text_images": logo_images
                    }
                    
                    success = generate_pdf(output_file, theme=client_pdf_theme, **client_data)
                    
                    if success:
                        with open(output_file, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.success("🎉 Portfolio generated successfully!")
                        st.download_button(
                            "📥 Download Your Portfolio",
                            pdf_bytes,
                            file_name=f"Client_Portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        os.remove(output_file)
                    
            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
    """
    <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.7);">
        <p>🚀 <strong>AI Consulting Portfolio Builder</strong> — Elevating expertise into professional impact</p>
        <p>Powered by <strong>PyStatRPlus</strong> | Future-ready design meets advanced intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)

def render_password_panel(admin_settings):
    st.sidebar.markdown("### 🔑 Password Management")

    # Initialize session state
    if "password_overrides" not in st.session_state:
        st.session_state.password_overrides = {}

    # Load saved overrides from admin_settings.json if not already in session
    if "password_overrides" in admin_settings:
        for user, info in admin_settings["password_overrides"].items():
            try:
                ts = datetime.datetime.fromisoformat(info["timestamp"])
                st.session_state.password_overrides[user] = {
                    "password": info["password"],
                    "timestamp": ts
                }
            except:
                continue

    # Dynamic user list (exclude admin by default)
    users = list(st.secrets["users"].keys())
    users = [u for u in users if u.lower() != "alierwai"]

    reset_user = st.sidebar.selectbox("Select user", users)
    new_pass = st.sidebar.text_input("New password", type="password")

    # ✅ Update Password block (your snippet goes here)
    if st.sidebar.button("Update Password"):
        st.session_state.password_overrides[reset_user] = {
            "password": new_pass,
            "timestamp": datetime.now()
        }
        admin_settings["password_overrides"] = {
            k: {"password": v["password"], "timestamp": v["timestamp"].isoformat()}
            for k, v in st.session_state.password_overrides.items()
        }
        save_admin_settings(admin_settings)
        st.sidebar.success(f"Password for {reset_user} updated (session + persisted).")

    # Reset ALL overrides
    if st.sidebar.button("🔄 Reset to Default Passwords"):
        st.session_state.password_overrides.clear()
        admin_settings.pop("password_overrides", None)
        save_admin_settings(admin_settings)
        st.sidebar.info("All overrides cleared; defaults restored.")

    # Expiry control
    expiry_hours = admin_settings.get("override_expiry_hours", 24)
    st.sidebar.markdown("#### ⏳ Override Expiry")
    st.sidebar.caption("ℹ️ Overrides older than this reset automatically.")
    expiry_hours = st.sidebar.slider("Expiry Time (hours)", 1, 72, expiry_hours, 1)

    if expiry_hours != admin_settings.get("override_expiry_hours", 24):
        admin_settings["override_expiry_hours"] = expiry_hours
        save_admin_settings(admin_settings)
        st.sidebar.success(f"✅ Override expiry updated to {expiry_hours} hours")

    MAX_AGE = expiry_hours * 3600

    # Active overrides monitor
    if st.session_state.password_overrides:
        st.sidebar.markdown("#### 🔍 Active Overrides")
        now = datetime.now()
        for user, info in list(st.session_state.password_overrides.items()):
            age = (now - info["timestamp"]).total_seconds()
            remaining = MAX_AGE - age
            if remaining > 0:
                hrs = int(remaining // 3600)
                mins = int((remaining % 3600) // 60)
                st.sidebar.write(
                    f"**{user}** — expires in ⏳ {hrs}h {mins}m "
                    f"(set {info['timestamp'].strftime('%Y-%m-%d %H:%M')})"
                )
            else:
                # Auto-clean expired overrides
                del st.session_state.password_overrides[user]
                if "password_overrides" in admin_settings and user in admin_settings["password_overrides"]:
                    del admin_settings["password_overrides"][user]
                    save_admin_settings(admin_settings)
                st.sidebar.warning(f"⚠️ Override for {user} expired and was reset.")

    # Optional Admin Reset (safety valve)
    st.sidebar.markdown("---")
    show_admin_reset = st.sidebar.checkbox("⚠️ Enable Admin Reset (dangerous)", value=False)

    if show_admin_reset:
        st.sidebar.warning("You are about to reset the **admin (alierwai)** password. Proceed carefully.")
        new_admin_pass = st.sidebar.text_input("New admin password", type="password")

        if st.sidebar.button("Update Admin Password"):
            st.session_state.password_overrides["alierwai"] = {
                "password": new_admin_pass,
                "timestamp": datetime.now()
            }
            admin_settings.setdefault("password_overrides", {})
            admin_settings["password_overrides"]["alierwai"] = {
                "password": new_admin_pass,
                "timestamp": datetime.now().isoformat()
            }
            save_admin_settings(admin_settings)
            st.sidebar.success("✅ Admin password override set (session + persisted).")



if __name__ == "__main__":
    main()