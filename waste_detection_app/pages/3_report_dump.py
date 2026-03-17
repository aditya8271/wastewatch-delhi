import streamlit as st
import sys, os
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db import init_db, add_dump
from utils.ndvi import run_model_inference
from utils.ui import render_topnav, close_main, page_header

st.set_page_config(page_title="Report a Dump", page_icon="📋", layout="wide", initial_sidebar_state="collapsed")
render_topnav("report")
init_db()

page_header("📋", "Report an Illegal Dump", "Submit a report — it appears on the live map instantly")

WARDS = ["Dharavi Colony","Seemapuri","Bhalswa","Okhla Phase 2","Jahangirpuri",
    "Sangam Vihar","Trilokpuri","Mangolpuri","Mustafabad","Badarpur",
    "Shahdara","Narela","Bawana","Dwarka Sector 23","Kondli",
    "Rohini Sector 3","Gokulpuri","Seelampur","Kirari Suleman Nagar","Tughlakabad"]

with st.form("report_form", clear_on_submit=True):
    st.markdown("#### Location details")
    c1, c2 = st.columns(2)
    with c1:
        ward     = st.selectbox("Ward *", WARDS)
        lat      = st.number_input("Latitude *",  value=28.6139, format="%.4f", step=0.0001)
    with c2:
        area_sqm = st.number_input("Estimated area (sq.m)", min_value=1, value=100)
        lng      = st.number_input("Longitude *", value=77.2090, format="%.4f", step=0.0001)
    st.markdown("#### Dump details")
    c3, c4 = st.columns(2)
    with c3:
        severity     = st.selectbox("Severity *", ["High","Medium","Low"])
        disease_risk = st.selectbox("Disease risk visible", ["Dengue","Cholera","Malaria","Typhoid","Low","Unknown"])
    with c4:
        report_date  = st.date_input("Date observed *", value=date.today())
        detected_by  = st.radio("Reported by", ["Citizen","Satellite"], horizontal=True)
    description = st.text_area("Description", placeholder="Type of waste, smell, water pooling, etc.")
    st.markdown("#### Photo evidence")
    photo = st.file_uploader("Upload photo (optional)", type=["jpg","jpeg","png"])
    if photo:
        col_p, col_r = st.columns(2)
        with col_p: st.image(photo, caption="Your photo", use_container_width=True)
        with col_r:
            with st.spinner("AI verifying..."):
                label, conf = run_model_inference(photo.read())
            if "detected" in label.lower() and "no" not in label.lower():
                st.markdown(f"<div class='result-bad'>🔴 {label} ({conf*100:.0f}%)</div>", unsafe_allow_html=True)
            elif "possible" in label.lower():
                st.markdown(f"<div class='result-warn'>🟡 {label} ({conf*100:.0f}%)</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='result-good'>🟢 {label} ({conf*100:.0f}%)</div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("📤 Submit Report", use_container_width=True, type="primary")

if submitted:
    photo_path = ""
    if photo:
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
        os.makedirs(save_dir, exist_ok=True)
        photo_path = os.path.join(save_dir, photo.name)
        with open(photo_path, "wb") as f: f.write(photo.getbuffer())
    add_dump(ward=ward, lat=lat, lng=lng, severity=severity, area_sqm=area_sqm,
             detected_by=detected_by, date=str(report_date), disease_risk=disease_risk,
             description=description, photo_path=photo_path)
    st.success("✅ Report submitted! Appears on live map now.")
    st.balloons()

close_main()
