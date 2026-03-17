import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db import init_db, get_all_dumps, log_alert, get_alerts_log
from utils.alerts import send_all_alerts, send_whatsapp_alert, send_email_alert
from utils.ui import render_topnav, close_main, page_header

st.set_page_config(page_title="Alert Centre", page_icon="🚨", layout="wide", initial_sidebar_state="collapsed")
render_topnav("alerts")
init_db()
df = get_all_dumps()

page_header("🚨", "Alert Centre", "Send WhatsApp + Email alerts to municipal officers instantly")

with st.expander("⚙️ Setup credentials — Twilio + Gmail"):
    st.code("""# utils/alerts.py mein directly daalo:
TWILIO_SID   = "ACf884b95a3bab3eeea1f44a1065eff65d"
TWILIO_AUTH  = "24424fac40a64b39ab0ce83b5691fc6b"
TWILIO_FROM  = "whatsapp:+14155238886"
ALERT_PHONE  = "whatsapp:+918572831710"
EMAIL_USER   = "your@gmail.com"
EMAIL_PASS   = "16char_app_password" """, language="python")

col_send, col_rules = st.columns([1.4, 0.6])
with col_send:
    st.markdown("#### Send alert for a dump site")
    open_dumps = df[df["status"]=="Open"]
    if len(open_dumps) == 0:
        st.info("No open dump sites right now.")
    else:
        options = [f"#{int(r['id'])} — {r['ward']} ({r['severity']})" for _, r in open_dumps.iterrows()]
        selected = st.selectbox("Select dump site", options)
        idx = int(selected.split("#")[1].split(" ")[0]) - 1
        row = open_dumps.iloc[min(idx, len(open_dumps)-1)]
        c1, c2 = st.columns(2)
        with c1:
            clr = "#ef4444" if row["severity"]=="High" else "#f59e0b" if row["severity"]=="Medium" else "#10b981"
            st.markdown(f"""
            <div style='background:#f8fafc;border-radius:12px;padding:16px;border:1px solid #e2e8f0'>
                <div style='font-size:15px;font-weight:700;color:#0f172a;margin-bottom:10px'>{row['ward']}</div>
                <div style='font-size:12px;color:#64748b;line-height:2.2'>
                    <span style='color:{clr};font-weight:600'>● {row['severity']}</span><br>
                    📐 {int(row['area_sqm'])} sq.m<br>
                    🦟 {row['disease_risk']} risk<br>
                    📍 {row['lat']:.4f}, {row['lng']:.4f}
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            alert_type = st.radio("Alert channel", ["WhatsApp + Email","WhatsApp only","Email only"])
            st.text_area("Extra note (optional)", height=80, key="note")
        if st.button("📤 Send Alert Now", use_container_width=True, type="primary"):
            dump_info = {"ward":row["ward"],"severity":row["severity"],
                         "area_sqm":int(row["area_sqm"]),"disease_risk":row["disease_risk"],
                         "lat":row["lat"],"lng":row["lng"]}
            with st.spinner("Sending..."):
                if alert_type == "WhatsApp + Email": results = send_all_alerts(dump_info)
                elif alert_type == "WhatsApp only":
                    ok, msg = send_whatsapp_alert(dump_info)
                    results = [{"channel":"WhatsApp","success":ok,"message":msg}]
                else:
                    ok, msg = send_email_alert(dump_info)
                    results = [{"channel":"Email","success":ok,"message":msg}]
            for r in results:
                if r["success"]:
                    st.markdown(f"<div class='result-good'>✅ {r['channel']}: {r['message']}</div>", unsafe_allow_html=True)
                    log_alert(int(row["id"]), r["channel"], "Officer", r["message"])
                else:
                    st.markdown(f"<div class='result-bad'>❌ {r['channel']}: {r['message']}</div>", unsafe_allow_html=True)

with col_rules:
    st.markdown("#### Alert levels")
    for bg, bl, bc, emoji, title, sub in [
        ("#fffbeb","#f59e0b","#92400e","🟡","Watch — Score > 40","Email to health officer"),
        ("#fff7ed","#f97316","#7c2d12","🟠","Warning — Score > 65","Email + WhatsApp to CMO"),
        ("#fef2f2","#ef4444","#991b1b","🔴","Emergency — Score > 80","SMS blast to all officers"),
    ]:
        st.markdown(f"<div style='background:{bg};border-left:4px solid {bl};border-radius:8px;padding:12px;margin-bottom:8px;font-size:12px;color:{bc}'>{emoji} <b>{title}</b><br>{sub}</div>", unsafe_allow_html=True)
    high_open = df[(df["severity"]=="High")&(df["status"]=="Open")]
    st.metric("Critical open dumps", len(high_open))
    if len(high_open) > 0: st.error(f"🔴 {len(high_open)} need immediate action!")
    else: st.success("✅ All clear")

st.markdown("<div class='section-hdr'>📜 Alert History</div>", unsafe_allow_html=True)
log_df = get_alerts_log()
if len(log_df) == 0:
    st.info("No alerts sent yet.")
else:
    st.dataframe(log_df[["alert_type","sent_to","message","sent_at"]].rename(columns={
        "alert_type":"Channel","sent_to":"Sent To","message":"Result","sent_at":"Time"
    }), use_container_width=True, height=200, hide_index=True)

close_main()
