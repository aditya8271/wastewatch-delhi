import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.db import init_db, get_all_dumps
from utils.ui import render_topnav, close_main

st.set_page_config(
    page_title="Delhi Waste Detection System",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}
[data-testid="stSidebar"]{display:none!important}
[data-testid="collapsedControl"]{display:none!important}
.kpi-card{background:white;border-radius:14px;padding:18px 20px;border:1px solid #e2e8f0;margin-bottom:4px}
.kpi-val{font-size:30px;font-weight:700;color:#0f172a;line-height:1.1}
.kpi-lbl{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-top:5px}
.kpi-delta{font-size:11px;margin-top:6px;font-weight:500}
.kpi-red{border-top:4px solid #ef4444}
.kpi-amber{border-top:4px solid #f59e0b}
.kpi-green{border-top:4px solid #10b981}
.kpi-blue{border-top:4px solid #3b82f6}
.kpi-purple{border-top:4px solid #8b5cf6}
.ward-card{background:white;border-radius:12px;padding:14px;border:1px solid #e2e8f0;margin-bottom:8px}
.section-hdr{font-size:15px;font-weight:600;color:#0f172a;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid #f1f5f9}
.alert-bar{background:#fef2f2;border:1px solid #fecaca;border-left:4px solid #ef4444;border-radius:10px;padding:12px 18px;margin-bottom:20px;font-size:13px;color:#991b1b}
</style>
""", unsafe_allow_html=True)

init_db()
df = get_all_dumps()

total      = len(df)
high       = len(df[df["severity"]=="High"])
cleaned    = len(df[df["status"]=="Cleaned"])
open_      = len(df[df["status"]=="Open"])
score      = max(0, 100 - int((high/total)*60 + (open_/total)*40)) if total else 100
total_area = int(df["area_sqm"].sum())

# ── Top Nav ────────────────────────────────────────────────────────────────────
render_topnav("dashboard")

# ── Header Banner ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:linear-gradient(135deg,#0a0f1e 0%,#1a2744 60%,#0d2137 100%);
     border-radius:16px;padding:22px 28px;margin-bottom:20px;
     display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px'>
    <div>
        <div style='font-size:20px;font-weight:700;color:#fff'>Delhi Waste Detection System</div>
        <div style='font-size:12px;color:#64748b;margin-top:3px'>Satellite-powered · AI Detection · Real-time Alerts</div>
    </div>
    <div style='display:flex;gap:8px;flex-wrap:wrap'>
        <div style='background:#0d2137;border:1px solid #1e3a5f;border-radius:10px;padding:8px 16px;text-align:center'>
            <div style='font-size:18px;font-weight:700;color:#22c55e'>{score}</div>
            <div style='font-size:10px;color:#64748b'>City Score</div>
        </div>
        <div style='background:#0d2137;border:1px solid #1e3a5f;border-radius:10px;padding:8px 16px;text-align:center'>
            <div style='font-size:18px;font-weight:700;color:#ef4444'>{high}</div>
            <div style='font-size:10px;color:#64748b'>Critical</div>
        </div>
        <div style='background:#0d2137;border:1px solid #1e3a5f;border-radius:10px;padding:8px 16px;text-align:center'>
            <div style='font-size:18px;font-weight:700;color:#3b82f6'>{total}</div>
            <div style='font-size:10px;color:#64748b'>Total Sites</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if high > 0:
    st.markdown(f"<div class='alert-bar'>🚨 <strong>Emergency Alert:</strong> {high} high-severity dump sites require immediate action across Delhi</div>", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
for col,cls,val,lbl,delta,clr in [
    (k1,"kpi-blue",   total,      "Total Dumps",    "↑ 3 this week", "#3b82f6"),
    (k2,"kpi-red",    high,       "High Severity",  "Needs action",  "#ef4444"),
    (k3,"kpi-amber",  open_,      "Open Cases",     "Unresolved",    "#f59e0b"),
    (k4,"kpi-green",  cleaned,    "Cleaned",        "↑ This month",  "#10b981"),
    (k5,"kpi-purple", total_area, "Total Area (m²)","Contaminated",  "#8b5cf6"),
]:
    with col:
        st.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-val'>{val:,}</div>
            <div class='kpi-lbl'>{lbl}</div>
            <div class='kpi-delta' style='color:{clr}'>{delta}</div>
        </div>""", unsafe_allow_html=True)

# ── Charts ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-hdr'>📊 Analytics Overview</div>", unsafe_allow_html=True)
c1,c2,c3 = st.columns([1.3,1,0.9])

with c1:
    ward_df = df.groupby("ward").agg(
        total=("id","count"),
        high=("severity", lambda x:(x=="High").sum()),
    ).reset_index().sort_values("high",ascending=False).head(8)
    fig1 = go.Figure(go.Bar(
        x=ward_df["ward"], y=ward_df["total"],
        marker=dict(color=ward_df["high"],colorscale=[[0,"#3b82f6"],[0.5,"#f59e0b"],[1,"#ef4444"]],showscale=False),
        hovertemplate="<b>%{x}</b><br>Dumps: %{y}<extra></extra>",
    ))
    fig1.update_layout(title=dict(text="Worst wards by dump count",font=dict(size=13,color="#0f172a"),x=0),
        height=280,margin=dict(l=0,r=0,t=36,b=70),paper_bgcolor="white",plot_bgcolor="white",
        xaxis=dict(tickangle=-40,tickfont=dict(size=9),showgrid=False),
        yaxis=dict(showgrid=True,gridcolor="#f1f5f9"))
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    status_df = df["status"].value_counts().reset_index()
    status_df.columns = ["Status","Count"]
    fig2 = go.Figure(go.Pie(
        labels=status_df["Status"],values=status_df["Count"],hole=0.55,
        marker=dict(colors=["#ef4444","#f59e0b","#10b981"],line=dict(color="white",width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} sites<extra></extra>",
    ))
    fig2.add_annotation(text=f"<b>{total}</b><br>Total",x=0.5,y=0.5,showarrow=False,font=dict(size=15,color="#0f172a"))
    fig2.update_layout(title=dict(text="Status breakdown",font=dict(size=13,color="#0f172a"),x=0),
        height=280,margin=dict(l=0,r=0,t=36,b=0),paper_bgcolor="white",showlegend=True,
        legend=dict(font=dict(size=11),orientation="h",y=-0.08))
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    dis_df = df[df["disease_risk"]!="Low"]["disease_risk"].value_counts().reset_index()
    dis_df.columns = ["Disease","Count"]
    dcolors = {"Dengue":"#ef4444","Cholera":"#f59e0b","Malaria":"#8b5cf6","Typhoid":"#06b6d4"}
    fig3 = go.Figure(go.Bar(
        x=dis_df["Count"],y=dis_df["Disease"],orientation="h",
        marker_color=[dcolors.get(d,"#94a3b8") for d in dis_df["Disease"]],
        hovertemplate="<b>%{y}</b><br>%{x} zones<extra></extra>",
    ))
    fig3.update_layout(title=dict(text="Disease risk zones",font=dict(size=13,color="#0f172a"),x=0),
        height=280,margin=dict(l=0,r=0,t=36,b=0),paper_bgcolor="white",plot_bgcolor="white",
        xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
    st.plotly_chart(fig3, use_container_width=True)

# ── Ward Leaderboard ───────────────────────────────────────────────────────────
st.markdown("<div class='section-hdr'>🏆 Ward Cleanliness Leaderboard</div>", unsafe_allow_html=True)
ws = df.groupby("ward").agg(
    total=("id","count"),
    high=("severity",lambda x:(x=="High").sum()),
    cleaned=("status",lambda x:(x=="Cleaned").sum()),
).reset_index()
ws["score"] = (100-((ws["high"]/ws["total"])*60+((ws["total"]-ws["cleaned"])/ws["total"])*40)).clip(0,100).astype(int)
ws = ws.sort_values("score",ascending=False).reset_index(drop=True)

lcols = st.columns(4)
for i,(_,row) in enumerate(ws.head(8).iterrows()):
    s = int(row["score"])
    color = "#10b981" if s>=70 else "#f59e0b" if s>=45 else "#ef4444"
    medal = ["🥇","🥈","🥉"][i] if i<3 else f"#{i+1}"
    with lcols[i%4]:
        st.markdown(f"""
        <div class='ward-card' style='border-top:3px solid {color}'>
            <div style='font-size:18px;margin-bottom:4px'>{medal}</div>
            <div style='font-size:12px;font-weight:600;color:#0f172a;margin-bottom:6px'>{row['ward']}</div>
            <div style='font-size:26px;font-weight:700;color:{color};line-height:1'>{s}</div>
            <div style='font-size:10px;color:#94a3b8'>/100</div>
        </div>""", unsafe_allow_html=True)

# ── Recent Table ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-hdr'>📍 Recent Dump Sites</div>", unsafe_allow_html=True)
st.dataframe(
    df.head(8)[["ward","severity","status","area_sqm","disease_risk","detected_by","date"]].rename(columns={
        "ward":"Ward","severity":"Severity","status":"Status","area_sqm":"Area (m²)",
        "disease_risk":"Disease Risk","detected_by":"Source","date":"Date"
    }),
    use_container_width=True, height=290, hide_index=True
)

close_main()
st.caption("WasteWatch AI · Sentinel-2 · Delhi Municipal Corporation")
