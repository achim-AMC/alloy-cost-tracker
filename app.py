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

# ── Smiths High Performance logo (base64) ───────────────────
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
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="left",x=0),height=420,margin=dict(l=60,r=60,t=40,b=40),hovermode='x unified')
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
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="left",x=0),height=420,margin=dict(l=60,r=20,t=40,b=40),hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

def stage_tab(df_cost, suffix, label, y_label, chart_key):
    if df_cost.empty: st.info("Save at least 2 data points."); return
    cols = [c for c in df_cost.columns if suffix in c]
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
