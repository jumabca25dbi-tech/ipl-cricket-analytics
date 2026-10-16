import base64
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ======================= THEME + ANIMATIONS (Finext-style dark UI) =======================
BG, PANEL, PANEL_2, LINE = "#121214", "#1A1A1E", "#232328", "#2A2A30"
CHALK, MUTED = "#F5F5F7", "#8A8A93"
RED, RED_DEEP, PEACH, GREEN, PURPLE = "#EE2E4A", "#C7233D", "#FFC9B5", "#2ED573", "#7B3FF2"
INK, LEATHER, BALL, GRASS = BG, RED, RED, GREEN
LOGO_FILTER = "brightness(1.9) saturate(1.3)"
COLORWAY = [RED, PEACH, "#6E6E78", PURPLE, GREEN, "#FF8FA0"]

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, .stApp * {{ font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }}
[data-testid="stIconMaterial"], [data-testid="stIconMaterial"] *, .material-icons, [class*="material-symbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-feature-settings: 'liga'; letter-spacing: normal !important; text-transform: none; white-space: nowrap; font-size: 1.25rem;
}}
.stApp {{ background: {BG}; color: {CHALK}; }}
.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }}
header[data-testid="stHeader"] {{ background: transparent; }}
h2, h3 {{ color: {CHALK} !important; font-weight: 700 !important; font-size: 1.15rem !important; letter-spacing: -0.01em; animation: fade .6s both; }}
hr {{ border-color: {LINE}; }}
[data-testid="stCaptionContainer"] {{ color: {MUTED}; }}

@keyframes roll-in {{ from {{ transform: translateX(-200px) rotate(-720deg); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
@keyframes slide-in {{ from {{ transform: translateX(-16px); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
@keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes pop {{ from {{ opacity: 0; transform: scaleY(.2); }} to {{ opacity: 1; transform: none; }} }}
@keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 {GREEN}88; }} 70% {{ box-shadow: 0 0 0 9px {GREEN}00; }} 100% {{ box-shadow: 0 0 0 0 {GREEN}00; }} }}
@property --num {{ syntax: '<integer>'; initial-value: 0; inherits: false; }}
@keyframes count {{ from {{ --num: 0; }} to {{ --num: var(--target); }} }}

/* ---------- Bowler Action Delivery Animation ---------- */
.simulation-card {{
    background: {PANEL};
    border: 1px solid {LINE};
    border-radius: 20px;
    padding: 16px 20px;
    margin-bottom: 24px;
    animation: rise .7s both;
}}
.sim-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}}
.sim-title {{
    font-size: 0.95rem;
    font-weight: 800;
    color: {CHALK};
    letter-spacing: 0.05em;
}}
.sim-sub {{
    font-size: 0.78rem;
    color: {MUTED};
}}
.sim-badge {{
    background: {RED}22;
    color: {RED};
    border: 1px solid {RED}66;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
}}
.bowler-pitch-area {{
    position: relative;
    height: 90px;
    background: linear-gradient(90deg, #183d22 0%, #20522e 50%, #183d22 100%);
    border-radius: 12px;
    border: 1px dashed {GREEN}44;
    overflow: hidden;
    display: flex;
    align-items: center;
    padding: 0 20px;
}}
.bowler-figure {{
    position: absolute;
    left: 30px;
    bottom: 15px;
    width: 16px;
    height: 50px;
    animation: run-up 2.2s infinite ease-in-out;
}}
.bowler-head {{
    position: absolute;
    top: 0; left: 2px;
    width: 10px; height: 10px;
    background: {PEACH}; border-radius: 50%;
}}
.bowler-body {{
    position: absolute;
    top: 10px; left: 4px;
    width: 6px; height: 24px;
    background: {RED}; border-radius: 3px;
}}
.bowler-arm-right {{
    position: absolute;
    top: 12px; left: 8px;
    width: 14px; height: 4px;
    background: {PEACH}; border-radius: 2px;
    transform-origin: left center;
    animation: arm-bowling 2.2s infinite ease-in-out;
}}
.action-ball {{
    position: absolute;
    left: 48px;
    bottom: 30px;
    width: 10px;
    height: 10px;
    background: radial-gradient(circle at 30% 30%, #FF7A8C, {RED});
    border-radius: 50%;
    box-shadow: 0 0 8px {RED};
    animation: ball-delivery 2.2s infinite cubic-bezier(0.2, 0.8, 0.2, 1);
}}
.stumps-right-box {{
    position: absolute;
    right: 30px;
    display: flex;
    gap: 3px;
}}
.stump-rod {{
    width: 3px;
    height: 35px;
    background: {PEACH};
    border-radius: 2px;
}}
@keyframes run-up {{
    0% {{ transform: translateX(0); }}
    40% {{ transform: translateX(60px); }}
    50%, 100% {{ transform: translateX(60px); }}
}}
@keyframes arm-bowling {{
    0%, 30% {{ transform: rotate(0deg); }}
    45% {{ transform: rotate(-140deg); }}
    60%, 100% {{ transform: rotate(20deg); }}
}}
@keyframes ball-delivery {{
    0%, 40% {{ left: 48px; bottom: 30px; opacity: 1; }}
    80% {{ left: calc(100% - 45px); bottom: 25px; opacity: 1; }}
    100% {{ left: calc(100% - 45px); bottom: 25px; opacity: 0; }}
}}

/* ---------- KPI Boxes Matching Color Glow & Zoom Effect ---------- */
.kpi {{
    border-radius: 20px;
    padding: 18px 20px;
    min-height: 150px;
    animation: rise .7s both;
    position: relative;
    z-index: 1;
    will-change: transform, box-shadow;
    transition: transform 0.35s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.35s ease !important;
}}

/* Red tone box & shadow */
.kpi, .kpi.t-red {{
    background: linear-gradient(135deg, #F5385A, #DD2342);
    box-shadow: 0 14px 30px {RED}33;
}}
.kpi:hover, .kpi.t-red:hover {{
    transform: translateY(-6px) scale(1.04) !important;
    box-shadow: 0 24px 48px {RED}88 !important;
    z-index: 9999 !important;
}}

/* Peach tone box & shadow */
.kpi.t-peach {{
    background: linear-gradient(135deg, #FFD9CB, #FFB79D);
    box-shadow: 0 14px 30px #FFC9B533;
}}
.kpi.t-peach:hover {{
    transform: translateY(-6px) scale(1.04) !important;
    box-shadow: 0 24px 48px #FFB79Daa !important;
    z-index: 9999 !important;
}}

/* Purple tone box & shadow */
.kpi.t-purple {{
    background: linear-gradient(135deg, #8F62F8, #6633DE);
    box-shadow: 0 14px 30px {PURPLE}33;
}}
.kpi.t-purple:hover {{
    transform: translateY(-6px) scale(1.04) !important;
    box-shadow: 0 24px 48px {PURPLE}88 !important;
    z-index: 9999 !important;
}}

/* Green tone box & shadow */
.kpi.t-green {{
    background: linear-gradient(135deg, #34D87B, #17A857);
    box-shadow: 0 14px 30px {GREEN}33;
}}
.kpi.t-green:hover {{
    transform: translateY(-6px) scale(1.04) !important;
    box-shadow: 0 24px 48px {GREEN}88 !important;
    z-index: 9999 !important;
}}

.kpi-label {{ color: #FFE0E5; font-size: .85rem; font-weight: 500; }}
.kpi-value {{ color: #fff; font-size: 1.95rem; font-weight: 700; line-height: 1.25; margin-top: 8px; letter-spacing: -0.02em; }}
.kpi-count {{ animation: count 1.4s .3s cubic-bezier(.2,.8,.2,1) both; counter-reset: n var(--num); }}
.kpi-count::after {{ content: counter(n); }}
.kpi-note {{ color: #FFE0E5; font-size: .78rem; margin-top: 4px; }}
.seg {{ display: flex; gap: 4px; margin-top: 12px; }}
.seg i {{ flex: 1; height: 22px; border-radius: 3px; background: #00000033; transform-origin: bottom; }}
.seg i.on {{ background: #fff; animation: pop .5s both; }}

.kpi.t-red .kpi-label, .kpi.t-red .kpi-note, .kpi.t-purple .kpi-label, .kpi.t-purple .kpi-note,
.kpi.t-green .kpi-label, .kpi.t-green .kpi-note {{ color: #ffffffcc; }}
.kpi.t-red .kpi-value, .kpi.t-purple .kpi-value, .kpi.t-green .kpi-value {{ color: #fff; }}
.kpi.t-peach .kpi-label, .kpi.t-peach .kpi-note {{ color: #7A3E2B; }}
.kpi.t-peach .kpi-value {{ color: #2B120B; }}

/* ---------- Animated Filter Box Accent Header ---------- */
.filter-anim-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    font-weight: 700;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid {LINE};
}}
.filter-pulse-dot {{
    width: 6px;
    height: 6px;
    background-color: {RED};
    border-radius: 50%;
    box-shadow: 0 0 8px {RED};
    animation: pulse 1.5s infinite;
}}

/* ---------- Page header ---------- */
.hero {{ display: flex; align-items: center; gap: 14px; }}
.hero-ball {{ width: 40px; height: 40px; flex: none; border-radius: 50%; position: relative;
    background: radial-gradient(circle at 32% 30%, #FF7A8C, {RED} 55%, #9E1630); box-shadow: 0 8px 22px {RED}55;
    animation: roll-in 1.1s cubic-bezier(.2,.8,.2,1) both, spin 3s linear 1.1s infinite; }}
.hero-ball::before, .hero-ball::after {{ content: ""; position: absolute; left: 50%; top: 6%; bottom: 6%; border-left: 2px dashed #fff; transform: translateX(-50%); }}
.hero-ball::before {{ margin-left: -5px; }} .hero-ball::after {{ margin-left: 5px; }}
.hero-title {{ font-size: 1.7rem; font-weight: 700; margin: 0; color: {CHALK}; animation: slide-in .8s .3s both; }}
.hero-sub {{ color: {MUTED}; font-size: .88rem; margin: 2px 0 20px 54px; animation: fade .8s .7s both; }}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{ background: #151518; border-right: 1px solid {LINE}; animation: slide-in .6s both; }}
section[data-testid="stSidebar"] * {{ color: {CHALK}; }}
.brand {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.2rem; margin: 4px 0 14px; }}
.brand-badge {{ width: 36px; height: 36px; border-radius: 11px; background: {RED}; display: grid; place-items: center; color: #fff !important; font-weight: 800; }}
.brand b {{ color: {RED}; font-weight: 700; }}
.live-dot {{ width: 8px; height: 8px; border-radius: 50%; background: {GREEN}; margin-left: auto; animation: pulse 1.8s infinite; }}
.logo-wrap {{ display: flex; justify-content: flex-start; margin: 2px 0 12px; animation: fade .8s both; }}
.logo {{ width: 100%; max-width: 190px; height: auto; max-height: 96px; object-fit: contain; filter: {LOGO_FILTER}; }}
.nav-label {{ font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; color: {MUTED} !important; margin: 18px 0 8px 4px; }}
section[data-testid="stSidebar"] label p {{ font-size: .78rem; color: {MUTED} !important; }}

section[data-testid="stSidebar"] .stButton > button {{
    width: 100%; justify-content: flex-start; background: transparent; border: none; border-radius: 12px; padding: 10px 14px;
    color: {MUTED}; font-weight: 500; box-shadow: none; transition: background .2s, color .2s, padding-left .2s; }}
section[data-testid="stSidebar"] .stButton > button * {{ color: inherit !important; }}
section[data-testid="stSidebar"] .stButton > button p {{ font-size: .95rem; text-align: left; }}
section[data-testid="stSidebar"] .stButton > button:hover {{ background: {PANEL_2}; color: {CHALK}; padding-left: 18px; transform: none; }}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{ background: {RED}; color: #fff; box-shadow: 0 8px 20px {RED}44; }}

section[data-testid="stSidebar"] [data-testid="stButtonGroup"] {{ gap: 0; }}
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button {{ background: {PANEL_2}; border: 1px solid {LINE}; color: {MUTED}; font-size: .85rem; }}

div[data-testid="stPlotlyChart"] {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 20px; padding: 10px; overflow: hidden; animation: rise .8s .15s both; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 20px; padding: 12px; }}

@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}
</style>
"""


def inject_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(title, subtitle=""):
    st.markdown(f'<div class="hero"><div class="hero-ball"></div><h1 class="hero-title">{title}</h1></div>'
                f'<div class="hero-sub">{subtitle}</div>', unsafe_allow_html=True)


def _find_logo():
    here = Path(__file__).resolve().parent
    dirs = []
    for base_dir in [here, here.parent, Path.cwd()]:
        for d in (base_dir / 'assets', base_dir / 'static', base_dir / 'images', base_dir):
            if d not in dirs:
                dirs.append(d)
    exts = ('.png', '.svg', '.webp', '.jpg', '.jpeg')
    for d in dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            n = p.name.lower()
            if p.is_file() and any(n.endswith(e) for e in exts) and ('logo' in n or n.startswith('ipl')):
                return p
    return None


def sidebar_brand():
    logo = _find_logo()
    if logo:
        ext = logo.name.lower().rsplit('.', 1)[-1]
        mime = {'svg': 'image/svg+xml', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'}.get(ext, f'image/{ext}')
        data = base64.b64encode(logo.read_bytes()).decode()
        st.sidebar.markdown(f'<div class="logo-wrap"><img class="logo" src="data:{mime};base64,{data}" alt="IPL"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="brand"><div class="brand-badge">I</div>IPL <b>Bowlers</b><span class="live-dot"></span></div>', unsafe_allow_html=True)


def nav_label(text):
    st.sidebar.markdown(f'<div class="nav-label">{text}</div>', unsafe_allow_html=True)


def chart_theme(fig, height=340):
    fig.update_layout(
        template="plotly_dark", height=height, margin=dict(l=20, r=20, t=64, b=36),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=COLORWAY, bargap=0.38,
        font=dict(family="Plus Jakarta Sans, Arial, sans-serif", size=12, color=MUTED),
        title=dict(font=dict(size=17, color=CHALK), x=0.02),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, font=dict(size=12, color=MUTED)),
        hoverlabel=dict(bgcolor=PANEL_2, bordercolor=RED, font=dict(color=CHALK, size=13)),
        transition=dict(duration=600, easing="cubic-in-out"),
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(color=MUTED), showline=False, zeroline=False, title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor="#26262C", tickfont=dict(color=MUTED), showline=False, zeroline=False, title_font=dict(color=MUTED))
    fig.update_traces(marker_cornerradius=8, selector=dict(type="bar"))
    return fig


def kpi(col, label, value, note="", delay=0.0, fill=None, featured=False, tone=None):
    if isinstance(value, (int, float)) and float(value).is_integer():
        body = f'<div class="kpi-value kpi-count" style="--target:{int(value)}"></div>'
    else:
        body = f'<div class="kpi-value">{value}</div>'
    bar = ""
    if fill is not None:
        on = int(round(max(0, min(100, fill)) / 100 * 12))
        bar = '<div class="seg">' + "".join(f'<i class="on" style="animation-delay:{0.4 + i * 0.07:.2f}s"></i>' if i < on else '<i></i>' for i in range(12)) + '</div>'
    col.markdown(f'<div class="kpi{(" t-" + (tone or "red")) if (tone or featured) else ""}" style="animation-delay:{delay}s"><div class="kpi-label">{label}</div>{body}<div class="kpi-note">{note}</div>{bar}</div>', unsafe_allow_html=True)


# ======================= APP =======================
st.set_page_config(page_title='IPL Bowlers Analytics', page_icon='🏏', layout='wide')

PROJECT_DIR = Path(r'C:\Users\jumab\Documents\ipl-cricket-analytics')
DB_CANDIDATES = [
    PROJECT_DIR / 'data' / 'ipl.db',
    PROJECT_DIR / 'data' / 'raw' / 'ipl.db'
]
DB_PATH = next((p for p in DB_CANDIDATES if p.exists()), DB_CANDIDATES[0])

inject_theme()


@st.cache_data
def load_data(path):
    with sqlite3.connect(str(path)) as conn:
        return pd.read_sql_query('SELECT * FROM v_ball', conn)

if not DB_PATH.exists():
    st.error(f'Database not found: {DB_PATH}. Check where ipl.db is saved.')
    st.stop()
try:
    df = load_data(DB_PATH)
except Exception as e:
    st.error(f'Could not read SQL view v_ball: {e}')
    st.stop()

needed = ['season_id','match_id','bowler','over_number','bowler_type','phase','is_legal','bowler_runs','bowler_wicket','bowling_team','batting_team','batter_runs']
missing = [c for c in needed if c not in df.columns]
if missing:
    st.error(f'Missing columns in v_ball: {missing}')
    st.stop()
for c in ['season_id','match_id','over_number','is_legal','bowler_runs','bowler_wicket','batter_runs']:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
df['season_id'] = df['season_id'].astype(int).astype(str)
df['bowler'] = df['bowler'].fillna('Unknown')
df['bowler_type'] = df['bowler_type'].fillna('Unknown').replace('', 'Unknown')
df['phase'] = df['phase'].fillna('Unknown')
df['bowling_team'] = df['bowling_team'].fillna('Unknown')
df['batting_team'] = df['batting_team'].fillna('Unknown')
df['dot_ball'] = (df['total_runs'].fillna(0) == 0).astype(int) if 'total_runs' in df.columns else (df['bowler_runs'] == 0).astype(int)

SPIN, PACE = 'spin', 'fast|pace|medium'

def balls(g): return int(g['is_legal'].sum())
def economy(g):
    b = balls(g)
    return float(g['bowler_runs'].sum() * 6 / b) if b else np.nan
def agg(data, keys):
    out = data.groupby(keys, as_index=False).agg(Runs=('bowler_runs','sum'), Balls=('is_legal','sum'), Wickets=('bowler_wicket','sum'), Dots=('dot_ball','mean'))
    out['Economy'] = np.where(out['Balls'] > 0, out['Runs'] * 6 / out['Balls'].replace(0, np.nan), np.nan)
    out['Dot-ball share'] = out['Dots'] * 100
    return out
def bowler_summary(data): return agg(data, 'bowler')
def style_group(s):
    s = s.str.lower()
    return np.where(s.str.contains(SPIN, na=False), 'Spin', np.where(s.str.contains(PACE, regex=True, na=False), 'Pace', 'Other'))


df['style_group'] = style_group(df['bowler_type'])
sidebar_brand()
if 'page' not in st.session_state:
    st.session_state.page = 'Overview'
nav_label('Menu')
for _name, _icon in [('Overview', ':material/dashboard:'), ('Bowler', ':material/sports_cricket:')]:
    if st.sidebar.button(_name, icon=_icon, key=f'nav_{_name}', use_container_width=True, type='primary' if st.session_state.page == _name else 'secondary'):
        st.session_state.page = _name
        st.rerun()
page = st.session_state.page
nav_label('Filters')
all_seasons = sorted(df['season_id'].unique().tolist(), key=lambda x:int(x))
if len(all_seasons) > 1:
    s_from, s_to = st.sidebar.select_slider('Seasons', options=all_seasons, value=(all_seasons[0], all_seasons[-1]))
else:
    s_from = s_to = all_seasons[0]
selected_seasons = [x for x in all_seasons if int(s_from) <= int(x) <= int(s_to)]
if hasattr(st.sidebar, 'segmented_control'):
    style_pick = st.sidebar.segmented_control('Bowling style', ['All', 'Spin', 'Pace'], default='All') or 'All'
else:
    style_pick = st.sidebar.radio('Bowling style', ['All', 'Spin', 'Pace'], horizontal=True)
min_balls = st.sidebar.slider('Min balls', 0, 1500, 500, 50)
min_wickets = st.sidebar.slider('Min wickets', 0, 100, 10, 1) if page == 'Bowler' else 0

season_df = df[df['season_id'].isin(selected_seasons)]
base = season_df if style_pick == 'All' else season_df[season_df['style_group'] == style_pick]
base = base.copy()
if base.empty:
    st.warning('No data matches these filters. Widen the season range or pick another bowling style.')
    st.stop()

if page == 'Overview':
    hero('IPL Bowlers: Overview', 'For the bowling coach, deciding which bowler to pick and for which overs.')
    
    # ---------- Bowler Delivery Action Animation ----------
    st.markdown("""
    <div class="simulation-card">
        <div class="sim-header">
            <div>
                <span class="sim-title">🏏 BOWLER RUN-UP & DELIVERY ACTION</span>
                <div class="sim-sub">Real-time player bowling action and ball release tracking</div>
            </div>
            <span class="sim-badge">ACTION CAM</span>
        </div>
        <div class="bowler-pitch-area">
            <div class="bowler-figure">
                <div class="bowler-head"></div>
                <div class="bowler-body"></div>
                <div class="bowler-arm-right"></div>
            </div>
            <div class="action-ball"></div>
            <div class="stumps-right-box">
                <div class="stump-rod"></div>
                <div class="stump-rod"></div>
                <div class="stump-rod"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    eligible = bowler_summary(base)
    eligible = eligible[eligible['Balls'] >= min_balls]
    c1, c2, c3, c4 = st.columns([1.25, 1, 1, 1.15])
    n_b = base['bowler'].nunique()
    kpi(c1, 'Bowlers in selection', n_b, f'{len(eligible)} meet the {min_balls:,}-ball minimum', delay=0.1, tone='red')
    kpi(c2, 'Wickets credited to bowlers', int(df['bowler_wicket'].sum()), 'Fixed total before filters', delay=0.25, tone='peach')
    spin_e = economy(season_df[season_df['style_group'] == 'Spin'])
    pace_e = economy(season_df[season_df['style_group'] == 'Pace'])
    kpi(c3, 'Spin vs pace economy', f'{spin_e:.2f} vs {pace_e:.2f}' if pd.notna(spin_e) and pd.notna(pace_e) else 'Not enough data', 'Runs per over', delay=0.4, tone='purple')
    q_pct = 100 * len(eligible) / n_b if n_b else 0
    kpi(c4, 'Qualified bowlers', f'{q_pct:.0f}%', f'{len(eligible)} of {n_b} bowlers', delay=0.55, fill=q_pct, tone='green')

    st.subheader('Economy by innings phase: spin vs pace')
    st.caption('Does spin or pace save more runs in each phase? Dashed line is the league economy for your selection.')
    
    # ---------- Animated Filter Box 1 ----------
    with st.container(border=True):
        st.markdown('<div class="filter-anim-header"><span>⚡ Phase & Style Parameters</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        phase_filter = f1.selectbox('Filter this chart by phase', ['All phases'] + sorted(base['phase'].unique().tolist()), key='overview_phase_filter')
        style_filter = f2.selectbox('Filter this chart by bowling style', ['All styles', 'Spin', 'Pace'], key='overview_style_filter')
    
    cb = base
    if phase_filter != 'All phases':
        cb = cb[cb['phase'] == phase_filter]
    if style_filter != 'All styles':
        cb = cb[cb['style_group'] == style_filter]
    plot = agg(cb, ['phase', 'style_group']).rename(columns={'style_group': 'Style group'})
    if not plot.empty:
        phase_order = ['Powerplay', 'Middle', 'Death']
        order = [p for p in phase_order if p in plot['phase'].unique()] + [p for p in plot['phase'].unique() if p not in phase_order]
        fig = px.bar(plot, x='phase', y='Economy', color='Style group', barmode='group', category_orders={'phase': order}, hover_data=['Balls'],
                     labels={'phase': 'Innings phase', 'Economy': 'Runs per over', 'Style group': 'Bowling type'}, title='Economy changes across innings phases')
        le = economy(base)
        if pd.notna(le):
            fig.add_hline(y=le, line_dash='dash', line_color=PEACH, annotation_text=f'League {le:.2f}')
        st.plotly_chart(chart_theme(fig, 390), use_container_width=True)
    else:
        st.info('No deliveries match this chart filter.')

    left, right = st.columns(2)
    with left:
        st.subheader('Styles ranked by economy')
        st.caption(f'Only bowlers with at least {min_balls:,} legal balls; counts shown on hover.')
        
        # ---------- Animated Filter Box 2 ----------
        with st.container(border=True):
            st.markdown('<div class="filter-anim-header"><span>⚡ Ranking Configuration</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
            rf1, rf2 = st.columns(2)
            rank_direction = rf1.selectbox('Rank order', ['Lowest first', 'Highest first'], key='rank_direction')
            top_styles = rf2.slider('Number of styles', 3, 15, 8, key='top_styles')
        
        rankbase = base[base['bowler'].isin(eligible['bowler'])]
        ranked = rankbase.groupby('bowler_type').apply(lambda g: pd.Series({'Economy': economy(g), 'Balls': balls(g), 'Bowlers': g['bowler'].nunique()}), include_groups=False).reset_index()
        ranked = ranked.sort_values('Economy', ascending=(rank_direction == 'Lowest first')).head(top_styles)
        if not ranked.empty:
            fig2 = px.bar(ranked, x='Economy', y='bowler_type', orientation='h', text='Economy', hover_data=['Balls', 'Bowlers'], labels={'bowler_type': 'Bowling style'}, title='Which bowling style is cheapest?')
            fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside', marker_color=LEATHER)
            st.plotly_chart(chart_theme(fig2, 330), use_container_width=True)
        else:
            st.info('No bowlers meet the minimum-ball filter.')
    with right:
        st.subheader('Wickets by innings phase')
        st.caption(f'Based on selected filters; minimum threshold {min_balls:,} balls per bowler.')
        
        # ---------- Animated Filter Box 3 ----------
        with st.container(border=True):
            st.markdown('<div class="filter-anim-header"><span>⚡ Phase Breakdown</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
            wicket_phase_filter = st.selectbox('Filter this chart by phase', ['All phases'] + sorted(base['phase'].unique().tolist()), key='wicket_phase_filter')
        
        wd = base[base['bowler'].isin(eligible['bowler'])].groupby('phase', as_index=False).agg(Wickets=('bowler_wicket', 'sum'), Balls=('is_legal', 'sum'))
        if wicket_phase_filter != 'All phases':
            wd = wd[wd['phase'] == wicket_phase_filter]
        fig3 = px.bar(wd, x='phase', y='Wickets', text='Wickets', hover_data=['Balls'], title='Where do wickets come from?')
        fig3.update_traces(marker_color=PEACH)
        st.plotly_chart(chart_theme(fig3, 330), use_container_width=True)
    st.caption('For the bowling coach: compare economy and wickets by phase before choosing a bowling style.')

else:
    hero('IPL Bowlers: Bowler', 'Season trend, phases, opponents and overs for one bowler.')
    summary = bowler_summary(base)
    eligible = summary[(summary['Balls'] >= min_balls) & (summary['Wickets'] >= min_wickets)]
    names = sorted(eligible['bowler'].unique().tolist())
    if not names:
        st.warning('No bowler meets the selected minimum balls and wickets. Lower the filters in the sidebar.')
        st.stop()
    chosen = st.selectbox('Selected bowler', names, help='All cards and charts below update for this bowler.')
    player = base[base['bowler'] == chosen].copy()
    pe = economy(player)
    dot = player['dot_ball'].mean() * 100
    c1, c2, c3 = st.columns(3)
    kpi(c1, 'Wickets taken', int(player['bowler_wicket'].sum()), f'{balls(player):,} legal balls bowled', delay=0.1, tone='red')
    kpi(c2, 'Economy', f'{pe:.2f}' if pd.notna(pe) else 'N/A', f'Based on {balls(player):,} legal balls', delay=0.25, fill=min(100, pe / 14 * 100) if pd.notna(pe) else None, tone='peach')
    kpi(c3, 'Dot-ball share', f'{dot:.1f}%', f'Based on {len(player):,} deliveries', delay=0.4, fill=dot, tone='purple')

    st.subheader('Economy by season: selected bowler')
    st.caption('Is this bowler better or worse than league economy each season? Dashed line is the league economy.')
    
    # ---------- Animated Filter Box 4 ----------
    with st.container(border=True):
        st.markdown('<div class="filter-anim-header"><span>⚡ Trend Configuration</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
        sf1, sf2 = st.columns(2)
        season_view = sf1.selectbox('Show trend', ['Economy', 'Wickets'], key='season_view')
        season_start = sf2.selectbox('Season range', ['All seasons', 'Recent 5 seasons'], key='season_range')
    
    ps = agg(player, 'season_id')[['season_id', 'Economy', 'Balls', 'Wickets']]
    ls = agg(base, 'season_id')[['season_id', 'Economy']].rename(columns={'Economy': 'League economy'})
    trend = ps.merge(ls, on='season_id', how='left').sort_values('season_id', key=lambda s: s.astype(int))
    if season_start == 'Recent 5 seasons':
        trend = trend.tail(5)
    fig = go.Figure()
    if season_view == 'Economy':
        fig.add_trace(go.Scatter(x=trend['season_id'], y=trend['Economy'], mode='lines+markers', name='Selected bowler', line=dict(color=LEATHER, width=3), customdata=trend[['Balls']], hovertemplate='Season %{x}<br>Economy %{y:.2f}<br>Balls %{customdata[0]}<extra></extra>'))
        fig.add_trace(go.Scatter(x=trend['season_id'], y=trend['League economy'], mode='lines', name='League economy', line=dict(dash='dash', color=PEACH)))
        y_title = 'Runs per over'
    else:
        fig.add_bar(x=trend['season_id'], y=trend['Wickets'], name='Wickets', marker_color=LEATHER)
        y_title = 'Wickets'
    fig.update_layout(title='Season-by-season performance', xaxis_title='Season', yaxis_title=y_title)
    st.plotly_chart(chart_theme(fig, 390), use_container_width=True)

    a, b, c = st.columns(3)
    with a:
        st.subheader('Wickets + economy by phase')
        
        # ---------- Animated Filter Box 5 ----------
        with st.container(border=True):
            st.markdown('<div class="filter-anim-header"><span>⚡ Metric Selection</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
            phase_metric = st.selectbox('Display on this chart', ['Both', 'Wickets', 'Economy'], key='bowler_phase_metric')
        
        ph = agg(player, 'phase')
        figp = go.Figure()
        if phase_metric in ['Both', 'Wickets']:
            figp.add_bar(x=ph['phase'], y=ph['Wickets'], name='Wickets', marker_color=LEATHER, customdata=ph[['Balls']], hovertemplate='%{x}<br>Wickets %{y}<br>Balls %{customdata[0]}<extra></extra>')
        if phase_metric in ['Both', 'Economy']:
            figp.add_scatter(x=ph['phase'], y=ph['Economy'], name='Economy', mode='lines+markers', line=dict(color=PEACH, width=3), yaxis='y2' if phase_metric == 'Both' else 'y')
        figp.update_layout(title='Which phases suit him?', yaxis_title='Wickets' if phase_metric != 'Economy' else 'Runs per over',
                           yaxis2=dict(title='Economy', overlaying='y', side='right', showgrid=False) if phase_metric == 'Both' else {})
        st.plotly_chart(chart_theme(figp, 350), use_container_width=True)
    with b:
        st.subheader('Economy vs opponent')
        
        # ---------- Animated Filter Box 6 ----------
        with st.container(border=True):
            st.markdown('<div class="filter-anim-header"><span>⚡ Opponent Range</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
            opponent_count = st.slider('Number of teams shown', 3, 12, 8, key='opponent_count')
        
        opp = agg(player, 'batting_team')
        opp = opp[opp['Balls'] > 0].sort_values('Economy').tail(opponent_count)
        figo = px.bar(opp, x='Economy', y='batting_team', orientation='h', hover_data=['Balls'], title='Toughest opponents (highest economy)', labels={'batting_team': 'Batting team'})
        figo.update_traces(marker_color=LEATHER)
        st.plotly_chart(chart_theme(figo, 350), use_container_width=True)
    with c:
        st.subheader('Economy by over number')
        
        # ---------- Animated Filter Box 7 ----------
        with st.container(border=True):
            st.markdown('<div class="filter-anim-header"><span>⚡ Over Limit</span><div class="filter-pulse-dot"></div></div>', unsafe_allow_html=True)
            over_max = st.slider('Show overs up to', 5, 20, 20, key='over_max')
        
        ov = agg(player, 'over_number')
        ov = ov[ov['over_number'] <= over_max]
        figv = px.line(ov, x='over_number', y='Economy', markers=True, hover_data=['Balls'], title='Which overs suit him?', labels={'over_number': 'Over'})
        figv.update_traces(line=dict(color=LEATHER, width=3))
        figv.update_xaxes(dtick=2)
        st.plotly_chart(chart_theme(figv, 350), use_container_width=True)
    st.caption('For the bowling coach: compare this bowler’s season trend, phase performance, opponents and over numbers.')