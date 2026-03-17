import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.risk import calculate_risk_score, get_alert_level, WARD_WASTE_SCORES
from utils.ui import render_topnav, close_main, page_header

st.set_page_config(page_title="Disease Risk", page_icon="🦟", layout="wide", initial_sidebar_state="collapsed")
render_topnav("disease")

page_header("🦟", "Disease Outbreak Risk Predictor", "Waste accumulation + weather → disease risk score per ward")

wc1, wc2, wc3 = st.columns(3)
with wc1: temp     = st.slider("Temperature (°C)", 10, 45, 32)
with wc2: rainfall = st.slider("Rainfall (mm, last 7 days)", 0, 200, 45)
with wc3: season   = st.selectbox("Season", ["Summer","Monsoon","Winter"])

st.markdown("<div class='section-hdr'>Ward risk analysis</div>", unsafe_allow_html=True)
selected_ward = st.selectbox("Select ward", list(WARD_WASTE_SCORES.keys()))
waste_score   = WARD_WASTE_SCORES[selected_ward]
risks = calculate_risk_score(waste_score, temp, rainfall, season)

st.markdown(f"**{selected_ward}** — Waste score: **{waste_score}/100**")
cols = st.columns(4)
for i, (disease, score) in enumerate(risks.items()):
    level, color = get_alert_level(score)
    with cols[i]:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            title={"text": disease, "font": {"size": 13}},
            gauge={"axis":{"range":[0,100]},"bar":{"color":color},
                   "steps":[{"range":[0,45],"color":"#f0fdf4"},
                             {"range":[45,70],"color":"#fffbeb"},
                             {"range":[70,100],"color":"#fef2f2"}]}
        ))
        fig.update_layout(height=200, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if level == "Emergency": st.error(f"🔴 {level}")
        elif level == "Warning":  st.warning(f"🟡 {level}")
        else:                     st.success(f"🟢 {level}")

st.markdown("<div class='section-hdr'>All wards — dengue risk overview</div>", unsafe_allow_html=True)
rows = []
for ward, wscore in WARD_WASTE_SCORES.items():
    r = calculate_risk_score(wscore, temp, rainfall, season)
    level, _ = get_alert_level(r["Dengue"])
    rows.append({"Ward":ward,"Waste Score":wscore,"Dengue Risk":r["Dengue"],
                 "Malaria Risk":r["Malaria"],"Cholera Risk":r["Cholera"],"Alert":level})
risk_df = pd.DataFrame(rows).sort_values("Dengue Risk", ascending=False)
risk_df.index = range(1, len(risk_df)+1)

fig_bar = px.bar(risk_df, x="Ward", y="Dengue Risk",
                 color="Dengue Risk", color_continuous_scale=["#10b981","#f59e0b","#ef4444"], height=300)
fig_bar.update_layout(margin=dict(l=0,r=0,t=10,b=0), xaxis_tickangle=-35,
                      paper_bgcolor="white", plot_bgcolor="white")
st.plotly_chart(fig_bar, use_container_width=True)
st.dataframe(risk_df, use_container_width=True, height=300, hide_index=False)

close_main()
