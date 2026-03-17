import streamlit as st
import folium
from streamlit_folium import st_folium
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db import init_db, get_all_dumps
from utils.ui import render_topnav, close_main, page_header

st.set_page_config(page_title="Dump Map", page_icon="🗺️", layout="wide", initial_sidebar_state="collapsed")
render_topnav("map")
init_db()
df = get_all_dumps()

page_header("🗺️", "Live Dump Map — Delhi", "Real-time illegal dump sites · Click markers for details")

fc1, fc2, fc3 = st.columns(3)
with fc1: sev_f  = st.multiselect("Severity", ["High","Medium","Low"], default=["High","Medium","Low"])
with fc2: stat_f = st.multiselect("Status",   ["Open","Assigned","Cleaned"], default=["Open","Assigned"])
with fc3: src_f  = st.multiselect("Source",   ["Satellite","Citizen"], default=["Satellite","Citizen"])

filtered = df[df["severity"].isin(sev_f) & df["status"].isin(stat_f) & df["detected_by"].isin(src_f)]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Showing",       len(filtered))
m2.metric("High severity", len(filtered[filtered["severity"]=="High"]))
m3.metric("Open cases",    len(filtered[filtered["status"]=="Open"]))
m4.metric("Total area",    f"{int(filtered['area_sqm'].sum()):,} m²")

fmap = folium.Map(location=[28.6139, 77.2090], zoom_start=11, tiles="CartoDB positron")
color_map = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}

for _, row in filtered.iterrows():
    color  = color_map.get(row["severity"],"#3b82f6")
    sev_bg = {"High":"#fef2f2","Medium":"#fffbeb","Low":"#f0fdf4"}.get(row["severity"],"#f8fafc")
    sev_cl = {"High":"#dc2626","Medium":"#d97706","Low":"#16a34a"}.get(row["severity"],"#64748b")
    popup_html = f"""
    <div style='font-family:Inter,sans-serif;min-width:200px;padding:4px'>
      <div style='font-size:14px;font-weight:700;color:#0f172a;margin-bottom:8px'>{row['ward']}</div>
      <div style='background:{sev_bg};color:{sev_cl};display:inline-block;
           padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-bottom:10px'>{row['severity']}</div>
      <table style='width:100%;font-size:12px'>
        <tr><td style='color:#64748b;padding:2px 0'>Status</td><td style='font-weight:500'>{row['status']}</td></tr>
        <tr><td style='color:#64748b;padding:2px 0'>Area</td><td style='font-weight:500'>{int(row['area_sqm'])} m²</td></tr>
        <tr><td style='color:#64748b;padding:2px 0'>Disease</td><td style='color:#ef4444;font-weight:500'>{row['disease_risk']}</td></tr>
        <tr><td style='color:#64748b;padding:2px 0'>Source</td><td style='font-weight:500'>{row['detected_by']}</td></tr>
        <tr><td style='color:#64748b;padding:2px 0'>Date</td><td style='font-weight:500'>{row['date']}</td></tr>
      </table>
    </div>"""
    folium.CircleMarker(
        location=[row["lat"], row["lng"]],
        radius=12 if row["severity"]=="High" else 8 if row["severity"]=="Medium" else 5,
        color=color, fill=True, fill_color=color, fill_opacity=0.75,
        popup=folium.Popup(popup_html, max_width=230),
        tooltip=f"<b>{row['ward']}</b> — {row['severity']}"
    ).add_to(fmap)

st_folium(fmap, use_container_width=True, height=500, returned_objects=[])

st.markdown("<div class='section-hdr'>📋 Filtered Dump Sites</div>", unsafe_allow_html=True)
st.dataframe(
    filtered[["ward","severity","status","area_sqm","disease_risk","detected_by","date"]].rename(columns={
        "ward":"Ward","severity":"Severity","status":"Status","area_sqm":"Area (m²)",
        "disease_risk":"Disease Risk","detected_by":"Source","date":"Date"
    }),
    use_container_width=True, height=250, hide_index=True
)
close_main()
