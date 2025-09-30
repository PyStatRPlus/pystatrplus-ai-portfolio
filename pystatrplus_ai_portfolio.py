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

def simple_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username: str, password: str):
    if "password_overrides" not in st.session_state:
        st.session_state.password_overrides = {}

    admin_settings = load_admin_settings()
    expiry_hours = admin_settings.get("override_expiry_hours", 24)
    max_age = expiry_hours * 3600
    now = datetime.now()

    users = {
        "alierwai": {
            "password": simple_hash(st.secrets["users"]["alierwai_password"]),
            "role": "admin",
            "name": "Alier Reng"
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

    if username in st.session_state.password_overrides:
        entry = st.session_state.password_overrides[username]
        age = (now - entry["timestamp"]).total_seconds()

        if age <= max_age:
            users[username]["password"] = simple_hash(entry["password"])
        else:
            del st.session_state.password_overrides[username]

    if username in users and users[username]["password"] == simple_hash(password):
        return users[username]

    return None

def check_session_timeout():
    current_time = time.time()
    if "last_activity" in st.session_state:
        if current_time - st.session_state["last_activity"] > 900:
            st.session_state.clear()
            st.rerun()
    st.session_state["last_activity"] = current_time

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* ========================================= */
    /* CORE LAYOUT - Maximum Specificity */
    /* ========================================= */
    
    .stApp,
    .stApp > div,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div {
        background: linear-gradient(-45deg, #0f172a, #1e3a8a, #2563eb, #38bdf8) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 18s ease infinite !important;
        font-family: 'Poppins', sans-serif !important;
        color: #f1f5f9 !important;
    }
    
    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    /* ========================================= */
    /* HEADERS - Multiple Selectors */
    /* ========================================= */
    
    .main-header {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(18px) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        margin: 2rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        text-align: center !important;
    }
    
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #FFD700, #38BDF8) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 1rem !important;
        letter-spacing: 1px !important;
    }
    
    .subtitle {
        font-size: 1.2rem !important;
        color: #38BDF8 !important;
        font-weight: 300 !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 0 10px rgba(56,189,248,0.7) !important;
    }
    
    /* ========================================= */
    /* CLIENT CONTAINERS - Enhanced Targeting */
    /* ========================================= */
    
    .client-container,
    div.client-container,
    .stMarkdown .client-container {
        background: rgba(30, 58, 138, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    
    .client-container:hover {
        box-shadow: 0 0 28px rgba(255, 215, 0, 0.7) !important;
        transform: translateY(-3px) !important;
    }
    
    .client-container h3,
    .client-container h2 {
        color: #FFD700 !important;
        font-weight: 700 !important;
        text-shadow: 0 0 6px rgba(255, 215, 0, 0.6) !important;
    }
    
    /* ========================================= */
    /* BUTTONS - All Variants Covered */
    /* ========================================= */
    
    button[kind="primary"],
    button[kind="secondary"],
    .stButton > button,
    .stButton button,
    .stDownloadButton > button,
    .stDownloadButton button,
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"],
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #38BDF8, #2563EB) !important;
        color: #fff !important;
        font-weight: 600 !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
        cursor: pointer !important;
    }
    
    button[kind="primary"]:hover,
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.7) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ========================================= */
    /* TEXT INPUTS - Universal Coverage */
    /* ========================================= */
    
    input[type="text"],
    input[type="password"],
    input[type="email"],
    input[type="number"],
    textarea,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    div[data-baseweb="input"] > input,
    div[data-baseweb="textarea"] > textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
        padding: 8px 12px !important;
        transition: all 0.3s ease !important;
    }
    
    input:focus,
    textarea:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.8) !important;
        outline: none !important;
    }
    
    /* ========================================= */
    /* SELECTBOX - Multiple Selector Strategy */
    /* ========================================= */
    
    [data-baseweb="select"],
    [data-baseweb="select"] > div,
    div[role="combobox"],
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 0 6px rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        transition: all 0.4s ease-in-out !important;
    }
    
    [data-baseweb="select"]:hover > div,
    div[role="combobox"]:hover {
        border-color: #FFD700 !important;
        box-shadow: 0 0 18px rgba(255, 215, 0, 0.6) !important;
        transform: scale(1.015) !important;
    }
    
    [data-baseweb="select"]:focus-within > div,
    div[role="combobox"]:focus-within {
        border-color: #FFD700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.7) !important;
    }
    
    /* Remove red error borders */
    [data-baseweb="select"][aria-invalid="true"] > div {
        border-color: rgba(56, 189, 248, 0.6) !important;
    }
    
    /* ========================================= */
    /* FILE UPLOADER - Deep Nesting Coverage */
    /* ========================================= */
    
    .stFileUploader,
    div[data-testid="stFileUploader"],
    section[data-testid="stFileUploadDropzone"],
    .stFileUploader > div,
    div[data-testid="stFileUploader"] > div {
        background: rgba(30, 58, 138, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover,
    div[data-testid="stFileUploader"]:hover {
        box-shadow: 0 0 22px rgba(255, 215, 0, 0.7) !important;
        border-color: #FFD700 !important;
    }
    
    .stFileUploader label,
    div[data-testid="stFileUploader"] label {
        color: #FFD700 !important;
        font-weight: 600 !important;
    }
    
    /* ========================================= */
    /* SIDEBAR - Complete Override */
    /* ========================================= */
    
    section[data-testid="stSidebar"],
    .css-1d391kg,
    [data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #0f172a, #1e3a8a) !important;
    }
    
    /* Sidebar inputs */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="password"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        padding: 8px 10px !important;
    }
    
    section[data-testid="stSidebar"] input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.9) !important;
        outline: none !important;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #1e3a8a, #2563eb) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1e3a8a !important;
        box-shadow: 0 0 16px rgba(255, 215, 0, 0.8) !important;
    }
    
    /* ========================================= */
    /* RADIO BUTTONS - Sidebar Specific */
    /* ========================================= */
    
    section[data-testid="stSidebar"] .stRadio > label {
        color: #FFD700 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }
    
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 0.5rem !important;
        color: #e5e7eb !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.6) !important;
    }
    
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        font-weight: 700 !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.8) !important;
    }
    
    /* ========================================= */
    /* TABS - Enhanced Styling */
    /* ========================================= */
    
    .stTabs [role="tab"],
    button[role="tab"] {
        color: #FFD700 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stTabs [role="tab"]:hover {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #fff !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.7) !important;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700, #facc15) !important;
        color: #1E3A8A !important;
        box-shadow: 0 0 24px rgba(255,215,0,0.9) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Hide tab underline */
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs div[role="tablist"] > div:last-child {
        background: transparent !important;
        height: 0 !important;
    }
    
    .stTabs [role="tablist"] {
        border-bottom: none !important;
    }
    
    /* ========================================= */
    /* ALERTS - Icon Enhancement */
    /* ========================================= */
    
    @keyframes pulseGlow {
        0% { text-shadow: 0 0 6px rgba(56,189,248,0.6); }
        50% { text-shadow: 0 0 16px rgba(255,215,0,0.9); }
        100% { text-shadow: 0 0 6px rgba(56,189,248,0.6); }
    }
    
    .stAlert[data-baseweb="notification"] {
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s ease !important;
    }
    
    .stAlert[kind="success"],
    .stAlert[data-baseweb="notification"][kind="success"] {
        background: rgba(255, 215, 0, 0.15) !important;
        border-left: 4px solid #FFD700 !important;
        color: #FFD700 !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.25) !important;
    }
    
    .stAlert[kind="error"],
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: rgba(220, 38, 38, 0.15) !important;
        border-left: 4px solid #DC2626 !important;
        color: #f87171 !important;
        box-shadow: 0 0 20px rgba(220,38,38,0.25) !important;
    }
    
    .stAlert[kind="warning"],
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: rgba(251, 191, 36, 0.15) !important;
        border-left: 4px solid #fbbf24 !important;
        color: #facc15 !important;
        box-shadow: 0 0 20px rgba(251,191,36,0.25) !important;
    }
    
    .stAlert[kind="info"],
    .stAlert[data-baseweb="notification"][kind="info"] {
        background: rgba(56, 189, 248, 0.15) !important;
        border-left: 4px solid #38BDF8 !important;
        color: #38BDF8 !important;
        box-shadow: 0 0 20px rgba(56,189,248,0.25) !important;
    }
    
    /* ========================================= */
    /* TABLES - Enhanced Styling */
    /* ========================================= */
    
    .stTable table,
    table {
        border-collapse: collapse !important;
        width: 100% !important;
        border: 1px solid rgba(56,189,248,0.4) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 0 18px rgba(56,189,248,0.3) !important;
    }
    
    .stTable th,
    table th {
        background: linear-gradient(135deg, #38BDF8, #1E3A8A) !important;
        color: #FFD700 !important;
        text-align: center !important;
        padding: 10px !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #FFD700 !important;
    }
    
    .stTable td,
    table td {
        padding: 8px 10px !important;
        text-align: center !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #f1f5f9 !important;
    }
    
    .stTable tr:nth-child(even) td,
    table tr:nth-child(even) td {
        background: rgba(56,189,248,0.08) !important;
    }
    
    .stTable tr:hover td,
    table tr:hover td {
        background: rgba(255, 215, 0, 0.12) !important;
        color: #FFD700 !important;
    }
    
    /* ========================================= */
    /* METRIC CARDS */
    /* ========================================= */
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        text-align: center !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s ease !important;
    }
    
    .metric-card:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
    }
    
    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #FFD700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-label {
        font-size: 0.95rem !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 400 !important;
    }
    
    /* ========================================= */
    /* HIDE STREAMLIT BRANDING */
    /* ========================================= */
    
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* ========================================= */
    /* HYPERLINKS */
    /* ========================================= */
    
    a, a:link, a:visited {
        color: #38BDF8 !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: #FFD700 !important;
        text-shadow: 0 0 8px rgba(255,215,0,0.7) !important;
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
    
    if theme == "Dark":
        wm_color = colors.Color(1, 1, 1, alpha=0.08)
    else:
        wm_color = colors.Color(0.1, 0.2, 0.5, alpha=0.08)
    
    if logo_path and os.path.exists(logo_path):
        from reportlab.lib.utils import ImageReader
        logo = ImageReader(logo_path)
        canvas_obj.translate(150, 250)
        canvas_obj.rotate(30)
        canvas_obj.drawImage(logo, 0, 0, width=300, height=300, mask='auto')
    else:
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
        
        if theme == "Dark":
            text_color_main = colors.HexColor("#F8FAFC")
            title_color = colors.HexColor("#FFD700")
            heading_color = colors.HexColor("#38BDF8")
            accent_color = colors.HexColor("#FFD700")
        else:
            text_color_main = colors.HexColor("#1A365D")
            title_color = colors.HexColor("#1E3A8A")
            heading_color = colors.HexColor("#38BDF8")
            accent_color = colors.HexColor("#FFD700")
        
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
            "Elevating Expertise into Professional Impact — Powered by PyStatR+",
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
                
                image_key = f"{key}_images"
                if kwargs.get(image_key):
                    img_temp_files = add_images_to_story(story, kwargs[image_key])
                    temp_files.extend(img_temp_files)
                
                story.append(Spacer(1, 20))
        
        story.append(PageBreak())
        story.append(Spacer(1, 200))
        story.append(divider)
        story.append(Spacer(1, 30))
        
        closing_text = Paragraph(
            "Thank you for reviewing this portfolio.<br/>For inquiries, collaborations, or consulting engagements, please contact your PyStatR+ consultant.",
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
            "Elevating Expertise into Professional Impact — Powered by PyStatR+",
            ParagraphStyle(
                "ClosingFooter",
                fontName="Helvetica-Oblique",
                fontSize=10,
                textColor=divider_color,
                alignment=TA_CENTER,
                spaceBefore=20
            )
        )
        story.append(closing_footer)
        
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

def render_password_panel(admin_settings):
    st.sidebar.markdown("### Password Management")

    if "password_overrides" not in st.session_state:
        st.session_state.password_overrides = {}

    if "password_overrides" in admin_settings:
        for user, info in admin_settings["password_overrides"].items():
            try:
                ts = datetime.fromisoformat(info["timestamp"])
                st.session_state.password_overrides[user] = {
                    "password": info["password"],
                    "timestamp": ts
                }
            except:
                continue

    users = list(st.secrets["users"].keys())
    users = [u for u in users if u.lower() != "alierwai"]

    reset_user = st.sidebar.selectbox("Select user", users)
    new_pass = st.sidebar.text_input("New password", type="password")

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
        st.sidebar.success(f"Password for {reset_user} updated")

    if st.sidebar.button("Reset to Default Passwords"):
        st.session_state.password_overrides.clear()
        admin_settings.pop("password_overrides", None)
        save_admin_settings(admin_settings)
        st.sidebar.info("All overrides cleared")

    expiry_hours = admin_settings.get("override_expiry_hours", 24)
    st.sidebar.markdown("#### Override Expiry")
    expiry_hours = st.sidebar.slider("Expiry Time (hours)", 1, 72, expiry_hours, 1)

    if expiry_hours != admin_settings.get("override_expiry_hours", 24):
        admin_settings["override_expiry_hours"] = expiry_hours
        save_admin_settings(admin_settings)
        st.sidebar.success(f"Override expiry updated to {expiry_hours} hours")

    MAX_AGE = expiry_hours * 3600

    if st.session_state.password_overrides:
        st.sidebar.markdown("#### Active Overrides")
        now = datetime.now()
        for user, info in list(st.session_state.password_overrides.items()):
            age = (now - info["timestamp"]).total_seconds()
            remaining = MAX_AGE - age
            if remaining > 0:
                hrs = int(remaining // 3600)
                mins = int((remaining % 3600) // 60)
                st.sidebar.write(
                    f"**{user}** — expires in {hrs}h {mins}m "
                    f"(set {info['timestamp'].strftime('%Y-%m-%d %H:%M')})"
                )
            else:
                del st.session_state.password_overrides[user]
                if "password_overrides" in admin_settings and user in admin_settings["password_overrides"]:
                    del admin_settings["password_overrides"][user]
                    save_admin_settings(admin_settings)
                st.sidebar.warning(f"Override for {user} expired and was reset")

def main():
    st.set_page_config(
        page_title="AI Consulting Portfolio Builder",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_css()
    
    admin_settings = load_admin_settings()
    check_session_timeout()
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">Portfolio Builder Login</h1>
            <p class="subtitle">Access your professional consulting portfolio tools</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Secure Access", use_container_width=True):
                user = check_credentials(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = user["role"]
                    st.session_state.user_name = user["name"]
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return
    
    if st.sidebar.button("End Session"):
        st.session_state.clear()
        st.rerun()
    
    st.sidebar.success(f"Welcome **{st.session_state.user_name}** ({st.session_state.user_role.title()})")
    
    if st.session_state.user_role == "admin":
        st.sidebar.markdown("### Admin Controls")
        render_password_panel(admin_settings)

        client_pdf_theme = st.sidebar.radio(
            "Default PDF Theme for All Clients",
            ["Light", "Dark"],
            index=0 if admin_settings["client_pdf_theme"] == "Light" else 1
        )
        
        if client_pdf_theme != admin_settings["client_pdf_theme"]:
            admin_settings["client_pdf_theme"] = client_pdf_theme
            save_admin_settings(admin_settings)
            st.sidebar.success(f"Client theme updated to **{client_pdf_theme}**")
        
        presets = load_presets()
        
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">AI Consulting Portfolio Builder</h1>
            <p class="subtitle">Turn your expertise into client-ready, professional portfolios powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        create_metric_cards()
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Brand Identity Workshop",
            "Strategic Content Composer",
            "Interactive Portfolio Preview",
            "Professional Export Hub"
        ])
        
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = {}
        
        with tab1:
            st.markdown('<div class="client-container">', unsafe_allow_html=True)
            st.markdown("## Branding Studio")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                preset_names = list(presets.keys())
                selected_preset = st.selectbox(
                    "Brand Preset Library",
                    ["Create New"] + preset_names
                )
            
            with col2:
                if selected_preset != "Create New" and selected_preset in presets:
                    st.success(f"Active: {selected_preset}")
                    branding = presets[selected_preset]
                else:
                    branding = {
                        "name": "AI Consultant Pro",
                        "brand_color": "#1E3A8A",
                        "font_choice": "Helvetica",
                        "logo": None,
                        "pdf_theme": "Light"
                    }
            
            col1, col2 = st.columns(2)
            
            with col1:
                name_input = st.text_input(
                    "Professional Identity",
                    value=branding.get("name", "")
                )
                
                brand_color = st.color_picker(
                    "Signature Brand Color",
                    value=branding.get("brand_color", "#1E3A8A")
                )
            
            with col2:
                font_choice = st.selectbox(
                    "Typography",
                    ["Helvetica", "Times-Roman", "Courier"],
                    index=["Helvetica", "Times-Roman", "Courier"].index(
                        branding.get("font_choice", "Helvetica")
                    )
                )
                
                pdf_theme = st.radio(
                    "Document Theme",
                    ["Light", "Dark"],
                    index=0 if branding.get("pdf_theme", "Light") == "Light" else 1,
                    horizontal=True
                )
            
            st.markdown("### Professional Logo")
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
            
            st.markdown("### Brand Preset Manager")
            preset_name_input = st.text_input(
                "Preset Collection Name",
                value=selected_preset if selected_preset != "Create New" else ""
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Save Branding Profile", use_container_width=True):
                    if preset_name_input.strip():
                        presets[preset_name_input] = {
                            "name": name_input,
                            "brand_color": brand_color,
                            "font_choice": font_choice,
                            "logo": cover_logo,
                            "pdf_theme": pdf_theme
                        }
                        save_presets(presets)
                        st.success(f"Brand preset '{preset_name_input}' saved")
                        st.rerun()
                    else:
                        st.error("Please enter a preset name")
            
            with col2:
                if st.button("Delete Branding Profile", use_container_width=True):
                    if selected_preset in presets:
                        del presets[selected_preset]
                        save_presets(presets)
                        st.success(f"Preset '{selected_preset}' removed")
                        st.rerun()
            
            with col3:
                if st.button("Reload Preset Library", use_container_width=True):
                    st.rerun()
            
            st.session_state.portfolio_data.update({
                "name": name_input,
                "brand_color": brand_color,
                "font_choice": font_choice,
                "logo": cover_logo,
                "pdf_theme": pdf_theme
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="client-container">', unsafe_allow_html=True)
            st.markdown("## Content Builder")
            
            st.markdown("### Project Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                project_title = st.text_input(
                    "Portfolio Title",
                    value="Generative AI Consulting Training Program"
                )
            
            with col2:
                date = st.date_input("Project Date", datetime.today())
            
            sections = [
                ("Executive Summary", "exec_summary"),
                ("Strategic Opportunities", "opportunities"),
                ("Risk Assessment", "risks"),
                ("Scenario Analysis", "scenarios"),
                ("Professional Insights", "reflection"),
                ("Design Case Study", "logo_text")
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
                        st.success(f"{len(content_data[f'{key}_images'])} image(s)")
            
            st.session_state.portfolio_data.update(content_data)
            st.session_state.portfolio_data.update({
                "project_title": project_title,
                "date": date
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="client-container">', unsafe_allow_html=True)
            st.markdown("## Live Preview")
            
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
            st.markdown('<div class="client-container">', unsafe_allow_html=True)
            st.markdown("## PDF Export Studio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                export_theme = st.radio(
                    "Export Theme",
                    ["Light", "Dark"],
                    horizontal=True
                )
            
            with col2:
                st.info("**Pro Tips:**\n\n• Use high-res images\n• Keep content concise\n• Preview before export")
            
            if st.button("Generate Professional Portfolio", use_container_width=True):
                try:
                    with st.spinner("Creating your portfolio..."):
                        output_file = "admin_portfolio.pdf"
                        
                        pdf_data = st.session_state.portfolio_data.copy()
                        success = generate_pdf(output_file, theme=export_theme, **pdf_data)
                        
                        if success:
                            with open(output_file, "rb") as f:
                                pdf_bytes = f.read()
                            
                            st.success("Portfolio generated successfully")
                            st.download_button(
                                "Download Your Portfolio",
                                pdf_bytes,
                                file_name=f"Admin_Portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            os.remove(output_file)
                        
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.user_role == "client":
        st.sidebar.markdown("### Client Portal")
        st.sidebar.info("Your portfolio uses **PyStatR+ branding** automatically")
        
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">Client Portfolio Portal</h1>
            <p class="subtitle">Build a future-ready consulting portfolio with PyStatR+ branding and AI-driven design</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### PyStatR+ Branding (Locked)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Brand Color:** Deep Blue (#1E3A8A)")
            st.markdown('<div style="width: 100%; height: 30px; background: #1E3A8A; border-radius: 5px;"></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Accent Color:** Bright Yellow (#FFD700)")
            st.markdown('<div style="width: 100%; height: 30px; background: #FFD700; border-radius: 5px;"></div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown("**Typography:** Helvetica")
            st.markdown('<div style="font-family: Helvetica; font-weight: 600; color: #1E3A8A;">Sample Text</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### Project Information")
        
        col1, col2 = st.columns(2)
        with col1:
            project_title = st.text_input("Project Title", "Consulting Engagement")
        with col2:
            date = st.date_input("Date")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### Portfolio Content")
        
        exec_summary = st.text_area("Executive Summary", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            opportunities = st.text_area("Strategic Opportunities", height=120)
        with col2:
            risks = st.text_area("Risk Assessment", height=120)
        
        scenarios = st.text_area("Scenario Analysis", 
                                value="Primary Strategy | High Investment | 35% ROI | Moderate Risk | Recommended\nAlternative Approach | Medium Investment | 20% ROI | Lower Risk | Consider",
                                height=100)
        
        reflection = st.text_area("Professional Insights", height=150)
        logo_text = st.text_area("Design Case Study", height=150)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### Visual Assets (Optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            exec_images = st.file_uploader("Executive Summary Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            or_images = st.file_uploader("Opportunities & Risks Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            scen_images = st.file_uploader("Scenario Analysis Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        with col2:
            reflection_images = st.file_uploader("Professional Insights Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            logo_images = st.file_uploader("Design Case Study Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="client-container">', unsafe_allow_html=True)
        st.markdown("### Preview & Export")
        
        client_pdf_theme = admin_settings.get("client_pdf_theme", "Light")
        st.info(f"Your portfolio will automatically use **PyStatR+ branding** with **{client_pdf_theme} theme**")
        
        if st.button("Generate Portfolio PDF", use_container_width=True):
            try:
                with st.spinner("Creating your professional portfolio..."):
                    output_file = "client_portfolio.pdf"
                    
                    client_data = {
                        "project_title": project_title,
                        "date": date,
                        "name": f"Client Portfolio - {st.session_state.user_name}",
                        "brand_color": "#1E3A8A",
                        "font_choice": "Helvetica",
                        "exec_summary": exec_summary,
                        "opportunities": opportunities,
                        "risks": risks,
                        "scenarios": scenarios,
                        "reflection": reflection,
                        "logo_text": logo_text,
                        "exec_summary_images": exec_images,
                        "opportunities_images": or_images,
                        "risks_images": or_images,
                        "scenarios_images": scen_images,
                        "reflection_images": reflection_images,
                        "logo_text_images": logo_images
                    }
                    
                    success = generate_pdf(output_file, theme=client_pdf_theme, **client_data)
                    
                    if success:
                        with open(output_file, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.success("Portfolio generated successfully")
                        st.download_button(
                            "Download Your Portfolio",
                            pdf_bytes,
                            file_name=f"Client_Portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        os.remove(output_file)
                    
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.7);">
        <p><strong>AI Consulting Portfolio Builder</strong> — Elevating expertise into professional impact</p>
        <p>Powered by <strong>PyStatRPlus</strong> | Future-ready design meets advanced intelligence</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()