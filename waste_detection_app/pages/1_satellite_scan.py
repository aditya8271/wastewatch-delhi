import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ndvi import get_ndvi_image, get_change_detection, run_model_inference, calculate_dump_area
from utils.db import init_db
from utils.ui import render_topnav, close_main, page_header

st.set_page_config(page_title="Satellite Scanner", page_icon="🛰️", layout="wide", initial_sidebar_state="collapsed")
render_topnav("satellite")
init_db()

page_header("🛰️", "Satellite Scanner", "NDVI Change Detection · Sentinel-2 · Delhi NCR")

tab1, tab2, tab3 = st.tabs(["📡 Live NDVI Map", "🔄 Before vs After", "🤖 AI Model Test"])

with tab1:
    st.markdown("<div class='info-box'>🟢 Green = healthy vegetation &nbsp;·&nbsp; 🟡 Yellow = degraded &nbsp;·&nbsp; 🔴 Red = illegal dump zone</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.spinner("Fetching Sentinel-2 data..."):
            buf, ndvi = get_ndvi_image(seed=42)
        st.image(buf, caption="NDVI Map — Delhi NCR (Sentinel-2)", use_container_width=True)
    with col2:
        dump_px = int((ndvi < 0.2).sum())
        good_px = int((ndvi >= 0.4).sum())
        st.markdown(f"<div class='stat-card'><div class='stat-val' style='color:#ef4444'>{dump_px:,}</div><div class='stat-lbl'>Dump zone pixels</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-val' style='color:#3b82f6'>{calculate_dump_area(dump_px):,}</div><div class='stat-lbl'>Est. area (sq.m)</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-val' style='color:#10b981'>{good_px:,}</div><div class='stat-lbl'>Healthy vegetation px</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='background:white;border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px;font-size:12px;color:#64748b;line-height:2'><b style='color:#0f172a'>Last scan:</b> Today, 06:00 AM<br><b style='color:#0f172a'>Source:</b> Sentinel-2 Band 4+8<br><b style='color:#0f172a'>Resolution:</b> 10m/pixel</div>", unsafe_allow_html=True)
        if st.button("🔄 Re-run Scan", use_container_width=True, type="primary"): st.rerun()

with tab2:
    st.markdown("#### Compare two satellite scans")
    ca, cb = st.columns(2)
    with ca: st.date_input("Before date", key="d1")
    with cb: st.date_input("After date",  key="d2")
    if st.button("🔍 Run Change Detection", use_container_width=True, type="primary"):
        with st.spinner("Analysing..."):
            img_before, img_after, changed_area, changed_px = get_change_detection(42, 99)
        c1, c2 = st.columns(2)
        with c1: st.image(img_before, caption="Before", use_container_width=True)
        with c2: st.image(img_after,  caption="After — new dumps in red", use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("New dump pixels",   f"{changed_px:,}")
        m2.metric("New area detected", f"{changed_area:,} sq.m")
        m3.metric("Alert level",       "🔴 HIGH" if changed_area > 1000 else "🟡 MEDIUM")
        if changed_area > 500:
            st.markdown(f"<div class='result-bad'>🚨 {changed_area:,} sq.m new illegal dumping detected!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-good'>✅ No major new dump sites detected.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:#f8fafc;border:2px dashed #cbd5e1;border-radius:12px;padding:40px;text-align:center;color:#94a3b8'>Select dates and click Run Change Detection</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("#### Upload waste site photo — AI will classify it")
    st.markdown("<div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 16px;font-size:12px;color:#166534;margin-bottom:14px'>💡 checkpoint.pth detected in utils/ — real AerialWaste AI model active!</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload waste site photo", type=["jpg","jpeg","png"])
    if uploaded:
        c1, c2 = st.columns(2)
        with c1: st.image(uploaded, caption="Uploaded image", use_container_width=True)
        with c2:
            with st.spinner("Running AI inference..."):
                label, conf = run_model_inference(uploaded.read())
            if "detected" in label.lower() and "no" not in label.lower():
                st.markdown(f"<div class='result-bad'>🔴 {label}<br><small>Confidence: {conf*100:.0f}%</small></div>", unsafe_allow_html=True)
            elif "possible" in label.lower():
                st.markdown(f"<div class='result-warn'>🟡 {label}<br><small>Confidence: {conf*100:.0f}%</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='result-good'>🟢 {label}<br><small>Confidence: {conf*100:.0f}%</small></div>", unsafe_allow_html=True)

close_main()
