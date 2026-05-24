import streamlit as st
import pandas as pd
import boto3
import plotly.graph_objects as go
import plotly.express as px
import io
import base64
from datetime import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Data Analysis 2024-25",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
[data-testid="stSidebar"] {
    width: 250px !important;
    min-width: 250px !important;
    transform: none !important;
    visibility: visible !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── TEAM COLORS ─────────────────────────────────────────────────
TEAM_COLORS = {
    'Red Bull': '#3671C6',
    'Ferrari': '#E8002D',
    'McLaren': '#FF8000',
    'Mercedes': '#27F4D2',
    'Aston Martin': '#229971',
    'Alpine F1 Team': '#FF87BC',
    'Williams': '#64C4FF',
    'RB F1 Team': '#6692FF',
    'Haas F1 Team': '#B6BABD',
    'Sauber': '#52E252',
}

# ── LOAD IMAGE ───────────────────────────────────────────────────
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

car_img = get_image_base64("images/f1car.png")
car_html = f'<img src="data:image/png;base64,{car_img}" style="width:100%;filter:drop-shadow(0 0 40px rgba(225,6,0,0.5));">' if car_img else ""

# ── CSS (separate from f-string to avoid conflicts) ──────────────
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, [class*="css"] {
    background-color: #0a0a0a !important;
    color: #ffffff !important;
    font-family: 'Rajdhani', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    color: #e10600 !important;
}
.block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background: #0f0f0f !important;
    border-right: 1px solid #1e1e1e !important;
    min-width: 220px !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }

.sidebar-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem;
    font-weight: 900;
    color: #e10600 !important;
    letter-spacing: 3px;
    padding: 1rem 0 0.5rem 0;
    border-bottom: 2px solid #e10600;
    margin-bottom: 1rem;
    text-align: center;
}
.sidebar-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.3) !important;
    letter-spacing: 4px;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 2rem;
}
.cover-page {
    min-height: 80vh;
    display: flex;
    align-items: center;
    padding: 2rem 4rem;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 60%, #0a0a0a 100%);
    border-radius: 4px;
    overflow: hidden;
}
.cover-eyebrow {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.4);
    letter-spacing: 6px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.cover-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(3rem, 7vw, 7rem);
    font-weight: 900;
    line-height: 0.9;
    letter-spacing: -3px;
    color: #ffffff;
    text-transform: uppercase;
}
.cover-title .red { color: #e10600; }
.cover-line { width: 100px; height: 4px; background: #e10600; margin: 2rem 0; }
.cover-tagline {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: rgba(255,255,255,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
}
.cover-stats { display: flex; gap: 3rem; margin-top: 3rem; }
.cover-stat-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    color: #e10600;
}
.cover-stat-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
}
.stat-card {
    background: #111111;
    border: 1px solid #1e1e1e;
    border-top: 3px solid #e10600;
    padding: 1.5rem;
    border-radius: 2px;
    text-align: center;
}
.stat-number {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #e10600;
    line-height: 1;
}
.stat-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(255,255,255,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.section-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #ffffff;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #1e1e1e;
}
.section-header span { color: #e10600; }
.driver-card {
    background: linear-gradient(135deg, #111111, #0f0f0f);
    border: 1px solid #1e1e1e;
    border-left: 4px solid #e10600;
    padding: 2rem;
    border-radius: 2px;
    margin-bottom: 1rem;
}
.driver-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.8rem;
    font-weight: 900;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.driver-team {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: rgba(255,255,255,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}
.stSelectbox > div > div {
    background: #111111 !important;
    border: 1px solid #333 !important;
    color: #fff !important;
    font-family: 'Rajdhani', sans-serif !important;
}
div[data-testid="stRadio"] label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
    color: rgba(255,255,255,0.6) !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(filename):
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket = "f1-datapipeline-sujal"
    response = s3.get_object(Bucket=bucket, Key=filename)
    return pd.read_csv(io.StringIO(response['Body'].read().decode('utf-8')))

@st.cache_data(ttl=3600)
def load_all():
    date = datetime.now().strftime('%Y%m%d')
    return {
        'r24': load_data(f"f1-cleaned-data/cleaned_results_2024_{date}.csv"),
        'r25': load_data(f"f1-cleaned-data/cleaned_results_2025_{date}.csv"),
        'd24': load_data(f"f1-cleaned-data/cleaned_driver_standings_2024_{date}.csv"),
        'd25': load_data(f"f1-cleaned-data/cleaned_driver_standings_2025_{date}.csv"),
        'c24': load_data(f"f1-cleaned-data/cleaned_constructor_standings_2024_{date}.csv"),
        'c25': load_data(f"f1-cleaned-data/cleaned_constructor_standings_2025_{date}.csv"),
    }

data = load_all()
r24, r25 = data['r24'], data['r25']
d24, d25 = data['d24'], data['d25']
c24, c25 = data['c24'], data['c25']

# ── CHART HELPER ─────────────────────────────────────────────────
CHART = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Rajdhani', color='rgba(255,255,255,0.7)', size=12),
    margin=dict(l=10, r=10, t=30, b=10),
)

def apply_chart(fig, height=350, extra=None):
    layout = {**CHART, 'height': height}
    if extra:
        layout.update(extra)
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.1)')
    return fig

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">F1</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Data Analysis 2024–25</div>', unsafe_allow_html=True)

    page = st.radio(
        "",
        ["🏠  Overview", "👤  Drivers", "🏆  Constructors", "🏁  Race Analysis", "🔍  Team Deep Dive"],
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:Rajdhani;font-size:0.7rem;color:rgba(255,255,255,0.2);'
        'letter-spacing:2px;text-transform:uppercase;text-align:center;">'
        'Live via AWS S3<br>Auto-updates daily</div>',
        unsafe_allow_html=True
    )

# ════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════
if "Overview" in page:
    col_left, col_right = st.columns([1, 1])
    races_done = r25['Race_name'].nunique()
    leader = d25.iloc[0]

    with col_left:
        st.markdown(f"""
        <div class="cover-page">
            <div>
                <div class="cover-eyebrow">Formula One · Live Data</div>
                <div class="cover-title">F1<br><span class="red">Data</span><br>Analysis</div>
                <div class="cover-line"></div>
                <div class="cover-tagline">AWS Cloud Pipeline · Built by Sujal Patidar</div>
                <div class="cover-stats">
                    <div><div class="cover-stat-num">{races_done}</div><div class="cover-stat-label">Races</div></div>
                    <div><div class="cover-stat-num">{len(d25)}</div><div class="cover-stat-label">Drivers</div></div>
                    <div><div class="cover-stat-num">{len(c25)}</div><div class="cover-stat-label">Teams</div></div>
                </div>
                <br>
                {car_html}
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div style="padding:2rem;background:#111;border:1px solid #1e1e1e;border-radius:2px;">
            <div class="section-header">Championship <span>Leader</span></div>
            <div class="driver-card">
                <div class="driver-name">{leader['Driver']}</div>
                <div class="driver-team">{leader['Team']}</div>
                <div style="display:flex;gap:2rem;margin-top:1.5rem;">
                    <div><div class="stat-number">{int(leader['Points'])}</div><div class="stat-label">Points</div></div>
                    <div><div class="stat-number">{int(leader['Wins'])}</div><div class="stat-label">Wins</div></div>
                    <div><div class="stat-number">{int(leader['Position'])}</div><div class="stat-label">Position</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Top 5 <span>Drivers</span></div>', unsafe_allow_html=True)
        top5 = d25.head(5)
        colors = [TEAM_COLORS.get(t, '#e10600') for t in top5['Team']]
        fig = go.Figure(go.Bar(
            x=top5['Points'], y=top5['Driver'],
            orientation='h',
            marker=dict(color=colors),
            text=top5['Points'].astype(int),
            textposition='outside',
            textfont=dict(family='Orbitron', size=11, color='white'),
        ))
        apply_chart(fig, height=300)
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE: DRIVERS
# ════════════════════════════════════════════════════════════════
elif "Drivers" in page:
    st.markdown('<div class="section-header">Driver <span>Deep Dive</span></div>', unsafe_allow_html=True)

    drivers_list = d25['Driver'].tolist()
    selected_driver = st.selectbox("SELECT DRIVER", drivers_list)

    driver_info = d25[d25['Driver'] == selected_driver].iloc[0]
    driver_races = r25[r25['Driver'] == selected_driver].sort_values('Round').copy()
    team_color = TEAM_COLORS.get(driver_info['Team'], '#e10600')

    wins = int(driver_info['Wins'])
    podiums = len(driver_races[driver_races['Position'] <= 3])
    avg_finish = driver_races['Position'].mean()
    best_finish = int(driver_races['Position'].min())
    worst_finish = int(driver_races['Position'].max())

    st.markdown(f"""
    <div class="driver-card" style="border-left-color:{team_color}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <div class="driver-name">{selected_driver}</div>
                <div class="driver-team">{driver_info['Team']} · P{int(driver_info['Position'])} Championship</div>
            </div>
            <div style="display:flex;gap:2rem;flex-wrap:wrap;">
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{int(driver_info['Points'])}</div><div class="stat-label">Points</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{wins}</div><div class="stat-label">Wins</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{podiums}</div><div class="stat-label">Podiums</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{avg_finish:.1f}</div><div class="stat-label">Avg Finish</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{best_finish}</div><div class="stat-label">Best</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{worst_finish}</div><div class="stat-label">Worst</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Points <span>Progression</span></div>', unsafe_allow_html=True)
        driver_races['Cumulative'] = driver_races['Points'].cumsum()
        hex_color = team_color.lstrip('#')
        r_val, g_val, b_val = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        fig = go.Figure(go.Scatter(
            x=driver_races['Race_name'], y=driver_races['Cumulative'],
            mode='lines+markers',
            line=dict(color=team_color, width=3),
            marker=dict(size=8, color=team_color),
            fill='tozeroy',
            fillcolor=f'rgba({r_val},{g_val},{b_val},0.1)'
        ))
        apply_chart(fig, height=300)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Finish <span>Positions</span></div>', unsafe_allow_html=True)
        finish_counts = driver_races['Position'].value_counts().sort_index()
        position_colors = []
        for pos in finish_counts.index:
            if pos == 1:
                position_colors.append('#FFD700')
            elif pos <= 3:
                position_colors.append(team_color)
            elif pos <= 10:
                position_colors.append('rgba(255,255,255,0.3)')
            else:
                position_colors.append('rgba(255,255,255,0.1)')

        fig2 = go.Figure(go.Bar(
            x=[f'P{p}' for p in finish_counts.index],
            y=finish_counts.values,
            marker=dict(color=position_colors),
            text=finish_counts.values,
            textposition='outside',
            textfont=dict(family='Orbitron', size=12, color='white'),
        ))
        apply_chart(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Race by Race <span>Results</span></div>', unsafe_allow_html=True)
    display_df = driver_races[['Race_name', 'Round', 'Grid', 'Position', 'Points', 'Status']].copy()
    display_df.columns = ['Race', 'Round', 'Grid', 'Finish', 'Points', 'Status']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════
# PAGE: CONSTRUCTORS
# ════════════════════════════════════════════════════════════════
elif "Constructors" in page:
    st.markdown('<div class="section-header">Constructor <span>Standings</span> — 2025</div>', unsafe_allow_html=True)

    cols = st.columns(len(c25))
    for i, (_, row) in enumerate(c25.iterrows()):
        color = TEAM_COLORS.get(row['Team'], '#e10600')
        with cols[i]:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:{color}">
                <div style="font-family:'Orbitron',sans-serif;font-size:0.6rem;color:{color};letter-spacing:2px;">P{int(row['Position'])}</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;font-weight:600;margin:0.3rem 0;">{row['Team']}</div>
                <div class="stat-number" style="color:{color};font-size:1.5rem">{int(row['Points'])}</div>
                <div class="stat-label">pts</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Points <span>Comparison</span></div>', unsafe_allow_html=True)
        colors_c = [TEAM_COLORS.get(t, '#555') for t in c25['Team']]
        fig = go.Figure(go.Bar(
            x=c25['Points'], y=c25['Team'],
            orientation='h',
            marker=dict(color=colors_c),
            text=c25['Points'].astype(int),
            textposition='outside',
            textfont=dict(family='Orbitron', size=11, color='white'),
        ))
        apply_chart(fig, height=400)
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Points <span>Share</span></div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=c25['Team'], values=c25['Points'],
            marker=dict(colors=[TEAM_COLORS.get(t, '#555') for t in c25['Team']]),
            hole=0.6,
            textfont=dict(family='Rajdhani', size=11),
        ))
        apply_chart(fig2, height=400)
        fig2.update_layout(
            annotations=[dict(text='2025', x=0.5, y=0.5,
                             font=dict(family='Orbitron', size=18, color='white'),
                             showarrow=False)],
            legend=dict(font=dict(family='Rajdhani', size=11))
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">2024 vs 2025 <span>Battle</span></div>', unsafe_allow_html=True)
    merged = pd.merge(
        c24[['Team', 'Points']].rename(columns={'Points': '2024'}),
        c25[['Team', 'Points']].rename(columns={'Points': '2025'}),
        on='Team', how='outer'
    ).fillna(0)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='2024', x=merged['Team'], y=merged['2024'],
                         marker_color=[TEAM_COLORS.get(t, '#555') for t in merged['Team']], opacity=0.4))
    fig3.add_trace(go.Bar(name='2025', x=merged['Team'], y=merged['2025'],
                         marker_color=[TEAM_COLORS.get(t, '#555') for t in merged['Team']]))
    apply_chart(fig3, height=350, extra=dict(
        barmode='group',
        legend=dict(font=dict(family='Orbitron', size=10))
    ))
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE: RACE ANALYSIS
# ════════════════════════════════════════════════════════════════
elif "Race" in page:
    st.markdown('<div class="section-header">Race by Race <span>Analysis</span> — 2025</div>', unsafe_allow_html=True)

    top5_drivers = d25.head(5)['Driver'].tolist()
    r25_top = r25[r25['Driver'].isin(top5_drivers)].sort_values(['Driver', 'Round']).copy()
    r25_top['Cumulative'] = r25_top.groupby('Driver')['Points'].cumsum()

    fig = go.Figure()
    for driver in top5_drivers:
        df_d = r25_top[r25_top['Driver'] == driver]
        team = d25[d25['Driver'] == driver]['Team'].values
        color = TEAM_COLORS.get(team[0], '#e10600') if len(team) > 0 else '#e10600'
        fig.add_trace(go.Scatter(
            x=df_d['Race_name'], y=df_d['Cumulative'],
            name=driver, line=dict(color=color, width=2.5),
            mode='lines+markers', marker=dict(size=7),
        ))
    apply_chart(fig, height=400, extra=dict(
        legend=dict(font=dict(family='Rajdhani', size=12)),
        title=dict(text='Cumulative Points — Top 5 Drivers',
                  font=dict(family='Orbitron', size=13, color='rgba(255,255,255,0.6)'))
    ))
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Grid vs <span>Finish</span></div>', unsafe_allow_html=True)
        fig2 = px.scatter(r25, x='Grid', y='Position', color='Team',
                         color_discrete_map=TEAM_COLORS,
                         hover_data=['Driver', 'Race_name'])
        apply_chart(fig2, height=350)
        fig2.add_shape(type='line', x0=1, y0=1, x1=20, y1=20,
                      line=dict(color='rgba(255,255,255,0.15)', dash='dash'))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Points per <span>Race</span></div>', unsafe_allow_html=True)
        race_totals = r25.groupby('Race_name')['Points'].sum().reset_index().sort_values('Points', ascending=False)
        fig3 = go.Figure(go.Bar(
            x=race_totals['Race_name'], y=race_totals['Points'],
            marker=dict(color='#e10600', opacity=0.8),
        ))
        apply_chart(fig3, height=350)
        fig3.update_xaxes(tickangle=45)
        st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE: TEAM DEEP DIVE
# ════════════════════════════════════════════════════════════════
elif "Team" in page:
    st.markdown('<div class="section-header">Team <span>Deep Dive</span></div>', unsafe_allow_html=True)

    teams = sorted(r25['Team'].unique().tolist())
    selected_team = st.selectbox("SELECT TEAM", teams)
    team_color = TEAM_COLORS.get(selected_team, '#e10600')

    team_r = r25[r25['Team'] == selected_team]
    team_drivers = team_r['Driver'].unique().tolist()

    total_pts = team_r['Points'].sum()
    wins = len(team_r[team_r['Position'] == 1])
    podiums = len(team_r[team_r['Position'] <= 3])
    avg_pos = team_r['Position'].mean()

    st.markdown(f"""
    <div class="driver-card" style="border-left-color:{team_color}">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
            <div>
                <div class="driver-name" style="color:{team_color}">{selected_team}</div>
                <div class="driver-team">2025 Season</div>
            </div>
            <div style="display:flex;gap:2rem;flex-wrap:wrap;">
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{int(total_pts)}</div><div class="stat-label">Points</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{wins}</div><div class="stat-label">Wins</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{podiums}</div><div class="stat-label">Podiums</div></div>
                <div style="text-align:center"><div class="stat-number" style="color:{team_color}">{avg_pos:.1f}</div><div class="stat-label">Avg Finish</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Driver <span>Points</span></div>', unsafe_allow_html=True)
        driver_pts = team_r.groupby('Driver')['Points'].sum().reset_index()
        fig = go.Figure(go.Bar(
            x=driver_pts['Driver'], y=driver_pts['Points'],
            marker_color=team_color,
            text=driver_pts['Points'].astype(int),
            textposition='outside',
            textfont=dict(family='Orbitron', size=14, color='white'),
        ))
        apply_chart(fig, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Points <span>Split</span></div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=driver_pts['Driver'], values=driver_pts['Points'],
            marker=dict(colors=[team_color, 'rgba(255,255,255,0.2)']),
            hole=0.6,
        ))
        apply_chart(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Race <span>Positions</span> by Driver</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    driver_colors = [team_color, 'rgba(255,255,255,0.5)']
    for i, driver in enumerate(team_drivers):
        df_d = team_r[team_r['Driver'] == driver].sort_values('Round')
        fig3.add_trace(go.Scatter(
            x=df_d['Race_name'], y=df_d['Position'],
            name=driver, mode='lines+markers',
            line=dict(color=driver_colors[i % 2], width=2.5),
            marker=dict(size=8),
        ))
    apply_chart(fig3, height=350, extra=dict(legend=dict(font=dict(family='Rajdhani', size=12))))
    fig3.update_yaxes(autorange='reversed')
    fig3.update_xaxes(tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)