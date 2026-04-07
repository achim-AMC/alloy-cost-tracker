"""
Aerospace Alloy Raw Material Cost Tracker — CLOUD VERSION
==========================================================
Uses Turso (libsql) cloud database instead of local SQLite.
Credentials stored in Streamlit secrets.
"""

import streamlit as st
import pandas as pd
import libsql_experimental as libsql
import math
import os
from datetime import date
import plotly.graph_objects as go

from config import ALLOYS, CONVERSION, MINOR_ELEMENT_DEFAULTS
from price_fetcher import fetch_all_prices
from cost_engine import calc_alloy_cost, calc_conversion_costs
from excel_export import generate_excel

# ── Smiths High Performance logo (base64 embedded) ───────────
_LOGO_SMITHS = "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"

COLORS = {'AA2040':'#C00000','AA2050':'#2F5496','AA2099':'#008000','AA2618':'#7030A0','AA7140':'#BF6900'}

st.set_page_config(page_title="Alloy Cost Tracker", page_icon="✈️", layout="wide")

# ── Config helper (supports Streamlit secrets AND environment variables) ──
def _get_secret(section, key, env_name):
    """Try st.secrets first, then environment variables."""
    try:
        return st.secrets[section][key]
    except Exception:
        return os.environ.get(env_name, "")

def check_password():
    """Simple password gate."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    pwd = st.text_input("🔒 Enter password to access the tracker:", type="password")
    if pwd:
        app_pwd = _get_secret("app", "password", "APP_PASSWORD")
        if pwd == app_pwd:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    return False

# ── Database (Turso cloud) ───────────────────────────────────
@st.cache_resource
def get_db():
    url = _get_secret("turso", "url", "TURSO_URL")
    token = _get_secret("turso", "token", "TURSO_TOKEN")
    conn = libsql.connect(url, auth_token=token)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            date TEXT PRIMARY KEY,
            al REAL, cu REAL, ag_oz REAL, zn REAL, ni REAL,
            li REAL, mg REAL, mn REAL, ti REAL, zr REAL, fe REAL, si REAL,
            source_notes TEXT
        )
    """)
    conn.commit()
    return conn

def save_prices(conn, dt, prices, notes=""):
    conn.execute("""
        INSERT OR REPLACE INTO price_history
        (date, al, cu, ag_oz, zn, ni, li, mg, mn, ti, zr, fe, si, source_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dt, prices['Al'], prices['Cu'], prices['Ag_oz'], prices['Zn'],
          prices['Ni'], prices['Li'], prices['Mg'], prices['Mn'],
          prices['Ti'], prices['Zr'], prices['Fe'], prices['Si'], notes))
    conn.commit()

def load_history(conn):
    rows = conn.execute("SELECT * FROM price_history ORDER BY date ASC").fetchall()
    cols = ['date','al','cu','ag_oz','zn','ni','li','mg','mn','ti','zr','fe','si','source_notes']
    return pd.DataFrame(rows, columns=cols)

# ── Build cost history ───────────────────────────────────────
def build_cost_df(df_hist, r_billet, r_total):
    rows = []
    for _, row in df_hist.iterrows():
        hp = {k: row[k.lower() if k != 'Ag_oz' else 'ag_oz'] for k in ['Al','Cu','Ag_oz','Zn','Ni','Li','Mg','Mn','Ti','Zr','Fe','Si']}
        entry = {'Date': row['date']}
        for key, alloy in ALLOYS.items():
            raw, ag_c, li_c = calc_alloy_cost(alloy['comp'], hp)
            billet, ext = calc_conversion_costs(raw, r_billet, r_total)
            entry[f"{alloy['name']} raw"] = round(raw, 2)
            entry[f"{alloy['name']} billet"] = round(billet, 2)
            entry[f"{alloy['name']} ext."] = round(ext, 2)
        entry['Ag ($/oz)'] = row['ag_oz']; entry['Al ($/t)'] = row['al']
        entry['Cu ($/t)'] = row['cu']; entry['Li ($/kg)'] = row['li']
        rows.append(entry)
    df = pd.DataFrame(rows); df['Date'] = pd.to_datetime(df['Date']); return df

# ── Plotly download config (high-res for PowerPoint) ─────────
PLOTLY_CONFIG = {
    'toImageButtonOptions': {
        'format': 'png',
        'height': 800,
        'width': 1400,
        'scale': 3,
    },
    'displaylogo': False,
}

# ── Chart helper ─────────────────────────────────────────────
def make_chart(df, cols, title, y_label, chart_key, dual_axis=False):
    y_max_val = float(df[cols].max().max()) if not dual_axis else float(df[cols[0]].max())
    with st.expander(f"⚙️ Axis Settings — {title}", expanded=False):
        c1,c2,c3,c4 = st.columns(4)
        with c1: ymin = st.number_input("Y min",value=0.0,step=1.0,key=f"{chart_key}_ymin")
        with c2: ymax = st.number_input("Y max",value=round(y_max_val*1.15,0),step=5.0,key=f"{chart_key}_ymax")
        with c3: xmin = st.date_input("From",value=df['Date'].min(),key=f"{chart_key}_xmin")
        with c4: xmax = st.date_input("To",value=df['Date'].max(),key=f"{chart_key}_xmax")
    fig = go.Figure()
    if dual_axis:
        fig.add_trace(go.Scatter(x=df['Date'],y=df[cols[0]],mode='lines+markers',name=cols[0],line=dict(color='#2F5496',width=2),marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=df['Date'],y=df[cols[1]],mode='lines+markers',name=cols[1],line=dict(color='#C00000',width=2),marker=dict(size=5),yaxis='y2'))
        fig.update_layout(
            yaxis=dict(title=cols[0],range=[ymin,ymax],title_font=dict(color='#2F5496'),tickfont=dict(color='#2F5496')),
            yaxis2=dict(title=cols[1],overlaying='y',side='right',range=[ymin,round(float(df[cols[1]].max())*1.15,-2)],title_font=dict(color='#C00000'),tickfont=dict(color='#C00000')),
            xaxis=dict(title="Date",range=[str(xmin),str(xmax)]),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="left",x=0),height=420,margin=dict(l=60,r=60,t=40,b=40),hovermode='x unified',
            plot_bgcolor='white',paper_bgcolor='white')
    else:
        for col in cols:
            color = '#0000FF' if col=='Ag ($/oz)' else ('#008000' if col=='Li ($/kg)' else '#333333')
            for akey,ac in COLORS.items():
                if ALLOYS[akey]['name'] in col: color=ac; break
            kw = dict(x=df['Date'],y=df[col],mode='lines+markers',name=col.replace(' raw','').replace(' billet','').replace(' ext.',''),line=dict(color=color,width=2),marker=dict(size=5))
            if col=='Ag ($/oz)': kw['fill']='tozeroy'; kw['fillcolor']='rgba(0,0,255,0.05)'
            elif col=='Li ($/kg)': kw['fill']='tozeroy'; kw['fillcolor']='rgba(0,128,0,0.05)'
            fig.add_trace(go.Scatter(**kw))
        fig.update_layout(yaxis=dict(title=y_label,range=[ymin,ymax]),xaxis=dict(title="Date",range=[str(xmin),str(xmax)]),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="left",x=0),height=420,margin=dict(l=60,r=20,t=40,b=40),hovermode='x unified',
            plot_bgcolor='white',paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.caption("💡 Click alloy names in legend to show/hide · Double-click to isolate one · 📷 Camera icon (top right) downloads high-res PNG for presentations")

def stage_tab(df_cost, suffix, label, y_label, chart_key):
    if df_cost.empty: st.info("Save at least 2 data points."); return
    all_cols = [c for c in df_cost.columns if suffix in c]
    alloy_names = [c.replace(suffix, '') for c in all_cols]
    selected = st.multiselect(f"Select alloys to display ({label})", options=alloy_names, default=alloy_names, key=f"{chart_key}_alloys")
    cols = [f"{a}{suffix}" for a in selected if f"{a}{suffix}" in all_cols]
    if not cols: st.warning("Select at least one alloy."); return
    st.write(f"#### {label} — Data Table (USD/kg)")
    disp = df_cost[['Date']+cols].copy(); disp['Date']=disp['Date'].dt.strftime('%Y-%m-%d')
    st.dataframe(disp.style.format({c:'${:.2f}' for c in cols}),use_container_width=True,hide_index=True)
    st.write(f"#### {label} — Trend Chart")
    make_chart(df_cost, cols, label, y_label, chart_key)

# ══════════════════════════════════════════════════════════════
def main():
    if not check_password():
        st.stop()

    conn = get_db()
    st.title("✈️ Aerospace Alloy Raw Material Cost Tracker")
    st.caption("5 alloys · Ingot → Billet → Extrusion / Forging · Daily price updates")

    with st.sidebar:
        st.markdown(f'''<div style="background:#fff;border-radius:8px;padding:10px 8px;margin-bottom:10px;border:0.5px solid #dddbd4;">
          <img src="data:image/png;base64,{_LOGO_SMITHS}" style="width:70%;max-height:80px;object-fit:contain;display:block;margin:0 auto;">
        </div>''', unsafe_allow_html=True)
        st.header("⚙️ Conversion Geometry")
        st.caption("All dimensions in mm.")
        st.markdown("**Stage 1: Cast Ingot → Lathed Billet**")
        d_cast = st.number_input("Cast ingot diameter (mm)",value=float(CONVERSION['d_cast']),step=1.0,format="%.0f",key="d_cast")
        l_cast = st.number_input("Cast ingot length (mm)",value=float(CONVERSION['l_cast']),step=10.0,format="%.0f",key="l_cast")
        d_lathed = st.number_input("Lathed billet diameter (mm)",value=float(CONVERSION['d_lathed']),step=1.0,format="%.0f",key="d_lathed")
        l_usable = st.number_input("Cropped billet length (mm)",value=float(CONVERSION['l_usable']),step=10.0,format="%.0f",key="l_usable")
        vol_cast = math.pi/4*d_cast**2*l_cast; vol_bil = math.pi/4*d_lathed**2*l_usable
        r_billet = vol_cast/vol_bil if vol_bil>0 else 1.0; y_billet = 1/r_billet*100
        st.metric("Stage 1 Ratio",f"×{r_billet:.4f}",f"Yield {y_billet:.1f}%")
        st.divider()
        st.markdown("**Stage 2: Billet → Extrusion / Forging**")
        r_ext = st.number_input("Extrusion / Forging ratio",value=float(CONVERSION['r_extrusion']),step=0.1,format="%.1f",key="r_ext")
        r_total = r_billet*r_ext; y_total = 1/r_total*100
        st.metric("Stage 2 Ratio",f"×{r_ext:.1f}",f"Yield {1/r_ext*100:.1f}%")
        st.divider(); st.metric("Total Ratio",f"×{r_total:.4f}",f"Yield {y_total:.1f}%")
        st.divider(); st.header("📊 Alloys")
        for key,a in ALLOYS.items():
            with st.expander(f"{a['name']} ({a['spec']})"):
                st.write(a['app']); st.caption(", ".join(f"{e} {v}%" for e,v in a['comp'].items() if v>0))

    tab_today,tab_raw,tab_billet,tab_ext,tab_metals,tab_export = st.tabs([
        "📈 Today's Prices","🔵 A) Raw Material","🟠 B) Billet Cost",
        "🟢 C) Extr./Forging","📊 Metal Prices","💾 Export"])

    with tab_today:
        st.subheader("Fetch Current Metal Prices")
        if st.button("🔄 Fetch Live Prices",type="primary",use_container_width=True):
            with st.spinner("Fetching..."): result=fetch_all_prices(); st.session_state['fp']=result['prices']; st.session_state['fn']=result['notes']; st.session_state['fe']=result.get('errors',[]); st.session_state['fs']=result.get('sources',{})
        st.divider()
        prices=st.session_state.get('fp'); notes=st.session_state.get('fn',''); errors=st.session_state.get('fe',[]); sources=st.session_state.get('fs',{})
        for e in errors: st.warning(e)
        st.subheader("Metal Prices")
        st.markdown("🟢 **Live** &nbsp; 🔵 **Estimated** &nbsp; 🟡 **Static** &nbsp; 🔴 **Fallback**")
        st.caption("LME base metals in USD/t · Silver in USD/oz · Minor elements in USD/kg")
        def _f(k):
            if k not in sources: return "⚪"
            return {"live":"🟢","estimated":"🔵","static":"🟡","fallback":"🔴"}.get(sources[k][0],"⚪")
        def _d(k): return sources[k][1] if k in sources else "Not fetched"
        c1,c2,c3,c4=st.columns(4)
        with c1:
            st.markdown(f"**{_f('Al')} Aluminium** — {_d('Al')}"); al=st.number_input("Al",value=float(prices['Al']) if prices else 3329.0,step=10.0,format="%.1f",label_visibility="collapsed")
            st.markdown(f"**{_f('Cu')} Copper** — {_d('Cu')}"); cu=st.number_input("Cu",value=float(prices['Cu']) if prices else 12022.0,step=50.0,format="%.1f",label_visibility="collapsed")
            st.markdown(f"**{_f('Ni')} Nickel** — {_d('Ni')}"); ni=st.number_input("Ni",value=float(prices['Ni']) if prices else 16770.0,step=50.0,format="%.1f",label_visibility="collapsed")
        with c2:
            st.markdown(f"**{_f('Ag_oz')} Silver (USD/oz)** — {_d('Ag_oz')}"); ag=st.number_input("Ag",value=float(prices['Ag_oz']) if prices else 65.0,step=1.0,format="%.2f",label_visibility="collapsed")
            st.markdown(f"**{_f('Zn')} Zinc** — {_d('Zn')}"); zn=st.number_input("Zn",value=float(prices['Zn']) if prices else 3066.0,step=10.0,format="%.1f",label_visibility="collapsed")
            st.markdown(f"**{_f('Li')} Lithium (USD/kg)** — {_d('Li')}"); li=st.number_input("Li",value=float(prices['Li']) if prices else 195.0,step=5.0,format="%.0f",label_visibility="collapsed")
        with c3:
            st.markdown(f"**{_f('Mg')} Magnesium** — {_d('Mg')}"); mg=st.number_input("Mg",value=float(prices['Mg']) if prices else 2.40,step=0.05,format="%.2f",label_visibility="collapsed")
            st.markdown(f"**{_f('Mn')} Manganese** — {_d('Mn')}"); mn=st.number_input("Mn",value=float(prices['Mn']) if prices else 1.85,step=0.05,format="%.2f",label_visibility="collapsed")
            st.markdown(f"**{_f('Ti')} Titanium** — {_d('Ti')}"); ti=st.number_input("Ti",value=float(prices['Ti']) if prices else 7.00,step=0.10,format="%.2f",label_visibility="collapsed")
        with c4:
            st.markdown(f"**{_f('Zr')} Zirconium** — {_d('Zr')}"); zr=st.number_input("Zr",value=float(prices['Zr']) if prices else 35.0,step=1.0,format="%.1f",label_visibility="collapsed")
            st.markdown(f"**{_f('Fe')} Iron** — {_d('Fe')}"); fe=st.number_input("Fe",value=float(prices['Fe']) if prices else 0.10,step=0.01,format="%.2f",label_visibility="collapsed")
            st.markdown(f"**{_f('Si')} Silicon** — {_d('Si')}"); si=st.number_input("Si",value=float(prices['Si']) if prices else 2.40,step=0.10,format="%.2f",label_visibility="collapsed")
        if sources:
            lc=sum(1 for s,_ in sources.values() if s=='live'); ec=sum(1 for s,_ in sources.values() if s=='estimated')
            sc=sum(1 for s,_ in sources.values() if s=='static'); fc=sum(1 for s,_ in sources.values() if s=='fallback')
            st.info(f"🟢 {lc} live · 🔵 {ec} estimated · 🟡 {sc} static · 🔴 {fc} fallback")
        cp={'Al':al,'Cu':cu,'Ag_oz':ag,'Zn':zn,'Ni':ni,'Li':li,'Mg':mg,'Mn':mn,'Ti':ti,'Zr':zr,'Fe':fe,'Si':si}
        save_date=st.date_input("Date",value=date.today())
        if st.button("💾 Save to Database",use_container_width=True): save_prices(conn,save_date.isoformat(),cp,notes); st.success(f"✅ Saved for {save_date}")
        st.divider(); st.subheader("Current Cost Summary")
        summary=[]
        for key,alloy in ALLOYS.items():
            raw,ag_c,li_c=calc_alloy_cost(alloy['comp'],cp); bil,ext=calc_conversion_costs(raw,r_billet,r_total)
            summary.append({'Alloy':alloy['name'],'Raw $/kg':raw,'Billet $/kg':bil,'Ext./Forg. $/kg':ext,'Ag $/kg':ag_c,'Ag %':ag_c/raw*100 if raw>0 else 0})
        df_s=pd.DataFrame(summary)
        st.dataframe(df_s.style.format({'Raw $/kg':'${:.2f}','Billet $/kg':'${:.2f}','Ext./Forg. $/kg':'${:.2f}','Ag $/kg':'${:.2f}','Ag %':'{:.1f}%'}).background_gradient(subset=['Ext./Forg. $/kg'],cmap='YlOrRd'),use_container_width=True,hide_index=True)
        cm=st.columns(5)
        for i,(key,alloy) in enumerate(ALLOYS.items()):
            with cm[i]: st.metric(alloy['name'],f"${summary[i]['Ext./Forg. $/kg']:.2f}/kg",f"${summary[i]['Raw $/kg']:.2f} raw")

    df_hist=load_history(conn); df_cost=build_cost_df(df_hist,r_billet,r_total) if not df_hist.empty else pd.DataFrame()
    with tab_raw: st.subheader("A) Raw Material Cost (USD/kg)"); st.caption("Element cost per kg — before conversion"); stage_tab(df_cost,' raw','Raw Material Cost','USD/kg','raw')
    with tab_billet: st.subheader(f"B) Billet Cost (USD/kg) — ×{r_billet:.4f}"); st.caption(f"Cast {d_cast:.0f}mm Ø × {l_cast:.0f}mm → Billet {d_lathed:.0f}mm Ø × {l_usable:.0f}mm | Yield {y_billet:.1f}%"); stage_tab(df_cost,' billet','Billet Cost','USD/kg','billet')
    with tab_ext: st.subheader(f"C) Extrusion / Forging Cost — ×{r_total:.4f}"); st.caption(f"×{r_billet:.4f} × {r_ext:.1f} = ×{r_total:.4f} | Yield {y_total:.1f}%"); stage_tab(df_cost,' ext.','Extrusion / Forging Cost','USD/kg','ext')
    with tab_metals:
        st.subheader("Metal Price History")
        if not df_cost.empty:
            st.write("#### Silver ($/oz)"); make_chart(df_cost,['Ag ($/oz)'],'Silver','USD/oz','ag')
            st.caption("Source: goldprice.org API / Bullion.com / APMEX / JM Bullion / Fortune")
            st.markdown("---"); st.write("#### Al & Cu LME ($/t)"); make_chart(df_cost,['Al ($/t)','Cu ($/t)'],'Al & Cu','USD/t','alcu',dual_axis=True)
            st.caption("Source: Westmetall.com — LME Cash Settlement")
            st.markdown("---"); st.write("#### Lithium Metal ($/kg)"); make_chart(df_cost,['Li ($/kg)'],'Lithium','USD/kg','li')
            st.caption("Source: TradingEconomics Li₂CO₃ × 10 / ChemAnalyst / IMARC")
            st.markdown("---"); st.write("#### Price History"); st.dataframe(df_hist,use_container_width=True)
            st.caption(f"{len(df_hist)} records | LME: Westmetall · Ag: dealer spot · Li: TradingEcon · Mg,Mn,Ti,Si: TradingEcon/Asian Metal · Zr: USGS · Fe: nominal")
    with tab_export:
        st.subheader("Export to Excel")
        if not df_hist.empty:
            conv={'r_billet':r_billet,'r_extrusion':r_ext,'r_total':r_total}
            if st.button("📥 Generate Excel",type="primary"):
                with st.spinner("Building..."): xlsx=generate_excel(df_hist,ALLOYS,conv)
                st.download_button("⬇️ Download",data=xlsx,file_name=f"AA_5Alloy_{date.today()}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ── Admin: Seed historical data ──────────────────────────
    with st.sidebar:
        st.divider()
        if st.button("🌱 Seed Historical Data"):
            from seed_history import HISTORY
            db = get_db()
            for row in HISTORY:
                db.execute("INSERT OR REPLACE INTO price_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
            db.commit()
            st.success(f"✅ Seeded {len(HISTORY)} rows!")
            st.rerun()

if __name__ == "__main__":
    main()
