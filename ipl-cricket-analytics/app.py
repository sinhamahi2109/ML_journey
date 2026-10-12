import os
import sqlite3
import zipfile
import altair as alt
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & DATABASE INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="IPL Statistical Archive (2008–2025)",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ipl.db")
ZIP_PATH = os.path.join(BASE_DIR, "ipl.db.zip")

# On cloud servers only the zip may be uploaded; extract on first start
if not os.path.exists(DB_PATH) and os.path.exists(ZIP_PATH):
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(BASE_DIR)


@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_d_batsman ON deliveries(batsman)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_d_bowler ON deliveries(bowler)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_m_season ON matches(season)")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    return conn


@st.cache_data(show_spinner=False)
def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_connection(), params=params)


# ==============================================================================
# 2. DOMAIN CONSTANTS & EDITORIAL COLOR PALETTE
# ==============================================================================
NOT_BOWLER_WICKET = "('run out', 'retired hurt', 'retired out', 'obstructing the field')"
LEGAL_BALL = "(d.isWide IS NULL OR d.isWide = 0)"
BOWLER_LEGAL_BALL = "(d.isWide IS NULL OR d.isWide = 0) AND (d.isNoBall IS NULL OR d.isNoBall = 0)"

# Editorial Sports Journalism Palette (Turf Green, Seam Crimson, Willow Ochre, Warm Stone)
TURF_GREEN = "#0F3D2E"
TURF_MID = "#1B6B50"
TURF_LIGHT = "#529E82"
SEAM_CRIMSON = "#B8292F"
WILLOW_OCHRE = "#C27803"
INK_DARK = "#181816"
INK_MUTED = "#6B665E"
GRID_COLOR = "#E5E0D5"

# Muted, print-friendly franchise colors (no neon)
TEAM_COLORS = {
    "Mumbai Indians": "#1D4E89",
    "Chennai Super Kings": "#C88A04",
    "Royal Challengers Bangalore": "#A61C1C",
    "Kolkata Knight Riders": "#4A2E56",
    "Sunrisers Hyderabad": "#C85A17",
    "Rajasthan Royals": "#9E2A5B",
    "Delhi Capitals": "#26547C",
    "Punjab Kings": "#B8292F",
    "Gujarat Titans": "#0F3D2E",
    "Lucknow Super Giants": "#2B6CB0",
    "Deccan Chargers": "#4A5568",
    "Rising Pune Supergiant": "#6B46C1",
    "Gujarat Lions": "#C05621",
    "Pune Warriors": "#2C7A7B",
    "Kochi Tuskers Kerala": "#B7791F",
}

TEAM_ABBR = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Sunrisers Hyderabad": "SRH",
    "Rajasthan Royals": "RR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
    "Deccan Chargers": "DCH",
    "Rising Pune Supergiant": "RPS",
    "Gujarat Lions": "GL",
    "Pune Warriors": "PWI",
    "Kochi Tuskers Kerala": "KTK",
}

PHASE_FILTERS = {
    "All Overs (1–20)": "1=1",
    "Powerplay (Overs 1–6)": 'd."over" < 6',
    "Middle Overs (Overs 7–15)": 'd."over" >= 6 AND d."over" < 15',
    "Death Overs (Overs 16–20)": 'd."over" >= 15',
}


# ==============================================================================
# 3. EDITORIAL DESIGN SYSTEM (THE ATHLETIC / WISDEN INSPIRED)
# ==============================================================================
def inject_editorial_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&display=swap');

        /* Warm Newsprint / Alabaster Canvas */
        .stApp {
            background-color: #F6F4EF !important;
            color: #181816 !important;
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .block-container {
            padding-top: 1.75rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1380px !important;
        }

        /* Architectural Stone Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #EDE9E0 !important;
            border-right: 1px solid #D8D2C5 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #181816 !important;
        }

        /* Editorial Masthead */
        .masthead {
            border-top: 3px solid #181816;
            border-bottom: 3px double #181816;
            padding: 1.1rem 0 1.25rem 0;
            margin-bottom: 1.5rem;
            background: transparent;
        }
        .masthead-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #6B665E;
            padding-bottom: 0.65rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid #DFDBD0;
        }
        .masthead-kicker {
            color: #B8292F;
            font-weight: 600;
        }
        .masthead-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 2.35rem;
            font-weight: 700;
            color: #181816;
            letter-spacing: -0.02em;
            line-height: 1.12;
            margin: 0 0 0.4rem 0;
        }
        .masthead-deck {
            font-size: 0.98rem;
            color: #57534E;
            max-width: 880px;
            line-height: 1.5;
            margin: 0;
        }

        /* Editorial Stat Ledger Cards */
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #DFDBD0;
            border-top: 3px solid var(--rule-color, #0F3D2E);
            padding: 1rem 1.15rem;
            height: 100%;
        }
        .stat-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #6B665E;
            margin-bottom: 0.35rem;
        }
        .stat-figure {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: #181816;
            line-height: 1.1;
            margin-bottom: 0.3rem;
        }
        .stat-note {
            font-size: 0.76rem;
            color: #6B665E;
            border-top: 1px solid #F0EDE6;
            padding-top: 0.35rem;
        }
        .stat-note strong {
            color: #0F3D2E;
            font-weight: 600;
        }

        /* Editorial Section Subhead */
        .sec-head {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            border-top: 2px solid #181816;
            border-bottom: 1px solid #DFDBD0;
            padding: 0.55rem 0;
            margin: 1.6rem 0 0.9rem 0;
        }
        .sec-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.3rem;
            font-weight: 600;
            color: #181816;
            letter-spacing: -0.01em;
        }
        .sec-meta {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6B665E;
        }

        /* Editorial Note / Callout */
        .ed-note {
            background: #FFFFFF;
            border: 1px solid #DFDBD0;
            border-left: 4px solid #0F3D2E;
            padding: 0.85rem 1.15rem;
            margin: 1rem 0 1.25rem 0;
            font-size: 0.9rem;
            color: #292524;
            line-height: 1.5;
        }
        .ed-note strong {
            color: #0F3D2E;
        }

        /* Head-to-Head Ledger */
        .h2h-ledger {
            background: #FFFFFF;
            border: 1px solid #DFDBD0;
            border-top: 3px solid #181816;
            padding: 1.35rem 1.5rem;
            margin: 1rem 0 1.25rem 0;
        }
        .h2h-grid {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0.8rem;
        }
        .h2h-side-name {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6B665E;
        }
        .h2h-side-val {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 2rem;
            font-weight: 700;
            color: #181816;
        }
        .h2h-center-tag {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.74rem;
            color: #6B665E;
            background: #F6F4EF;
            border: 1px solid #DFDBD0;
            padding: 4px 12px;
        }
        .h2h-strip {
            width: 100%;
            height: 12px;
            background: #EDE9E0;
            display: flex;
            overflow: hidden;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            color: #57534E !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #0F3D2E !important;
        }

        /* Chart wrapper card */
        div[data-testid="stVegaLiteChart"] {
            background: #FFFFFF;
            border: 1px solid #DFDBD0;
            padding: 0.65rem 0.65rem 0.25rem 0.65rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_masthead(kicker: str, title: str, deck: str):
    st.markdown(
        f"""
        <div class="masthead">
            <div class="masthead-meta">
                <span class="masthead-kicker">{kicker}</span>
                <span>INDIAN PREMIER LEAGUE • 2008–2025 ARCHIVE • SQLITE3 + VEGA-LITE</span>
            </div>
            <h1 class="masthead-title">{title}</h1>
            <p class="masthead-deck">{deck}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(label: str, figure: str, highlight: str, note: str, rule_color: str = TURF_GREEN):
    st.markdown(
        f"""
        <div class="stat-card" style="--rule-color: {rule_color};">
            <div class="stat-label">{label}</div>
            <div class="stat-figure">{figure}</div>
            <div class="stat-note"><strong>{highlight}</strong> {note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_head(title: str, meta: str = ""):
    st.markdown(
        f"""
        <div class="sec-head">
            <div class="sec-title">{title}</div>
            <div class="sec-meta">{meta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_editorial_note(text_html: str):
    st.markdown(f'<div class="ed-note">{text_html}</div>', unsafe_allow_html=True)


def show_sql_drawer(sql_code: str, title: str = "Inspect SQL Query", force_open: bool = False):
    with st.expander(f"SQL Query — {title}", expanded=force_open):
        st.code(sql_code.strip(), language="sql")


def style_altair(chart: alt.Chart, height: int = 350) -> alt.Chart:
    return (
        chart.properties(height=height, background="#FFFFFF")
        .configure_axis(
            labelColor="#44403C",
            titleColor="#181816",
            labelFont="DM Sans, sans-serif",
            titleFont="IBM Plex Mono, monospace",
            titleFontWeight=600,
            labelFontSize=11,
            titleFontSize=10,
            gridColor="#EAE6DC",
            gridDash=[3, 3],
            domainColor="#C7C1B4",
            tickColor="#C7C1B4",
        )
        .configure_legend(
            labelColor="#44403C",
            titleColor="#181816",
            labelFont="DM Sans, sans-serif",
            titleFont="IBM Plex Mono, monospace",
            labelFontSize=11,
            titleFontSize=10,
        )
        .configure_view(strokeWidth=0)
    )


def add_rank_col(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.insert(0, "Rank", range(1, len(out) + 1))
    return out


# ==============================================================================
# 4. GLOBAL METADATA & SIDEBAR NAVIGATION
# ==============================================================================
inject_editorial_css()

seasons = run_query("SELECT DISTINCT season FROM matches ORDER BY season")["season"].tolist()
teams = (
    run_query("SELECT team1 AS team FROM matches UNION SELECT team2 FROM matches ORDER BY team")["team"]
    .dropna()
    .tolist()
)

with st.sidebar:
    st.markdown(
        """
        <div style="border-top: 3px solid #181816; border-bottom: 1px solid #C7C1B4; padding: 0.85rem 0; margin-bottom: 1rem;">
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.12em; color: #B8292F; text-transform: uppercase;">
                CRICKET DATA DESK
            </div>
            <div style="font-family: 'Newsreader', Georgia, serif; font-size: 1.55rem; font-weight: 700; color: #181816; line-height: 1.15; margin-top: 2px;">
                IPL Statistical Archive
            </div>
            <div style="font-size: 0.78rem; color: #57534E; margin-top: 4px;">
                18 Seasons (2008–2025) • Ball-by-Ball
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "SECTIONS",
        [
            "01 / Tournament Overview",
            "02 / Batting Records",
            "03 / Bowling Records",
            "04 / Franchises & Rivalries",
            "05 / Stadiums & Pitches",
            "06 / Player Matchups",
        ],
        index=0,
    )

    st.markdown("<hr style='border-color: #D8D2C5; margin: 1.1rem 0;'>", unsafe_allow_html=True)
    recruiter_sql_mode = st.toggle(
        "Show SQL Queries",
        value=False,
        help="Expand the underlying SQL queries (CTEs, Window Functions, Joins) below each section.",
    )

    st.markdown(
        """
        <div style="background: #F6F4EF; border: 1px solid #D8D2C5; padding: 0.8rem; margin-top: 1rem; font-size: 0.76rem; color: #57534E; line-height: 1.55;">
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 600; color: #181816; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">
                Technical Notes
            </div>
            <b>Database:</b> SQLite3 (<code>ipl.db</code>)<br>
            <b>Coverage:</b> 2007/08 – 2025<br>
            <b>SQL Features:</b> Common Table Expressions (<code>WITH</code>), Window Functions (<code>RANK() OVER</code>), Phase Aggregations
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# PAGE 1: TOURNAMENT OVERVIEW
# ==============================================================================
if page == "01 / Tournament Overview":
    render_masthead(
        "ISSUE 01 • MACRO TRENDS & SCORING EVOLUTION",
        "Eighteen Seasons of the Indian Premier League",
        "A comprehensive statistical ledger of every match and delivery bowled from 2008 through 2025, tracking run-rate inflation, boundary reliance, and phase-by-phase scoring tempo.",
    )

    overview_sql = """
        SELECT
            (SELECT COUNT(*) FROM matches) AS matches,
            (SELECT COUNT(DISTINCT season) FROM matches) AS seasons,
            (SELECT COUNT(DISTINCT venue) FROM matches) AS venues,
            (SELECT COUNT(*) FROM deliveries) AS balls,
            (SELECT SUM(batsman_runs + extras) FROM deliveries) AS total_runs,
            (SELECT SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) FROM deliveries) AS sixes,
            (SELECT SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END) FROM deliveries) AS fours,
            (SELECT COUNT(*) FROM deliveries WHERE dismissal_kind IS NOT NULL AND dismissal_kind <> '') AS total_wickets
    """
    totals = run_query(overview_sql).iloc[0]

    avg_runs_match = totals["total_runs"] / totals["matches"]
    boundary_runs = (totals["sixes"] * 6) + (totals["fours"] * 4)
    boundary_pct = (boundary_runs / totals["total_runs"]) * 100

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        render_stat_card("Matches Logged", f"{int(totals['matches']):,}", f"{int(totals['seasons'])} Seasons", "since 2008", TURF_GREEN)
    with k2:
        render_stat_card("Deliveries", f"{int(totals['balls']):,}", f"{int(totals['venues'])} Venues", "ball-by-ball", TURF_GREEN)
    with k3:
        render_stat_card("Aggregate Runs", f"{int(totals['total_runs']):,}", f"{avg_runs_match:.1f}", "runs per match", SEAM_CRIMSON)
    with k4:
        render_stat_card("Sixes Struck", f"{int(totals['sixes']):,}", f"{int(totals['fours']):,}", "fours hit", WILLOW_OCHRE)
    with k5:
        render_stat_card("Boundary Share", f"{boundary_pct:.1f}%", f"{int(boundary_runs):,}", "runs in 4s & 6s", TURF_GREEN)
    with k6:
        render_stat_card("Wickets Fallen", f"{int(totals['total_wickets']):,}", f"{totals['total_wickets']/totals['matches']:.1f}", "per fixture", SEAM_CRIMSON)

    season_sql = f"""
        SELECT
            m.season,
            COUNT(DISTINCT m.matchId) AS matches,
            SUM(d.batsman_runs + d.extras) AS total_runs,
            ROUND(SUM(d.batsman_runs + d.extras) * 1.0 / COUNT(DISTINCT m.matchId), 1) AS runs_per_match,
            ROUND(6.0 * SUM(d.batsman_runs + d.extras) /
                  SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END), 2) AS run_rate,
            ROUND(SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) * 1.0 / COUNT(DISTINCT m.matchId), 1) AS sixes_per_match
        FROM matches m
        JOIN deliveries d ON m.matchId = d.matchId
        GROUP BY m.season
        ORDER BY m.season
    """
    season_df = run_query(season_sql)
    peak_scoring = season_df.loc[season_df["runs_per_match"].idxmax()]

    render_editorial_note(
        f"<strong>Editorial Note:</strong> Scoring rates have accelerated sharply in the recent cycle, peaking in <strong>{peak_scoring['season']}</strong> at <strong>{peak_scoring['runs_per_match']} runs per match</strong> (overall run rate of <strong>{peak_scoring['run_rate']} RPO</strong> and <strong>{peak_scoring['sixes_per_match']} sixes per fixture</strong>)."
    )

    col_left, col_right = st.columns(2)

    with col_left:
        render_section_head("Average Runs per Match by Season", "DASHED LINE = 18-SEASON MEAN")
        mean_rpm = float(season_df["runs_per_match"].mean())

        area = (
            alt.Chart(season_df)
            .mark_area(
                line={"color": TURF_GREEN, "strokeWidth": 2.5},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color="rgba(15, 61, 46, 0.25)", offset=0),
                        alt.GradientStop(color="rgba(15, 61, 46, 0.02)", offset=1),
                    ],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                point=alt.OverlayMarkDef(color=TURF_GREEN, size=55, filled=True),
            )
            .encode(
                x=alt.X("season:N", title="SEASON", sort=None, axis=alt.Axis(labelAngle=-40)),
                y=alt.Y("runs_per_match:Q", title="AVG RUNS / MATCH", scale=alt.Scale(zero=False, padding=15)),
                tooltip=[
                    alt.Tooltip("season:N", title="Season"),
                    alt.Tooltip("matches:Q", title="Matches"),
                    alt.Tooltip("runs_per_match:Q", title="Avg Runs / Match"),
                    alt.Tooltip("run_rate:Q", title="Run Rate (RPO)"),
                    alt.Tooltip("sixes_per_match:Q", title="Sixes / Match"),
                ],
            )
        )
        rule = (
            alt.Chart(pd.DataFrame({"y": [mean_rpm]}))
            .mark_rule(color=SEAM_CRIMSON, strokeDash=[5, 4], strokeWidth=1.5)
            .encode(y="y:Q")
        )
        st.altair_chart(style_altair(area + rule, height=330), width="stretch")

    with col_right:
        render_section_head("Sixes Hit per Match Across Seasons", "POWER-HITTING PROGRESSION")
        bars = (
            alt.Chart(season_df)
            .mark_bar(color=SEAM_CRIMSON, cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
            .encode(
                x=alt.X("season:N", title="SEASON", sort=None, axis=alt.Axis(labelAngle=-40)),
                y=alt.Y("sixes_per_match:Q", title="SIXES / MATCH"),
                tooltip=[
                    alt.Tooltip("season:N", title="Season"),
                    alt.Tooltip("sixes_per_match:Q", title="Sixes / Match"),
                    alt.Tooltip("matches:Q", title="Matches Played"),
                    alt.Tooltip("total_runs:Q", title="Total Runs", format=","),
                ],
            )
        )
        text = bars.mark_text(dy=-7, color=INK_DARK, fontSize=10, fontWeight=600).encode(
            text=alt.Text("sixes_per_match:Q", format=".1f")
        )
        st.altair_chart(style_altair(bars + text, height=330), width="stretch")

    show_sql_drawer(season_sql, "Season-over-Season Scoring & Sixes Trend", recruiter_sql_mode)

    # Row 2: Phase Intelligence & Over-by-Over Worm
    c_phase, c_worm = st.columns(2)

    with c_phase:
        render_section_head("Run Rate & Boundary Share by Phase", "OVERS 1–6 vs 7–15 vs 16–20")
        phase_sql = f"""
            SELECT
                CASE
                    WHEN d."over" < 6 THEN '1. Powerplay (Overs 1–6)'
                    WHEN d."over" < 15 THEN '2. Middle (Overs 7–15)'
                    ELSE '3. Death (Overs 16–20)'
                END AS phase,
                COUNT(*) AS deliveries,
                SUM(d.batsman_runs + d.extras) AS total_runs,
                ROUND(6.0 * SUM(d.batsman_runs + d.extras) /
                      SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END), 2) AS run_rate,
                ROUND(100.0 * SUM(CASE WHEN d.batsman_runs IN (4, 6) THEN 1 ELSE 0 END) /
                      SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END), 1) AS boundary_ball_pct,
                ROUND(100.0 * SUM(CASE WHEN d.batsman_runs = 0 AND d.extras = 0 THEN 1 ELSE 0 END) /
                      COUNT(*), 1) AS dot_ball_pct,
                SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> '' THEN 1 ELSE 0 END) AS wickets
            FROM deliveries d
            WHERE d.inning IN (1, 2)
            GROUP BY phase
            ORDER BY phase
        """
        phase_df = run_query(phase_sql)

        phase_chart = (
            alt.Chart(phase_df)
            .mark_bar(height=38)
            .encode(
                x=alt.X("run_rate:Q", title="RUNS PER OVER (RPO)", scale=alt.Scale(domain=[0, 12])),
                y=alt.Y("phase:N", title=None, sort=None),
                color=alt.Color(
                    "phase:N",
                    scale=alt.Scale(range=[TURF_LIGHT, TURF_GREEN, SEAM_CRIMSON]),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("phase:N", title="Phase"),
                    alt.Tooltip("run_rate:Q", title="Run Rate (RPO)"),
                    alt.Tooltip("boundary_ball_pct:Q", title="Boundary Ball %"),
                    alt.Tooltip("dot_ball_pct:Q", title="Dot Ball %"),
                    alt.Tooltip("wickets:Q", title="Wickets Fallen", format=","),
                ],
            )
        )
        phase_labels = phase_chart.mark_text(align="left", dx=8, color=INK_DARK, fontWeight=700, fontSize=11).encode(
            text=alt.Text("run_rate:Q", format=".2f")
        )
        st.altair_chart(style_altair(phase_chart + phase_labels, height=205), width="stretch")
        st.dataframe(
            phase_df[["phase", "run_rate", "boundary_ball_pct", "dot_ball_pct", "wickets"]],
            hide_index=True,
            width="stretch",
            column_config={
                "phase": st.column_config.TextColumn("Innings Phase"),
                "run_rate": st.column_config.NumberColumn("Run Rate (RPO)", format="%.2f"),
                "boundary_ball_pct": st.column_config.ProgressColumn("Boundary Balls %", min_value=0, max_value=30, format="%.1f%%"),
                "dot_ball_pct": st.column_config.ProgressColumn("Dot Balls %", min_value=0, max_value=50, format="%.1f%%"),
                "wickets": st.column_config.NumberColumn("Wickets", format="%d"),
            },
        )
        show_sql_drawer(phase_sql, "Innings Phase Telemetry", recruiter_sql_mode)

    with c_worm:
        render_section_head("Over-by-Over Scoring Tempo (Overs 1 to 20)", "1ST INNINGS VS 2ND INNINGS")
        over_sql = f"""
            SELECT
                (d."over" + 1) AS over_num,
                CASE WHEN d.inning = 1 THEN '1st Innings (Setting)' ELSE '2nd Innings (Chasing)' END AS innings_type,
                ROUND(6.0 * SUM(d.batsman_runs + d.extras) /
                      SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END), 2) AS rpo
            FROM deliveries d
            WHERE d.inning IN (1, 2) AND d."over" BETWEEN 0 AND 19
            GROUP BY over_num, innings_type
            ORDER BY over_num
        """
        over_df = run_query(over_sql)

        worm_chart = (
            alt.Chart(over_df)
            .mark_line(point=alt.OverlayMarkDef(size=45), strokeWidth=2.5)
            .encode(
                x=alt.X("over_num:O", title="OVER NUMBER (1 TO 20)", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("rpo:Q", title="AVG RUNS PER OVER", scale=alt.Scale(zero=False, padding=10)),
                color=alt.Color(
                    "innings_type:N",
                    title="INNINGS",
                    scale=alt.Scale(range=[TURF_GREEN, SEAM_CRIMSON]),
                    legend=alt.Legend(orient="top"),
                ),
                tooltip=[
                    alt.Tooltip("over_num:O", title="Over #"),
                    alt.Tooltip("innings_type:N", title="Innings"),
                    alt.Tooltip("rpo:Q", title="Avg Runs / Over"),
                ],
            )
        )
        st.altair_chart(style_altair(worm_chart, height=345), width="stretch")
        show_sql_drawer(over_sql, "Over-by-Over Scoring Progression", recruiter_sql_mode)

    # Row 3: Season Honours Roll
    render_section_head("Season Honours Roll: Orange Cap & Purple Cap", "WINDOW FUNCTION: RANK() OVER (PARTITION BY SEASON)")
    honours_sql = f"""
        WITH bat_season AS (
            SELECT m.season, d.batsman, SUM(d.batsman_runs) AS runs,
                   RANK() OVER (PARTITION BY m.season ORDER BY SUM(d.batsman_runs) DESC) AS rnk
            FROM deliveries d JOIN matches m ON d.matchId = m.matchId
            GROUP BY m.season, d.batsman
        ),
        bowl_season AS (
            SELECT m.season, d.bowler, COUNT(*) AS wickets,
                   RANK() OVER (PARTITION BY m.season ORDER BY COUNT(*) DESC) AS rnk
            FROM deliveries d JOIN matches m ON d.matchId = m.matchId
            WHERE d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
              AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET}
            GROUP BY m.season, d.bowler
        )
        SELECT
            b.season AS Season,
            b.batsman AS "Leading Run-Scorer (Orange Cap)",
            b.runs AS "Runs",
            w.bowler AS "Leading Wicket-Taker (Purple Cap)",
            w.wickets AS "Wickets"
        FROM bat_season b
        JOIN bowl_season w ON b.season = w.season
        WHERE b.rnk = 1 AND w.rnk = 1
        ORDER BY b.season DESC
    """
    honours_df = run_query(honours_sql)

    h_col1, h_col2 = st.columns([1.45, 1])
    with h_col1:
        st.dataframe(
            honours_df,
            hide_index=True,
            width="stretch",
            height=350,
            column_config={
                "Runs": st.column_config.ProgressColumn("Runs", min_value=0, max_value=1000, format="%d"),
                "Wickets": st.column_config.ProgressColumn("Wickets", min_value=0, max_value=35, format="%d"),
            },
        )
    with h_col2:
        mvp_sql = """
            SELECT player_of_match AS player, COUNT(*) AS awards
            FROM matches
            WHERE player_of_match IS NOT NULL AND player_of_match <> ''
            GROUP BY player_of_match
            ORDER BY awards DESC
            LIMIT 10
        """
        mvp_df = run_query(mvp_sql)
        mvp_chart = (
            alt.Chart(mvp_df)
            .mark_bar(color=TURF_GREEN)
            .encode(
                x=alt.X("awards:Q", title="PLAYER OF THE MATCH AWARDS"),
                y=alt.Y("player:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("player:N", title="Player"),
                    alt.Tooltip("awards:Q", title="Awards"),
                ],
            )
        )
        mvp_lbl = mvp_chart.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(text="awards:Q")
        st.markdown("**Most Player of the Match Awards (2008–2025)**")
        st.altair_chart(style_altair(mvp_chart + mvp_lbl, height=315), width="stretch")

    show_sql_drawer(honours_sql, "CTE & Window Function for Season Leaders", recruiter_sql_mode)


# ==============================================================================
# PAGE 2: BATTING RECORDS
# ==============================================================================
elif page == "02 / Batting Records":
    render_masthead(
        "ISSUE 02 • BATTING TELEMETRY & STROKEPLAY",
        "Run Scorers, Boundary Power & Strike-Rate Quadrants",
        "Filter by season, franchise, and phase of the innings to evaluate high-volume anchors against high-strike-rate boundary hitters.",
    )

    f1, f2, f3, f4 = st.columns([1.2, 1.4, 1.3, 1.1])
    season = f1.selectbox("Season", ["All"] + seasons, index=0)
    phase_label = f2.selectbox("Innings Phase", list(PHASE_FILTERS.keys()), index=0)
    team_filter = f3.selectbox("Batting Franchise", ["All Teams"] + teams, index=0)
    top_n = f4.slider("Players Displayed", 5, 25, 12)

    phase_cond = PHASE_FILTERS[phase_label]

    bat_leader_sql = f"""
        SELECT
            d.batsman,
            COUNT(DISTINCT d.matchId) AS innings,
            SUM(d.batsman_runs) AS runs,
            SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) AS balls,
            ROUND(100.0 * SUM(d.batsman_runs) / NULLIF(SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END), 0), 2) AS strike_rate,
            SUM(CASE WHEN d.batsman_runs = 4 THEN 1 ELSE 0 END) AS fours,
            SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes,
            ROUND(100.0 * SUM(CASE WHEN d.batsman_runs IN (4, 6) THEN d.batsman_runs ELSE 0 END) /
                  NULLIF(SUM(d.batsman_runs), 0), 1) AS boundary_run_pct
        FROM deliveries d
        JOIN matches m ON d.matchId = m.matchId
        WHERE (? = 'All' OR m.season = ?)
          AND (? = 'All Teams' OR d.batting_team = ?)
          AND ({phase_cond})
        GROUP BY d.batsman
        ORDER BY runs DESC
        LIMIT ?
    """
    runs_df = run_query(bat_leader_sql, (season, season, team_filter, team_filter, top_n))

    if not runs_df.empty:
        top_batter = runs_df.iloc[0]
        best_sr_row = runs_df.loc[runs_df["strike_rate"].idxmax()]
        most_6s_row = runs_df.loc[runs_df["sixes"].idxmax()]
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            render_stat_card("Leading Run-Scorer", top_batter["batsman"], f"{int(top_batter['runs']):,} runs", f"across {int(top_batter['innings'])} innings", TURF_GREEN)
        with b2:
            render_stat_card("Fastest Scorer (Top N)", best_sr_row["batsman"], f"{best_sr_row['strike_rate']} SR", f"({int(best_sr_row['runs']):,} runs)", SEAM_CRIMSON)
        with b3:
            render_stat_card("Most Sixes (Top N)", most_6s_row["batsman"], f"{int(most_6s_row['sixes'])} sixes", f"& {int(most_6s_row['fours'])} fours", WILLOW_OCHRE)
        with b4:
            render_stat_card("Boundary Run Share", f"{runs_df['boundary_run_pct'].mean():.1f}%", "Top-N Mean", "of runs via 4s & 6s", TURF_GREEN)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Most Runs",
            "Sixes & Boundary Efficiency",
            "Strike Rate & Volume Quadrant",
            "Highest Innings & Season Leaders",
        ]
    )

    with tab1:
        c_chart, c_table = st.columns([1.15, 1.25])
        with c_chart:
            render_section_head(f"Top {top_n} Run Scorers ({season})", phase_label)
            bar = (
                alt.Chart(runs_df)
                .mark_bar(color=TURF_GREEN)
                .encode(
                    x=alt.X("runs:Q", title="TOTAL RUNS"),
                    y=alt.Y("batsman:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("batsman:N", title="Batter"),
                        alt.Tooltip("runs:Q", title="Runs", format=","),
                        alt.Tooltip("innings:Q", title="Innings"),
                        alt.Tooltip("balls:Q", title="Balls Faced", format=","),
                        alt.Tooltip("strike_rate:Q", title="Strike Rate"),
                        alt.Tooltip("fours:Q", title="Fours"),
                        alt.Tooltip("sixes:Q", title="Sixes"),
                    ],
                )
            )
            lbl = bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600, fontSize=11).encode(
                text=alt.Text("runs:Q", format=",")
            )
            st.altair_chart(style_altair(bar + lbl, height=max(340, top_n * 28)), width="stretch")

        with c_table:
            render_section_head("Batting Ledger", "SORTABLE TABLE")
            max_runs_val = int(runs_df["runs"].max()) if not runs_df.empty else 1000
            st.dataframe(
                add_rank_col(runs_df),
                hide_index=True,
                width="stretch",
                height=max(340, top_n * 28),
                column_config={
                    "Rank": st.column_config.NumberColumn("#", width="small"),
                    "batsman": st.column_config.TextColumn("Batter"),
                    "innings": st.column_config.NumberColumn("Inn", format="%d"),
                    "runs": st.column_config.ProgressColumn("Runs", min_value=0, max_value=max_runs_val, format="%d"),
                    "balls": st.column_config.NumberColumn("Balls", format="%d"),
                    "strike_rate": st.column_config.NumberColumn("SR", format="%.2f"),
                    "fours": st.column_config.NumberColumn("4s", format="%d"),
                    "sixes": st.column_config.NumberColumn("6s", format="%d"),
                    "boundary_run_pct": st.column_config.NumberColumn("Bnd %", format="%.1f%%"),
                },
            )
        show_sql_drawer(bat_leader_sql, "Multi-Filter Batting Leaderboard", recruiter_sql_mode)

    with tab2:
        sixes_sql = f"""
            SELECT
                d.batsman,
                COUNT(CASE WHEN d.batsman_runs = 6 THEN 1 END) AS sixes,
                COUNT(CASE WHEN d.batsman_runs = 4 THEN 1 END) AS fours,
                SUM(d.batsman_runs) AS runs,
                SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) AS balls,
                ROUND(1.0 * SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) /
                      NULLIF(COUNT(CASE WHEN d.batsman_runs = 6 THEN 1 END), 0), 1) AS balls_per_six
            FROM deliveries d
            JOIN matches m ON d.matchId = m.matchId
            WHERE (? = 'All' OR m.season = ?)
              AND (? = 'All Teams' OR d.batting_team = ?)
              AND ({phase_cond})
            GROUP BY d.batsman
            HAVING sixes > 0
            ORDER BY sixes DESC
            LIMIT ?
        """
        sixes_df = run_query(sixes_sql, (season, season, team_filter, team_filter, top_n))

        sc1, sc2 = st.columns([1.15, 1.25])
        with sc1:
            render_section_head(f"Most Sixes Hit ({season})", phase_label)
            s_bar = (
                alt.Chart(sixes_df)
                .mark_bar(color=SEAM_CRIMSON)
                .encode(
                    x=alt.X("sixes:Q", title="SIXES HIT (6s)"),
                    y=alt.Y("batsman:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("batsman:N", title="Batter"),
                        alt.Tooltip("sixes:Q", title="Sixes"),
                        alt.Tooltip("fours:Q", title="Fours"),
                        alt.Tooltip("balls_per_six:Q", title="Balls per Six"),
                        alt.Tooltip("runs:Q", title="Total Runs", format=","),
                    ],
                )
            )
            s_lbl = s_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(text="sixes:Q")
            st.altair_chart(style_altair(s_bar + s_lbl, height=max(340, top_n * 28)), width="stretch")
        with sc2:
            render_section_head("Balls per Six & Boundary Breakdown", "POWER EFFICIENCY")
            max_six_val = int(sixes_df["sixes"].max()) if not sixes_df.empty else 100
            st.dataframe(
                add_rank_col(sixes_df),
                hide_index=True,
                width="stretch",
                height=max(340, top_n * 28),
                column_config={
                    "Rank": st.column_config.NumberColumn("#", width="small"),
                    "batsman": st.column_config.TextColumn("Batter"),
                    "sixes": st.column_config.ProgressColumn("Sixes (6s)", min_value=0, max_value=max_six_val, format="%d"),
                    "fours": st.column_config.NumberColumn("Fours (4s)", format="%d"),
                    "runs": st.column_config.NumberColumn("Total Runs", format="%d"),
                    "balls": st.column_config.NumberColumn("Balls Faced", format="%d"),
                    "balls_per_six": st.column_config.NumberColumn("Balls / Six", format="%.1f"),
                },
            )
        show_sql_drawer(sixes_sql, "Six-Hitting & Balls-per-Six Query", recruiter_sql_mode)

    with tab3:
        default_min_balls = 300 if (season == "All" and phase_label == "All Overs (1–20)" and team_filter == "All Teams") else 60
        min_balls = st.slider("Minimum Legal Balls Faced", 20, 1000, default_min_balls, step=20)
        sr_sql = f"""
            SELECT
                d.batsman,
                SUM(d.batsman_runs) AS runs,
                COUNT(*) AS balls,
                ROUND(100.0 * SUM(d.batsman_runs) / COUNT(*), 2) AS strike_rate,
                SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes,
                SUM(CASE WHEN d.batsman_runs = 4 THEN 1 ELSE 0 END) AS fours
            FROM deliveries d
            JOIN matches m ON d.matchId = m.matchId
            WHERE {LEGAL_BALL}
              AND (? = 'All' OR m.season = ?)
              AND (? = 'All Teams' OR d.batting_team = ?)
              AND ({phase_cond})
            GROUP BY d.batsman
            HAVING COUNT(*) >= ?
            ORDER BY strike_rate DESC
            LIMIT ?
        """
        sr_df = run_query(sr_sql, (season, season, team_filter, team_filter, min_balls, top_n))

        q1, q2 = st.columns(2)
        with q1:
            render_section_head(f"Best Strike Rate (Min {min_balls} Balls)", "RUNS PER 100 BALLS")
            sr_bar = (
                alt.Chart(sr_df)
                .mark_bar(color=WILLOW_OCHRE)
                .encode(
                    x=alt.X("strike_rate:Q", title="STRIKE RATE", scale=alt.Scale(zero=False)),
                    y=alt.Y("batsman:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("batsman:N", title="Batter"),
                        alt.Tooltip("strike_rate:Q", title="Strike Rate"),
                        alt.Tooltip("runs:Q", title="Runs", format=","),
                        alt.Tooltip("balls:Q", title="Balls", format=","),
                        alt.Tooltip("sixes:Q", title="Sixes"),
                    ],
                )
            )
            sr_lbl = sr_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(
                text=alt.Text("strike_rate:Q", format=".1f")
            )
            st.altair_chart(style_altair(sr_bar + sr_lbl, height=350), width="stretch")

        with q2:
            render_section_head("Volume vs Tempo Quadrant", "CIRCLE SIZE = SIXES HIT")
            if not sr_df.empty:
                mean_r = float(sr_df["runs"].mean())
                mean_s = float(sr_df["strike_rate"].mean())
                scatter = (
                    alt.Chart(sr_df)
                    .mark_circle(opacity=0.82, color=TURF_GREEN, stroke="#FFFFFF", strokeWidth=1.2)
                    .encode(
                        x=alt.X("runs:Q", title="RUNS SCORED", scale=alt.Scale(zero=False, padding=15)),
                        y=alt.Y("strike_rate:Q", title="STRIKE RATE", scale=alt.Scale(zero=False, padding=15)),
                        size=alt.Size("sixes:Q", title="Sixes", scale=alt.Scale(range=[80, 650])),
                        tooltip=[
                            alt.Tooltip("batsman:N", title="Batter"),
                            alt.Tooltip("runs:Q", title="Runs", format=","),
                            alt.Tooltip("balls:Q", title="Balls Faced", format=","),
                            alt.Tooltip("strike_rate:Q", title="Strike Rate"),
                            alt.Tooltip("sixes:Q", title="Sixes"),
                        ],
                    )
                )
                txt = (
                    alt.Chart(sr_df.head(10))
                    .mark_text(dy=-11, color=INK_DARK, fontSize=10, fontWeight=600)
                    .encode(x="runs:Q", y="strike_rate:Q", text="batsman:N")
                )
                vline = alt.Chart(pd.DataFrame({"x": [mean_r]})).mark_rule(strokeDash=[4, 4], color=SEAM_CRIMSON).encode(x="x:Q")
                hline = alt.Chart(pd.DataFrame({"y": [mean_s]})).mark_rule(strokeDash=[4, 4], color=SEAM_CRIMSON).encode(y="y:Q")
                st.altair_chart(style_altair(vline + hline + scatter + txt, height=350), width="stretch")

        st.dataframe(add_rank_col(sr_df), hide_index=True, width="stretch")
        show_sql_drawer(sr_sql, "Strike Rate Qualification Query", recruiter_sql_mode)

    with tab4:
        ic1, ic2 = st.columns(2)
        with ic1:
            render_section_head("Top 15 Individual Innings Scores", "SINGLE-MATCH RECORDS")
            high_inn_sql = f"""
                SELECT
                    d.batsman AS Batter,
                    SUM(d.batsman_runs) AS Runs,
                    SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) AS Balls,
                    ROUND(100.0 * SUM(d.batsman_runs) / NULLIF(SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END), 0), 1) AS SR,
                    SUM(CASE WHEN d.batsman_runs = 4 THEN 1 ELSE 0 END) AS "4s",
                    SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) AS "6s",
                    d.batting_team AS Team,
                    d.bowling_team AS Opponent,
                    m.season AS Season
                FROM deliveries d
                JOIN matches m ON d.matchId = m.matchId
                WHERE (? = 'All' OR m.season = ?)
                GROUP BY d.matchId, d.batsman, d.batting_team, d.bowling_team, m.season
                ORDER BY Runs DESC
                LIMIT 15
            """
            high_inn_df = run_query(high_inn_sql, (season, season))
            st.dataframe(
                add_rank_col(high_inn_df),
                hide_index=True,
                width="stretch",
                height=420,
                column_config={
                    "Rank": st.column_config.NumberColumn("#", width="small"),
                    "Runs": st.column_config.ProgressColumn("Runs", min_value=0, max_value=175, format="%d"),
                    "SR": st.column_config.NumberColumn("SR", format="%.1f"),
                },
            )
            show_sql_drawer(high_inn_sql, "Highest Individual Innings Scores", recruiter_sql_mode)

        with ic2:
            render_section_head("Top Run-Scorer of Every Season", "RANK() OVER (PARTITION BY SEASON)")
            orange_sql = """
                WITH season_runs AS (
                    SELECT m.season, d.batsman, SUM(d.batsman_runs) AS runs,
                           ROUND(100.0 * SUM(d.batsman_runs) /
                                 SUM(CASE WHEN (d.isWide IS NULL OR d.isWide = 0) THEN 1 ELSE 0 END), 1) AS sr
                    FROM deliveries d JOIN matches m ON d.matchId = m.matchId
                    GROUP BY m.season, d.batsman
                ), ranked AS (
                    SELECT season, batsman, runs, sr,
                           RANK() OVER (PARTITION BY season ORDER BY runs DESC) AS rnk
                    FROM season_runs
                )
                SELECT season AS Season, batsman AS Batter, runs AS Runs, sr AS "Strike Rate"
                FROM ranked WHERE rnk = 1 ORDER BY Season DESC
            """
            orange_df = run_query(orange_sql)
            st.dataframe(
                orange_df,
                hide_index=True,
                width="stretch",
                height=420,
                column_config={
                    "Runs": st.column_config.ProgressColumn("Runs", min_value=0, max_value=1000, format="%d"),
                },
            )
            show_sql_drawer(orange_sql, "Season Orange Cap Winners (Window Function)", recruiter_sql_mode)


# ==============================================================================
# PAGE 3: BOWLING RECORDS
# ==============================================================================
elif page == "03 / Bowling Records":
    render_masthead(
        "ISSUE 03 • BOWLING ANALYSIS & WICKET-TAKING",
        "Strike Bowlers, Death Specialists & Economy Control",
        "Examine wicket-taking efficiency, death-over containment (overs 16–20), dot-ball pressure, and modes of dismissal.",
    )

    f1, f2, f3, f4 = st.columns([1.2, 1.4, 1.3, 1.1])
    season = f1.selectbox("Season", ["All"] + seasons, index=0)
    phase_label = f2.selectbox("Innings Phase", list(PHASE_FILTERS.keys()), index=0)
    team_filter = f3.selectbox("Bowling Franchise", ["All Teams"] + teams, index=0)
    top_n = f4.slider("Bowlers Displayed", 5, 25, 12)

    phase_cond = PHASE_FILTERS[phase_label]

    bowl_sql = f"""
        SELECT
            d.bowler,
            COUNT(DISTINCT d.matchId) AS matches,
            SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                      AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET} THEN 1 ELSE 0 END) AS wickets,
            SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END) AS legal_balls,
            SUM(d.batsman_runs + d.extras) AS runs_conceded,
            ROUND(6.0 * SUM(d.batsman_runs + d.extras) /
                  NULLIF(SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END), 0), 2) AS economy,
            ROUND(1.0 * SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END) /
                  NULLIF(SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                              AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET} THEN 1 ELSE 0 END), 0), 1) AS bowling_sr,
            ROUND(100.0 * SUM(CASE WHEN d.batsman_runs = 0 AND d.extras = 0 THEN 1 ELSE 0 END) /
                  COUNT(*), 1) AS dot_pct
        FROM deliveries d
        JOIN matches m ON d.matchId = m.matchId
        WHERE (? = 'All' OR m.season = ?)
          AND (? = 'All Teams' OR d.bowling_team = ?)
          AND ({phase_cond})
        GROUP BY d.bowler
        ORDER BY wickets DESC, economy ASC
        LIMIT ?
    """
    bowl_df = run_query(bowl_sql, (season, season, team_filter, team_filter, top_n))

    if not bowl_df.empty:
        top_w = bowl_df.iloc[0]
        best_econ = bowl_df.loc[bowl_df["economy"].idxmin()]
        best_sr = bowl_df.loc[bowl_df["bowling_sr"].idxmin()]
        best_dot = bowl_df.loc[bowl_df["dot_pct"].idxmax()]
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_stat_card("Leading Wicket-Taker", top_w["bowler"], f"{int(top_w['wickets'])} wickets", f"in {int(top_w['matches'])} matches", TURF_GREEN)
        with k2:
            render_stat_card("Lowest Economy (Top N)", best_econ["bowler"], f"{best_econ['economy']} RPO", f"({int(best_econ['wickets'])} wickets)", SEAM_CRIMSON)
        with k3:
            render_stat_card("Best Strike Rate (Top N)", best_sr["bowler"], f"{best_sr['bowling_sr']} balls/wkt", f"({int(best_sr['wickets'])} wickets)", WILLOW_OCHRE)
        with k4:
            render_stat_card("Highest Dot Share", best_dot["bowler"], f"{best_dot['dot_pct']}% dots", "scoreless deliveries", TURF_GREEN)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Most Wickets",
            "Death-Over Specialists (16–20)",
            "Dot Balls & Economy Matrix",
            "Dismissal Types & Season Leaders",
        ]
    )

    with tab1:
        bc1, bc2 = st.columns([1.15, 1.25])
        with bc1:
            render_section_head(f"Top {top_n} Wicket-Takers ({season})", phase_label)
            w_bar = (
                alt.Chart(bowl_df)
                .mark_bar(color=TURF_GREEN)
                .encode(
                    x=alt.X("wickets:Q", title="WICKETS TAKEN (EXCL. RUN OUTS)"),
                    y=alt.Y("bowler:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("bowler:N", title="Bowler"),
                        alt.Tooltip("wickets:Q", title="Wickets"),
                        alt.Tooltip("matches:Q", title="Matches"),
                        alt.Tooltip("economy:Q", title="Economy (RPO)"),
                        alt.Tooltip("bowling_sr:Q", title="Bowling SR"),
                        alt.Tooltip("dot_pct:Q", title="Dot Ball %"),
                    ],
                )
            )
            w_lbl = w_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(text="wickets:Q")
            st.altair_chart(style_altair(w_bar + w_lbl, height=max(340, top_n * 28)), width="stretch")

        with bc2:
            render_section_head("Bowling Ledger", "ECONOMY & STRIKE RATE")
            max_w_val = int(bowl_df["wickets"].max()) if not bowl_df.empty else 250
            st.dataframe(
                add_rank_col(bowl_df),
                hide_index=True,
                width="stretch",
                height=max(340, top_n * 28),
                column_config={
                    "Rank": st.column_config.NumberColumn("#", width="small"),
                    "bowler": st.column_config.TextColumn("Bowler"),
                    "matches": st.column_config.NumberColumn("Mat", format="%d"),
                    "wickets": st.column_config.ProgressColumn("Wickets", min_value=0, max_value=max_w_val, format="%d"),
                    "legal_balls": st.column_config.NumberColumn("Balls", format="%d"),
                    "runs_conceded": st.column_config.NumberColumn("Runs", format="%d"),
                    "economy": st.column_config.NumberColumn("Econ", format="%.2f"),
                    "bowling_sr": st.column_config.NumberColumn("SR", format="%.1f"),
                    "dot_pct": st.column_config.NumberColumn("Dot %", format="%.1f%%"),
                },
            )
        show_sql_drawer(bowl_sql, "Multi-Filter Bowling Leaderboard", recruiter_sql_mode)

    with tab2:
        death_sql = f"""
            SELECT
                d.bowler,
                COUNT(DISTINCT d.matchId) AS matches,
                SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                          AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET} THEN 1 ELSE 0 END) AS death_wickets,
                SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END) AS death_balls,
                ROUND(6.0 * SUM(d.batsman_runs + d.extras) /
                      NULLIF(SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END), 0), 2) AS death_economy,
                ROUND(100.0 * SUM(CASE WHEN d.batsman_runs = 0 AND d.extras = 0 THEN 1 ELSE 0 END) /
                      COUNT(*), 1) AS death_dot_pct
            FROM deliveries d
            JOIN matches m ON d.matchId = m.matchId
            WHERE d."over" >= 15
              AND (? = 'All' OR m.season = ?)
              AND (? = 'All Teams' OR d.bowling_team = ?)
            GROUP BY d.bowler
            HAVING death_wickets > 0
            ORDER BY death_wickets DESC, death_economy ASC
            LIMIT ?
        """
        death_df = run_query(death_sql, (season, season, team_filter, team_filter, top_n))

        dc1, dc2 = st.columns([1.15, 1.25])
        with dc1:
            render_section_head(f"Death-Over Wickets (Overs 16–20 • {season})", "CLOSING OVERS")
            d_bar = (
                alt.Chart(death_df)
                .mark_bar(color=SEAM_CRIMSON)
                .encode(
                    x=alt.X("death_wickets:Q", title="DEATH-OVER WICKETS (OVERS 16–20)"),
                    y=alt.Y("bowler:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("bowler:N", title="Bowler"),
                        alt.Tooltip("death_wickets:Q", title="Death Wickets"),
                        alt.Tooltip("death_economy:Q", title="Death Economy"),
                        alt.Tooltip("death_dot_pct:Q", title="Death Dot %"),
                    ],
                )
            )
            d_lbl = d_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(text="death_wickets:Q")
            st.altair_chart(style_altair(d_bar + d_lbl, height=max(340, top_n * 28)), width="stretch")
        with dc2:
            render_section_head("Death Overs Scorecard", "OVERS 16–20")
            max_dw = int(death_df["death_wickets"].max()) if not death_df.empty else 120
            st.dataframe(
                add_rank_col(death_df),
                hide_index=True,
                width="stretch",
                height=max(340, top_n * 28),
                column_config={
                    "Rank": st.column_config.NumberColumn("#", width="small"),
                    "bowler": st.column_config.TextColumn("Bowler"),
                    "matches": st.column_config.NumberColumn("Innings", format="%d"),
                    "death_wickets": st.column_config.ProgressColumn("Death Wkts", min_value=0, max_value=max_dw, format="%d"),
                    "death_balls": st.column_config.NumberColumn("Balls", format="%d"),
                    "death_economy": st.column_config.NumberColumn("Death Econ", format="%.2f"),
                    "death_dot_pct": st.column_config.NumberColumn("Dot %", format="%.1f%%"),
                },
            )
        show_sql_drawer(death_sql, "Death-Over Specialists Query", recruiter_sql_mode)

    with tab3:
        dot_sql = f"""
            SELECT
                d.bowler,
                SUM(CASE WHEN d.batsman_runs = 0 AND d.extras = 0 THEN 1 ELSE 0 END) AS dot_balls,
                COUNT(*) AS total_deliveries,
                ROUND(100.0 * SUM(CASE WHEN d.batsman_runs = 0 AND d.extras = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS dot_pct,
                ROUND(6.0 * SUM(d.batsman_runs + d.extras) /
                      NULLIF(SUM(CASE WHEN {BOWLER_LEGAL_BALL} THEN 1 ELSE 0 END), 0), 2) AS economy,
                SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                          AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET} THEN 1 ELSE 0 END) AS wickets
            FROM deliveries d
            JOIN matches m ON d.matchId = m.matchId
            WHERE (? = 'All' OR m.season = ?)
              AND (? = 'All Teams' OR d.bowling_team = ?)
              AND ({phase_cond})
            GROUP BY d.bowler
            ORDER BY dot_balls DESC
            LIMIT ?
        """
        dot_df = run_query(dot_sql, (season, season, team_filter, team_filter, top_n))

        mc1, mc2 = st.columns(2)
        with mc1:
            render_section_head("Most Dot Balls Bowled", "SCORELESS DELIVERIES")
            dot_bar = (
                alt.Chart(dot_df)
                .mark_bar(color=TURF_MID)
                .encode(
                    x=alt.X("dot_balls:Q", title="TOTAL DOT BALLS"),
                    y=alt.Y("bowler:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("bowler:N", title="Bowler"),
                        alt.Tooltip("dot_balls:Q", title="Dot Balls", format=","),
                        alt.Tooltip("dot_pct:Q", title="Dot Ball %"),
                        alt.Tooltip("economy:Q", title="Economy"),
                        alt.Tooltip("wickets:Q", title="Wickets"),
                    ],
                )
            )
            dot_lbl = dot_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(
                text=alt.Text("dot_balls:Q", format=",")
            )
            st.altair_chart(style_altair(dot_bar + dot_lbl, height=350), width="stretch")

        with mc2:
            render_section_head("Control vs Threat: Economy vs Wickets", "CIRCLE SIZE = DOT BALL %")
            if not bowl_df.empty:
                b_scat = (
                    alt.Chart(bowl_df)
                    .mark_circle(opacity=0.85, color=SEAM_CRIMSON, stroke="#FFFFFF", strokeWidth=1.2)
                    .encode(
                        x=alt.X("wickets:Q", title="WICKETS TAKEN", scale=alt.Scale(zero=False, padding=15)),
                        y=alt.Y("economy:Q", title="ECONOMY RATE (LOWER IS BETTER)", scale=alt.Scale(zero=False, padding=15)),
                        size=alt.Size("dot_pct:Q", title="Dot %", scale=alt.Scale(range=[100, 600])),
                        tooltip=[
                            alt.Tooltip("bowler:N", title="Bowler"),
                            alt.Tooltip("wickets:Q", title="Wickets"),
                            alt.Tooltip("economy:Q", title="Economy"),
                            alt.Tooltip("bowling_sr:Q", title="Bowling SR"),
                            alt.Tooltip("dot_pct:Q", title="Dot Ball %"),
                        ],
                    )
                )
                b_txt = (
                    alt.Chart(bowl_df.head(10))
                    .mark_text(dy=-11, color=INK_DARK, fontSize=10, fontWeight=600)
                    .encode(x="wickets:Q", y="economy:Q", text="bowler:N")
                )
                st.altair_chart(style_altair(b_scat + b_txt, height=350), width="stretch")

        st.dataframe(add_rank_col(dot_df), hide_index=True, width="stretch")
        show_sql_drawer(dot_sql, "Dot Balls & Pressure Percentage", recruiter_sql_mode)

    with tab4:
        dm1, dm2 = st.columns(2)
        with dm1:
            render_section_head("Modes of Dismissal", "SHARE OF TOTAL WICKETS")
            dism_sql = """
                SELECT
                    dismissal_kind AS dismissal_type,
                    COUNT(*) AS count,
                    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
                FROM deliveries d
                JOIN matches m ON d.matchId = m.matchId
                WHERE d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                  AND (? = 'All' OR m.season = ?)
                GROUP BY dismissal_kind
                ORDER BY count DESC
            """
            dism_df = run_query(dism_sql, (season, season))
            dism_chart = (
                alt.Chart(dism_df)
                .mark_bar(color=TURF_GREEN)
                .encode(
                    x=alt.X("count:Q", title="TOTAL DISMISSALS"),
                    y=alt.Y("dismissal_type:N", sort="-x", title=None),
                    tooltip=[
                        alt.Tooltip("dismissal_type:N", title="Dismissal Mode"),
                        alt.Tooltip("count:Q", title="Wickets", format=","),
                        alt.Tooltip("share_pct:Q", title="Share %"),
                    ],
                )
            )
            st.altair_chart(style_altair(dism_chart, height=340), width="stretch")
            show_sql_drawer(dism_sql, "Dismissal Mode Distribution", recruiter_sql_mode)

        with dm2:
            render_section_head("Leading Wicket-Taker of Every Season", "RANK() OVER (PARTITION BY SEASON)")
            purple_sql = f"""
                WITH season_wkts AS (
                    SELECT m.season, d.bowler, COUNT(*) AS wickets
                    FROM deliveries d JOIN matches m ON d.matchId = m.matchId
                    WHERE d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                      AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET}
                    GROUP BY m.season, d.bowler
                ), ranked AS (
                    SELECT season, bowler, wickets,
                           RANK() OVER (PARTITION BY season ORDER BY wickets DESC) AS rnk
                    FROM season_wkts
                )
                SELECT season AS Season, bowler AS Bowler, wickets AS Wickets
                FROM ranked WHERE rnk = 1 ORDER BY Season DESC
            """
            purple_df = run_query(purple_sql)
            st.dataframe(
                purple_df,
                hide_index=True,
                width="stretch",
                height=340,
                column_config={
                    "Wickets": st.column_config.ProgressColumn("Wickets", min_value=0, max_value=35, format="%d"),
                },
            )
            show_sql_drawer(purple_sql, "Season Purple Cap Winners (Window Function)", recruiter_sql_mode)


# ==============================================================================
# PAGE 4: FRANCHISES & RIVALRIES
# ==============================================================================
elif page == "04 / Franchises & Rivalries":
    render_masthead(
        "ISSUE 04 • FRANCHISE STANDINGS & HEAD-TO-HEAD ARCHIVE",
        "All-Time Win Percentages, Rivalries & Toss Impact",
        "Compare historical franchise win rates, inspect direct head-to-head series records, and evaluate the statistical value of the toss.",
    )

    render_section_head("Franchise Win Percentage Standings", "UNION ALL + CONDITIONAL AGGREGATION")
    min_played = st.slider("Minimum Matches Played by Franchise", 10, 120, 45, step=5)

    team_win_sql = """
        SELECT
            t.team,
            COUNT(*) AS played,
            SUM(CASE WHEN t.team = m.winner THEN 1 ELSE 0 END) AS won,
            COUNT(*) - SUM(CASE WHEN t.team = m.winner THEN 1 ELSE 0 END) AS lost_or_nr,
            ROUND(100.0 * SUM(CASE WHEN t.team = m.winner THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct,
            ROUND(100.0 * SUM(CASE WHEN t.team = m.toss_winner THEN 1 ELSE 0 END) / COUNT(*), 1) AS toss_win_pct
        FROM (
            SELECT matchId, team1 AS team FROM matches
            UNION ALL
            SELECT matchId, team2 AS team FROM matches
        ) AS t
        JOIN matches m ON t.matchId = m.matchId
        WHERE t.team IS NOT NULL
        GROUP BY t.team
        HAVING COUNT(*) >= ?
        ORDER BY win_pct DESC
    """
    team_df = run_query(team_win_sql, (min_played,))
    team_df["color"] = team_df["team"].map(lambda x: TEAM_COLORS.get(x, TURF_GREEN))

    tc1, tc2 = st.columns([1.15, 1.25])
    with tc1:
        t_bar = (
            alt.Chart(team_df)
            .mark_bar()
            .encode(
                x=alt.X("win_pct:Q", title="WIN PERCENTAGE (%)", scale=alt.Scale(domain=[0, 70])),
                y=alt.Y("team:N", sort="-x", title=None),
                color=alt.Color(
                    "team:N",
                    scale=alt.Scale(domain=team_df["team"].tolist(), range=team_df["color"].tolist()),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("team:N", title="Franchise"),
                    alt.Tooltip("played:Q", title="Matches Played"),
                    alt.Tooltip("won:Q", title="Matches Won"),
                    alt.Tooltip("win_pct:Q", title="Win %"),
                    alt.Tooltip("toss_win_pct:Q", title="Toss Win %"),
                ],
            )
        )
        t_lbl = t_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(
            text=alt.Text("win_pct:Q", format=".1f")
        )
        rule50 = alt.Chart(pd.DataFrame({"x": [50.0]})).mark_rule(strokeDash=[5, 4], color=SEAM_CRIMSON).encode(x="x:Q")
        st.altair_chart(style_altair(rule50 + t_bar + t_lbl, height=350), width="stretch")

    with tc2:
        st.dataframe(
            add_rank_col(team_df.drop(columns=["color"])),
            hide_index=True,
            width="stretch",
            height=350,
            column_config={
                "Rank": st.column_config.NumberColumn("#", width="small"),
                "team": st.column_config.TextColumn("Franchise"),
                "played": st.column_config.NumberColumn("Played", format="%d"),
                "won": st.column_config.NumberColumn("Won", format="%d"),
                "lost_or_nr": st.column_config.NumberColumn("Lost/NR", format="%d"),
                "win_pct": st.column_config.ProgressColumn("Win %", min_value=0, max_value=75, format="%.1f%%"),
                "toss_win_pct": st.column_config.NumberColumn("Toss Win %", format="%.1f%%"),
            },
        )
    show_sql_drawer(team_win_sql, "Franchise Win Percentage via UNION ALL", recruiter_sql_mode)

    # Head-to-Head Rivalry Ledger
    render_section_head("Head-to-Head Rivalry Comparison", "SELECT TWO FRANCHISES")
    default_a = teams.index("Mumbai Indians") if "Mumbai Indians" in teams else 0
    default_b = teams.index("Chennai Super Kings") if "Chennai Super Kings" in teams else min(1, len(teams) - 1)

    hc1, hc2 = st.columns(2)
    team_a = hc1.selectbox("Franchise A", teams, index=default_a)
    team_b = hc2.selectbox("Franchise B", teams, index=default_b)

    if team_a == team_b:
        st.warning("Select two different franchises to inspect their head-to-head record.")
    else:
        h2h_sql = """
            SELECT
                COUNT(*) AS played,
                SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS wins_a,
                SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS wins_b,
                SUM(CASE WHEN winner IS NULL OR winner = '' OR winner NOT IN (?, ?) THEN 1 ELSE 0 END) AS no_result
            FROM matches
            WHERE (team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?)
        """
        h2h_row = run_query(h2h_sql, (team_a, team_b, team_a, team_b, team_a, team_b, team_b, team_a)).iloc[0]
        played_h2h = int(h2h_row["played"])

        if played_h2h == 0:
            st.info(f"No matches recorded between **{team_a}** and **{team_b}**.")
        else:
            wins_a = int(h2h_row["wins_a"] or 0)
            wins_b = int(h2h_row["wins_b"] or 0)
            nr_cnt = int(h2h_row["no_result"] or 0)
            decided = max(wins_a + wins_b, 1)
            pct_a = round(100.0 * wins_a / decided, 1)
            pct_b = round(100.0 * wins_b / decided, 1)
            col_a = TEAM_COLORS.get(team_a, TURF_GREEN)
            col_b = TEAM_COLORS.get(team_b, SEAM_CRIMSON)

            st.markdown(
                f"""
                <div class="h2h-ledger">
                    <div class="h2h-grid">
                        <div>
                            <div class="h2h-side-name">{team_a}</div>
                            <div class="h2h-side-val" style="color:{col_a};">{wins_a} Wins ({pct_a}%)</div>
                        </div>
                        <div class="h2h-center-tag">{played_h2h} FIXTURES • {nr_cnt} NO RESULT</div>
                        <div style="text-align:right;">
                            <div class="h2h-side-name">{team_b}</div>
                            <div class="h2h-side-val" style="color:{col_b};">{wins_b} Wins ({pct_b}%)</div>
                        </div>
                    </div>
                    <div class="h2h-strip">
                        <div style="width:{pct_a}%; background:{col_a}; height:100%;"></div>
                        <div style="width:{pct_b}%; background:{col_b}; height:100%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            rc1, rc2 = st.columns(2)
            with rc1:
                h2h_bat_sql = """
                    SELECT d.batsman AS Batter, SUM(d.batsman_runs) AS Runs,
                           ROUND(100.0 * SUM(d.batsman_runs) /
                                 NULLIF(SUM(CASE WHEN (d.isWide IS NULL OR d.isWide = 0) THEN 1 ELSE 0 END), 0), 1) AS SR
                    FROM deliveries d JOIN matches m ON d.matchId = m.matchId
                    WHERE (m.team1 = ? AND m.team2 = ?) OR (m.team1 = ? AND m.team2 = ?)
                    GROUP BY d.batsman ORDER BY Runs DESC LIMIT 5
                """
                st.markdown(f"**Leading Run-Scorers in {TEAM_ABBR.get(team_a, team_a)} vs {TEAM_ABBR.get(team_b, team_b)} Fixtures**")
                st.dataframe(run_query(h2h_bat_sql, (team_a, team_b, team_b, team_a)), hide_index=True, width="stretch")
            with rc2:
                h2h_bowl_sql = f"""
                    SELECT d.bowler AS Bowler, COUNT(*) AS Wickets
                    FROM deliveries d JOIN matches m ON d.matchId = m.matchId
                    WHERE ((m.team1 = ? AND m.team2 = ?) OR (m.team1 = ? AND m.team2 = ?))
                      AND d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                      AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET}
                    GROUP BY d.bowler ORDER BY Wickets DESC LIMIT 5
                """
                st.markdown(f"**Leading Wicket-Takers in {TEAM_ABBR.get(team_a, team_a)} vs {TEAM_ABBR.get(team_b, team_b)} Fixtures**")
                st.dataframe(run_query(h2h_bowl_sql, (team_a, team_b, team_b, team_a)), hide_index=True, width="stretch")

            show_sql_drawer(h2h_sql, "Head-to-Head Series Summary", recruiter_sql_mode)

    # Toss & Innings Strategy Section
    render_section_head("Toss & Innings Strategy: Does Winning the Toss Help?", "DECIDED FIXTURES")
    toss_sql = """
        SELECT
            COUNT(*) AS total_decided,
            SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS toss_winner_won,
            SUM(CASE WHEN toss_decision = 'field' THEN 1 ELSE 0 END) AS chose_field,
            SUM(CASE WHEN winner = (
                CASE WHEN toss_decision = 'bat' THEN toss_winner
                     WHEN toss_winner = team1 THEN team2
                     ELSE team1 END
            ) THEN 1 ELSE 0 END) AS won_batting_first
        FROM matches
        WHERE winner IS NOT NULL AND winner <> ''
    """
    tr = run_query(toss_sql).iloc[0]
    total_dec = int(tr["total_decided"])
    toss_win_match_pct = 100.0 * tr["toss_winner_won"] / total_dec
    field_pref_pct = 100.0 * tr["chose_field"] / total_dec
    bat_first_win_pct = 100.0 * tr["won_batting_first"] / total_dec
    chase_win_pct = 100.0 - bat_first_win_pct

    tk1, tk2, tk3, tk4 = st.columns(4)
    with tk1:
        render_stat_card("Toss Winner Wins Match", f"{toss_win_match_pct:.1f}%", f"{int(tr['toss_winner_won'])} of {total_dec}", "decided matches", TURF_GREEN)
    with tk2:
        render_stat_card("Elect to Field First", f"{field_pref_pct:.1f}%", f"{int(tr['chose_field'])} times", "at the toss", WILLOW_OCHRE)
    with tk3:
        render_stat_card("Won Chasing (2nd Inn)", f"{chase_win_pct:.1f}%", f"{total_dec - int(tr['won_batting_first'])} wins", "chasing target", TURF_GREEN)
    with tk4:
        render_stat_card("Won Defending (1st Inn)", f"{bat_first_win_pct:.1f}%", f"{int(tr['won_batting_first'])} wins", "setting target", SEAM_CRIMSON)

    show_sql_drawer(toss_sql, "Toss & Chasing Win Split", recruiter_sql_mode)


# ==============================================================================
# PAGE 5: STADIUMS & PITCHES
# ==============================================================================
elif page == "05 / Stadiums & Pitches":
    render_masthead(
        "ISSUE 05 • VENUE & PITCH INTELLIGENCE",
        "First-Innings Par Scores & Chasing Bias by Ground",
        "Compare average first-innings totals, second-innings drop-off, and chasing win rates across major IPL stadiums.",
    )

    min_matches = st.slider("Minimum Matches Hosted at Venue", 5, 60, 15, step=5)

    venue_sql = """
        WITH match_scores AS (
            SELECT
                matchId,
                SUM(CASE WHEN inning = 1 THEN batsman_runs + extras ELSE 0 END) AS inn1_runs,
                SUM(CASE WHEN inning = 2 THEN batsman_runs + extras ELSE 0 END) AS inn2_runs,
                SUM(CASE WHEN dismissal_kind IS NOT NULL AND dismissal_kind <> '' THEN 1 ELSE 0 END) AS match_wickets
            FROM deliveries
            GROUP BY matchId
        ),
        venue_outcomes AS (
            SELECT
                m.venue,
                m.city,
                s.inn1_runs,
                s.inn2_runs,
                s.match_wickets,
                m.winner,
                CASE
                    WHEN m.toss_decision = 'bat' THEN m.toss_winner
                    WHEN m.toss_winner = m.team1 THEN m.team2
                    ELSE m.team1
                END AS bat_first_team
            FROM matches m
            JOIN match_scores s ON m.matchId = s.matchId
            WHERE m.venue IS NOT NULL AND m.venue <> ''
        )
        SELECT
            venue,
            COUNT(*) AS matches,
            ROUND(AVG(inn1_runs), 1) AS avg_first_innings,
            ROUND(AVG(inn2_runs), 1) AS avg_second_innings,
            MAX(inn1_runs) AS highest_1st_inn,
            ROUND(AVG(match_wickets), 1) AS avg_wickets,
            ROUND(100.0 * SUM(CASE WHEN winner IS NOT NULL AND winner <> '' AND winner <> bat_first_team THEN 1 ELSE 0 END) /
                  NULLIF(SUM(CASE WHEN winner IS NOT NULL AND winner <> '' THEN 1 ELSE 0 END), 0), 1) AS chase_win_pct
        FROM venue_outcomes
        GROUP BY venue
        HAVING COUNT(*) >= ?
        ORDER BY avg_first_innings DESC
        LIMIT 15
    """
    venue_df = run_query(venue_sql, (min_matches,))

    if not venue_df.empty:
        top_v = venue_df.iloc[0]
        most_m = venue_df.loc[venue_df["matches"].idxmax()]
        best_chase = venue_df.loc[venue_df["chase_win_pct"].idxmax()]
        vk1, vk2, vk3 = st.columns(3)
        with vk1:
            render_stat_card("Highest Scoring Venue", top_v["venue"].split(",")[0], f"{top_v['avg_first_innings']} avg 1st inn", f"(max: {int(top_v['highest_1st_inn'])})", SEAM_CRIMSON)
        with vk2:
            render_stat_card("Most Fixtures Hosted", most_m["venue"].split(",")[0], f"{int(most_m['matches'])} matches", f"(avg 1st inn: {most_m['avg_first_innings']})", TURF_GREEN)
        with vk3:
            render_stat_card("Highest Chasing Win Rate", best_chase["venue"].split(",")[0], f"{best_chase['chase_win_pct']}% chase wins", f"across {int(best_chase['matches'])} fixtures", WILLOW_OCHRE)

    vc1, vc2 = st.columns(2)
    with vc1:
        render_section_head("Highest Average 1st-Innings Score", f"MIN {min_matches} MATCHES")
        v_bar = (
            alt.Chart(venue_df)
            .mark_bar(color=TURF_GREEN)
            .encode(
                x=alt.X("avg_first_innings:Q", title="AVG 1ST INNINGS SCORE", scale=alt.Scale(zero=False, padding=15)),
                y=alt.Y("venue:N", sort="-x", title=None, axis=alt.Axis(labelLimit=230)),
                tooltip=[
                    alt.Tooltip("venue:N", title="Venue"),
                    alt.Tooltip("matches:Q", title="Matches Hosted"),
                    alt.Tooltip("avg_first_innings:Q", title="Avg 1st Innings"),
                    alt.Tooltip("avg_second_innings:Q", title="Avg 2nd Innings"),
                    alt.Tooltip("highest_1st_inn:Q", title="Highest 1st Inn Total"),
                    alt.Tooltip("chase_win_pct:Q", title="Chase Win %"),
                ],
            )
        )
        v_lbl = v_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(
            text=alt.Text("avg_first_innings:Q", format=".1f")
        )
        st.altair_chart(style_altair(v_bar + v_lbl, height=410), width="stretch")

    with vc2:
        render_section_head("Chasing Win Percentage by Venue", "50% RULE = NEUTRAL PITCH")
        c_bar = (
            alt.Chart(venue_df)
            .mark_bar(color=WILLOW_OCHRE)
            .encode(
                x=alt.X("chase_win_pct:Q", title="CHASING WIN % (2ND INNINGS)", scale=alt.Scale(domain=[0, 80])),
                y=alt.Y("venue:N", sort="-x", title=None, axis=alt.Axis(labelLimit=230)),
                tooltip=[
                    alt.Tooltip("venue:N", title="Venue"),
                    alt.Tooltip("chase_win_pct:Q", title="Chasing Win %"),
                    alt.Tooltip("matches:Q", title="Matches"),
                ],
            )
        )
        rule50 = alt.Chart(pd.DataFrame({"x": [50.0]})).mark_rule(strokeDash=[5, 4], color=SEAM_CRIMSON).encode(x="x:Q")
        c_lbl = c_bar.mark_text(align="left", dx=6, color=INK_DARK, fontWeight=600).encode(
            text=alt.Text("chase_win_pct:Q", format=".1f")
        )
        st.altair_chart(style_altair(rule50 + c_bar + c_lbl, height=410), width="stretch")

    render_section_head("Complete Venue Register", "SORTABLE TABLE")
    st.dataframe(
        add_rank_col(venue_df),
        hide_index=True,
        width="stretch",
        column_config={
            "Rank": st.column_config.NumberColumn("#", width="small"),
            "venue": st.column_config.TextColumn("Stadium / Venue"),
            "matches": st.column_config.NumberColumn("Matches", format="%d"),
            "avg_first_innings": st.column_config.ProgressColumn("Avg 1st Inn", min_value=120, max_value=210, format="%.1f"),
            "avg_second_innings": st.column_config.NumberColumn("Avg 2nd Inn", format="%.1f"),
            "highest_1st_inn": st.column_config.NumberColumn("Max 1st Inn", format="%d"),
            "avg_wickets": st.column_config.NumberColumn("Wkts / Match", format="%.1f"),
            "chase_win_pct": st.column_config.ProgressColumn("Chase Win %", min_value=0, max_value=100, format="%.1f%%"),
        },
    )
    show_sql_drawer(venue_sql, "CTE-Powered Venue Scoring & Pitch Bias", recruiter_sql_mode)


# ==============================================================================
# PAGE 6: PLAYER MATCHUPS & CAREER PROFILES
# ==============================================================================
elif page == "06 / Player Matchups":
    render_masthead(
        "ISSUE 06 • PLAYER SCOUTING & HEAD-TO-HEAD ARCHIVE",
        "Batter vs Bowler Matchups & Career Trajectories",
        "Examine ball-by-ball matchups between any IPL batter and bowler, or trace a player's season-by-season output.",
    )

    top_batters = (
        run_query("SELECT batsman FROM deliveries GROUP BY batsman ORDER BY SUM(batsman_runs) DESC LIMIT 250")["batsman"]
        .dropna()
        .tolist()
    )
    top_bowlers = (
        run_query("SELECT bowler FROM deliveries GROUP BY bowler ORDER BY COUNT(*) DESC LIMIT 250")["bowler"]
        .dropna()
        .tolist()
    )

    mode_tab1, mode_tab2 = st.tabs(["Batter vs Bowler Head-to-Head", "Player Season-by-Season Career Log"])

    with mode_tab1:
        mc1, mc2 = st.columns(2)
        default_bat = top_batters.index("V Kohli") if "V Kohli" in top_batters else 0
        default_bwl = top_bowlers.index("JJ Bumrah") if "JJ Bumrah" in top_bowlers else 0

        sel_batter = mc1.selectbox("Select Batter", top_batters, index=default_bat)
        sel_bowler = mc2.selectbox("Select Bowler", top_bowlers, index=default_bwl)

        matchup_sql = f"""
            SELECT
                COUNT(DISTINCT d.matchId) AS innings_faced,
                SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) AS balls_faced,
                SUM(d.batsman_runs) AS runs_scored,
                SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                          AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET} THEN 1 ELSE 0 END) AS dismissals,
                SUM(CASE WHEN d.batsman_runs = 0 AND d.extras = 0 THEN 1 ELSE 0 END) AS dots,
                SUM(CASE WHEN d.batsman_runs = 4 THEN 1 ELSE 0 END) AS fours,
                SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes,
                ROUND(100.0 * SUM(d.batsman_runs) /
                      NULLIF(SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END), 0), 1) AS strike_rate
            FROM deliveries d
            WHERE d.batsman = ? AND d.bowler = ?
        """
        m_row = run_query(matchup_sql, (sel_batter, sel_bowler)).iloc[0]
        balls_f = int(m_row["balls_faced"] or 0)

        if balls_f == 0:
            st.info(f"**{sel_batter}** and **{sel_bowler}** have not faced each other in the IPL dataset.")
        else:
            runs_s = int(m_row["runs_scored"] or 0)
            outs = int(m_row["dismissals"] or 0)
            sr_val = float(m_row["strike_rate"] or 0.0)
            dots_v = int(m_row["dots"] or 0)
            fours_v = int(m_row["fours"] or 0)
            sixes_v = int(m_row["sixes"] or 0)

            mk1, mk2, mk3, mk4, mk5 = st.columns(5)
            with mk1:
                render_stat_card("Runs Scored", f"{runs_s}", f"{balls_f} balls", f"({int(m_row['innings_faced'])} matches)", TURF_GREEN)
            with mk2:
                render_stat_card("Strike Rate", f"{sr_val}", f"{fours_v}x4, {sixes_v}x6", "scoring rate", WILLOW_OCHRE)
            with mk3:
                render_stat_card("Dismissals", f"{outs}", f"Avg {runs_s/outs:.1f}" if outs > 0 else "Not Out", f"vs {sel_bowler}", SEAM_CRIMSON)
            with mk4:
                render_stat_card("Dot Balls", f"{dots_v}", f"{100.0*dots_v/balls_f:.1f}%", "dot ball share", TURF_GREEN)
            with mk5:
                render_stat_card("Boundary Runs", f"{fours_v*4 + sixes_v*6}", f"{fours_v + sixes_v} boundaries", "in 4s & 6s", SEAM_CRIMSON)

            season_m_sql = f"""
                SELECT
                    m.season AS Season,
                    SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) AS Balls,
                    SUM(d.batsman_runs) AS Runs,
                    SUM(CASE WHEN d.dismissal_kind IS NOT NULL AND d.dismissal_kind <> ''
                              AND d.dismissal_kind NOT IN {NOT_BOWLER_WICKET} THEN 1 ELSE 0 END) AS Dismissals,
                    SUM(CASE WHEN d.batsman_runs = 4 THEN 1 ELSE 0 END) AS Fours,
                    SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) AS Sixes,
                    ROUND(100.0 * SUM(d.batsman_runs) /
                          NULLIF(SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END), 0), 1) AS SR
                FROM deliveries d
                JOIN matches m ON d.matchId = m.matchId
                WHERE d.batsman = ? AND d.bowler = ?
                GROUP BY m.season
                ORDER BY m.season
            """
            sm_df = run_query(season_m_sql, (sel_batter, sel_bowler))
            render_section_head(f"Season-by-Season Log: {sel_batter} vs {sel_bowler}", "CHRONOLOGICAL RECORD")
            st.dataframe(sm_df, hide_index=True, width="stretch")
            show_sql_drawer(matchup_sql, "Batter vs Bowler Head-to-Head Telemetry", recruiter_sql_mode)

    with mode_tab2:
        profile_batter = st.selectbox("Select Batter for Career Progression", top_batters, index=0)
        career_sql = f"""
            SELECT
                m.season,
                COUNT(DISTINCT d.matchId) AS innings,
                SUM(d.batsman_runs) AS runs,
                SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END) AS balls,
                ROUND(100.0 * SUM(d.batsman_runs) /
                      NULLIF(SUM(CASE WHEN {LEGAL_BALL} THEN 1 ELSE 0 END), 0), 1) AS strike_rate,
                SUM(CASE WHEN d.batsman_runs = 4 THEN 1 ELSE 0 END) AS fours,
                SUM(CASE WHEN d.batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes
            FROM deliveries d
            JOIN matches m ON d.matchId = m.matchId
            WHERE d.batsman = ?
            GROUP BY m.season
            ORDER BY m.season
        """
        c_df = run_query(career_sql, (profile_batter,))

        render_section_head(f"{profile_batter} — Season-by-Season Runs", "CAREER TRAJECTORY")
        c_bars = (
            alt.Chart(c_df)
            .mark_bar(color=TURF_GREEN)
            .encode(
                x=alt.X("season:N", title="SEASON", sort=None, axis=alt.Axis(labelAngle=-40)),
                y=alt.Y("runs:Q", title="SEASON RUNS"),
                tooltip=[
                    alt.Tooltip("season:N", title="Season"),
                    alt.Tooltip("innings:Q", title="Innings"),
                    alt.Tooltip("runs:Q", title="Runs", format=","),
                    alt.Tooltip("strike_rate:Q", title="Strike Rate"),
                    alt.Tooltip("fours:Q", title="Fours"),
                    alt.Tooltip("sixes:Q", title="Sixes"),
                ],
            )
        )
        c_lbl = c_bars.mark_text(dy=-7, color=INK_DARK, fontSize=10, fontWeight=600).encode(text="runs:Q")
        st.altair_chart(style_altair(c_bars + c_lbl, height=330), width="stretch")
        st.dataframe(c_df, hide_index=True, width="stretch")
        show_sql_drawer(career_sql, "Player Career Trajectory by Season", recruiter_sql_mode)