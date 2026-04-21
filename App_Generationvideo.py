"""
Creative Video Ads Operating System
A manual creative intelligence & prompt engineering system.
Runs on Streamlit Community Cloud with Cloudflare R2 storage.
"""

import streamlit as st
import pandas as pd
import boto3
import io
import uuid
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AdOS · Creative Video Ads OS",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg:        #0d0f14;
    --surface:   #13161e;
    --surface2:  #1a1e28;
    --border:    #252a36;
    --border2:   #2e3445;
    --text:      #e8eaf0;
    --text-muted:#6b7280;
    --text-dim:  #9ca3af;
    --accent:    #6366f1;
    --accent2:   #818cf8;
    --accent-glow: rgba(99,102,241,0.15);
    --green:     #22c55e;
    --amber:     #f59e0b;
    --red:       #ef4444;
    --radius:    10px;
    --radius-lg: 16px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1100px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }
[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar logo ── */
.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    padding: 1rem 0 0.5rem 0;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-tagline {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0.5rem 0 0.3rem 0;
    border-top: 1px solid var(--border);
    margin-top: 0.5rem;
}

/* ── Project Header ── */
.project-header {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    position: relative;
    overflow: hidden;
}
.project-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #a78bfa, #6366f1);
}
.project-header-icon {
    font-size: 2rem;
    line-height: 1;
    opacity: 0.9;
}
.project-header-body {}
.project-header-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 0.25rem 0;
    letter-spacing: -0.02em;
}
.project-header-meta {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    padding: 0.2rem 0.6rem;
    border-radius: 99px;
    background: var(--accent-glow);
    border: 1px solid rgba(99,102,241,0.3);
    color: var(--accent2);
    text-transform: uppercase;
}
.badge-green {
    background: rgba(34,197,94,0.1);
    border-color: rgba(34,197,94,0.3);
    color: #4ade80;
}
.badge-amber {
    background: rgba(245,158,11,0.1);
    border-color: rgba(245,158,11,0.3);
    color: #fbbf24;
}

/* ── Step Cards ── */
.step-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    margin-bottom: 1rem;
    overflow: hidden;
    transition: border-color 0.2s;
}
.step-card:hover { border-color: var(--border2); }
.step-card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
}
.step-number {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--accent2);
    background: var(--accent-glow);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 6px;
    padding: 0.15rem 0.5rem;
    letter-spacing: 0.05em;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    flex: 1;
}
.step-status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--border2);
}
.step-status-dot.done { background: var(--green); box-shadow: 0 0 6px var(--green); }
.step-status-dot.partial { background: var(--amber); }

/* ── Section Labels ── */
.section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
}
.empty-state-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
}
.empty-state-desc { font-size: 0.85rem; color: var(--text-muted); }

/* ── Pipeline overview ── */
.pipeline-track {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 1rem 0 1.5rem 0;
    overflow-x: auto;
    padding: 0.25rem 0;
}
.pipeline-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
    flex-shrink: 0;
}
.pipeline-circle {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: var(--surface2);
    border: 2px solid var(--border2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: 500;
}
.pipeline-circle.done {
    background: rgba(34,197,94,0.15);
    border-color: var(--green);
    color: var(--green);
}
.pipeline-circle.active {
    background: var(--accent-glow);
    border-color: var(--accent);
    color: var(--accent2);
}
.pipeline-label {
    font-size: 0.6rem;
    color: var(--text-muted);
    white-space: nowrap;
    max-width: 60px;
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
}
.pipeline-connector {
    height: 2px;
    width: 24px;
    background: var(--border2);
    flex-shrink: 0;
    margin-bottom: 1.3rem;
}
.pipeline-connector.done { background: var(--green); opacity: 0.5; }

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}
.stTextInput input {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}
.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}
.stButton button {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}
.stButton button:hover {
    border-color: var(--accent) !important;
    color: var(--accent2) !important;
    background: var(--accent-glow) !important;
}
/* Primary button */
[data-testid="baseButton-primary"] button,
.stButton [kind="primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}
[data-testid="baseButton-primary"]:hover button {
    background: var(--accent2) !important;
}
div[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
div[data-testid="stExpander"] summary {
    background: var(--surface2) !important;
    border-radius: var(--radius) !important;
    font-size: 0.85rem !important;
    color: var(--text-dim) !important;
}
.stNumberInput input {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
}
.stSlider { padding: 0.5rem 0 !important; }
div[data-testid="stMarkdownContainer"] p { color: var(--text-dim); font-size: 0.875rem; }
.stSuccess { background: rgba(34,197,94,0.1) !important; border: 1px solid rgba(34,197,94,0.3) !important; border-radius: var(--radius) !important; }
.stInfo { background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: var(--radius) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.25) !important; border-radius: var(--radius) !important; }
hr { border-color: var(--border) !important; margin: 0.75rem 0 !important; }

/* ── Settings ── */
.settings-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.settings-card h4 {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 0.25rem 0;
}
.settings-card p {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin: 0 0 1rem 0;
}

/* ── Divider ── */
.vdivider {
    height: 1px;
    background: var(--border);
    margin: 1rem 0;
}

/* ── Prompt copy box ── */
.prompt-copy-box {
    background: #0a0c10;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #a5b4fc;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 180px;
    overflow-y: auto;
    margin-bottom: 0.5rem;
}

/* ── Nav items in sidebar ── */
.nav-item {
    padding: 0.45rem 0.75rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85rem;
    color: var(--text-dim);
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.nav-item:hover { background: var(--surface2); color: var(--text); }
.nav-item.active {
    background: var(--accent-glow);
    color: var(--accent2);
    border: 1px solid rgba(99,102,241,0.2);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# R2 STORAGE LAYER
# ─────────────────────────────────────────────

@st.cache_resource
def get_r2():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{st.secrets['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=st.secrets["R2_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["R2_SECRET_KEY"],
        region_name="auto",
    )


def load_parquet(key: str, cols: list) -> pd.DataFrame:
    try:
        obj = get_r2().get_object(Bucket=st.secrets["R2_BUCKET"], Key=key)
        return pd.read_parquet(io.BytesIO(obj["Body"].read()))
    except Exception:
        return pd.DataFrame(columns=cols)


def save_parquet(df: pd.DataFrame, key: str):
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    get_r2().put_object(
        Bucket=st.secrets["R2_BUCKET"], Key=key, Body=buf.getvalue()
    )


# ─────────────────────────────────────────────
# DATA KEYS & SCHEMAS
# ─────────────────────────────────────────────

PROJECTS_KEY  = "ados/projects.parquet"
SETTINGS_KEY  = "ados/settings.parquet"

PROJECT_COLS = [
    "id", "name", "type", "num_steps", "context",
    "created_at", "updated_at",
]
STEP_COLS = [
    "project_id", "step_num", "label",
    "prompt", "output", "updated_at",
]
SETTINGS_COLS = ["key", "value"]


def steps_key(project_id: str) -> str:
    return f"ados/steps/{project_id}.parquet"


# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────

def load_projects() -> pd.DataFrame:
    return load_parquet(PROJECTS_KEY, PROJECT_COLS)


def save_projects(df: pd.DataFrame):
    save_parquet(df, PROJECTS_KEY)


def load_steps(project_id: str) -> pd.DataFrame:
    return load_parquet(steps_key(project_id), STEP_COLS)


def save_steps(df: pd.DataFrame, project_id: str):
    save_parquet(df, steps_key(project_id))


def load_settings() -> dict:
    df = load_parquet(SETTINGS_KEY, SETTINGS_COLS)
    defaults = {
        "inspiration_steps": "3",
        "script_steps": "4",
        "inspiration_labels": "Raw Analysis,Inspiration Cards,Creative Amplification",
        "script_labels": "Script Generation,Conversion Optimization,Creative Enhancement,Remotion Formatting",
    }
    if df.empty:
        return defaults
    result = defaults.copy()
    for _, row in df.iterrows():
        result[str(row["key"])] = str(row["value"])
    return result


def save_settings(settings: dict):
    rows = [{"key": k, "value": v} for k, v in settings.items()]
    df = pd.DataFrame(rows, columns=SETTINGS_COLS)
    save_parquet(df, SETTINGS_KEY)


def create_project(name: str, proj_type: str, num_steps: int, context: str, labels: list) -> str:
    pid = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    projects = load_projects()
    new_row = pd.DataFrame([{
        "id": pid, "name": name, "type": proj_type,
        "num_steps": num_steps, "context": context,
        "created_at": now, "updated_at": now,
    }])
    projects = pd.concat([projects, new_row], ignore_index=True)
    save_projects(projects)

    # Initialize empty steps
    steps_rows = []
    for i in range(1, num_steps + 1):
        label = labels[i - 1] if i - 1 < len(labels) else f"Step {i}"
        steps_rows.append({
            "project_id": pid, "step_num": i, "label": label,
            "prompt": "", "output": "", "updated_at": now,
        })
    save_steps(pd.DataFrame(steps_rows, columns=STEP_COLS), pid)
    return pid


def delete_project(pid: str):
    projects = load_projects()
    projects = projects[projects["id"] != pid]
    save_projects(projects)


def get_step_completion(steps_df: pd.DataFrame) -> tuple:
    """Returns (done_count, total)."""
    total = len(steps_df)
    done = int((steps_df["output"].fillna("").str.strip() != "").sum())
    return done, total


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────

def init_state():
    defaults = {
        "page": "home",
        "selected_project": None,
        "show_new_project_form": False,
        "project_type_filter": "all",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">AdOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">Creative Video Ads OS</div>', unsafe_allow_html=True)

        # ── Navigation ──
        st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)

        pages = [
            ("🎬", "Video Inspiration", "inspiration"),
            ("📝", "Script Projects", "script"),
            ("⚙️", "Settings", "settings"),
        ]
        for icon, label, pg in pages:
            active_cls = "active" if st.session_state.page == pg else ""
            if st.button(f"{icon}  {label}", key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg
                st.session_state.selected_project = None
                st.rerun()

        # ── Project list shortcut ──
        projects = load_projects()
        current_type = st.session_state.page  # "inspiration" or "script"
        if current_type in ("inspiration", "script"):
            filtered = projects[projects["type"] == current_type]
            if not filtered.empty:
                st.markdown('<div class="sidebar-section">Recent Projects</div>', unsafe_allow_html=True)
                for _, proj in filtered.sort_values("updated_at", ascending=False).head(8).iterrows():
                    label = proj["name"][:22] + "…" if len(proj["name"]) > 22 else proj["name"]
                    is_selected = st.session_state.selected_project == proj["id"]
                    btn_label = f"{'▶ ' if is_selected else '  '}{label}"
                    if st.button(btn_label, key=f"proj_{proj['id']}", use_container_width=True):
                        st.session_state.selected_project = proj["id"]
                        st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.68rem;color:#4b5563;text-align:center;">'
            'Manual AI workflow · No APIs sent<br>All data stored in Cloudflare R2'
            '</div>',
            unsafe_allow_html=True
        )


render_sidebar()


# ─────────────────────────────────────────────
# HELPERS: UI COMPONENTS
# ─────────────────────────────────────────────

def project_header(name: str, proj_type: str, num_steps: int, done: int, context: str):
    icon = "🎬" if proj_type == "inspiration" else "📝"
    type_label = "Video Inspiration" if proj_type == "inspiration" else "Script Project"
    pct = int(done / num_steps * 100) if num_steps else 0
    status_badge = (
        f'<span class="badge badge-green">✓ Complete</span>' if done == num_steps
        else f'<span class="badge badge-amber">{pct}% Done</span>'
        if done > 0 else '<span class="badge">Not Started</span>'
    )
    ctx_html = (
        f'<span style="font-size:0.78rem;color:#6b7280;margin-left:0.5rem;">· {context[:60]}{"…" if len(context)>60 else ""}</span>'
        if context else ""
    )
    st.markdown(f"""
    <div class="project-header">
        <div class="project-header-icon">{icon}</div>
        <div class="project-header-body">
            <div class="project-header-name">{name}</div>
            <div class="project-header-meta">
                <span class="badge">{type_label}</span>
                <span class="badge">{done}/{num_steps} Steps</span>
                {status_badge}
                {ctx_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def pipeline_track(steps_df: pd.DataFrame, num_steps: int):
    """Render the horizontal pipeline progress bar."""
    nodes_html = ""
    for i in range(1, num_steps + 1):
        row = steps_df[steps_df["step_num"] == i]
        if not row.empty:
            has_output = str(row.iloc[0]["output"]).strip() != ""
            label = str(row.iloc[0]["label"])[:10]
            cls = "done" if has_output else ""
        else:
            cls = ""
            label = f"Step {i}"
        circle_cls = cls
        nodes_html += f"""
        <div class="pipeline-node">
            <div class="pipeline-circle {circle_cls}">{i}</div>
            <div class="pipeline-label">{label}</div>
        </div>
        """
        if i < num_steps:
            conn_cls = "done" if cls == "done" else ""
            nodes_html += f'<div class="pipeline-connector {conn_cls}"></div>'

    st.markdown(f'<div class="pipeline-track">{nodes_html}</div>', unsafe_allow_html=True)


def step_card(step_row: pd.Series, project_id: str, step_num: int, num_steps: int):
    """Render one step card with editable prompt and output."""
    label    = str(step_row.get("label", f"Step {step_num}"))
    prompt   = str(step_row.get("prompt", ""))
    output   = str(step_row.get("output", ""))
    has_out  = output.strip() != ""
    has_pr   = prompt.strip() != ""

    dot_cls = "done" if has_out else ("partial" if has_pr else "")
    status_icon = "✓" if has_out else ("✎" if has_pr else "·")

    st.markdown(f"""
    <div class="step-card">
        <div class="step-card-header">
            <span class="step-number">STEP {step_num}</span>
            <span class="step-title">{label}</span>
            <span class="step-status-dot {dot_cls}" title="{'Done' if has_out else 'In progress' if has_pr else 'Empty'}"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_p, col_o = st.columns([1, 1], gap="medium")

    # ── Left: Prompt ──
    with col_p:
        with st.expander("✏️  Prompt", expanded=not has_out):
            st.markdown('<div class="section-label">🔧 Edit prompt for this step</div>', unsafe_allow_html=True)
            new_prompt = st.text_area(
                "Prompt",
                value=prompt,
                height=180,
                key=f"prompt_{project_id}_{step_num}",
                label_visibility="collapsed",
                placeholder="Write your ChatGPT prompt here…\n\nTip: Be specific. Include context, tone, format requirements.",
            )
            save_col, copy_col = st.columns([1, 1])
            with save_col:
                if st.button("💾 Save Prompt", key=f"save_prompt_{project_id}_{step_num}"):
                    _upsert_step_field(project_id, step_num, "prompt", new_prompt)
                    st.success("Prompt saved.")
                    st.rerun()
            with copy_col:
                if st.button("📋 Copy Prompt", key=f"copy_{project_id}_{step_num}"):
                    st.session_state[f"show_copy_{project_id}_{step_num}"] = True

            if st.session_state.get(f"show_copy_{project_id}_{step_num}"):
                st.markdown(
                    f'<div class="prompt-copy-box">{new_prompt or "(no prompt yet)"}</div>',
                    unsafe_allow_html=True
                )
                st.caption("☝️ Select all text above and copy to clipboard, then paste into ChatGPT.")
                if st.button("✕ Dismiss", key=f"dismiss_copy_{project_id}_{step_num}"):
                    st.session_state[f"show_copy_{project_id}_{step_num}"] = False

    # ── Right: Output ──
    with col_o:
        with st.expander("💬  ChatGPT Output", expanded=True):
            st.markdown('<div class="section-label">📥 Paste ChatGPT response here</div>', unsafe_allow_html=True)
            new_output = st.text_area(
                "Output",
                value=output,
                height=200,
                key=f"output_{project_id}_{step_num}",
                label_visibility="collapsed",
                placeholder="Paste the ChatGPT response here after running your prompt…",
            )
            save_out_col, clear_col = st.columns([1, 1])
            with save_out_col:
                if st.button("💾 Save Output", key=f"save_output_{project_id}_{step_num}", type="primary"):
                    _upsert_step_field(project_id, step_num, "output", new_output)
                    st.success("Output saved!")
                    st.rerun()
            with clear_col:
                if has_out:
                    if st.button("🗑 Clear", key=f"clear_{project_id}_{step_num}"):
                        _upsert_step_field(project_id, step_num, "output", "")
                        st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


def _upsert_step_field(project_id: str, step_num: int, field: str, value: str):
    """Update a single field in a step row."""
    steps = load_steps(project_id)
    now = datetime.utcnow().isoformat()
    mask = steps["step_num"] == step_num
    if mask.any():
        steps.loc[mask, field] = value
        steps.loc[mask, "updated_at"] = now
    else:
        new_row = pd.DataFrame([{
            "project_id": project_id, "step_num": step_num,
            "label": f"Step {step_num}", "prompt": "",
            "output": "", "updated_at": now, field: value,
        }])
        steps = pd.concat([steps, new_row], ignore_index=True)
    save_steps(steps, project_id)

    # Update project updated_at
    projects = load_projects()
    projects.loc[projects["id"] == project_id, "updated_at"] = now
    save_projects(projects)


# ─────────────────────────────────────────────
# PAGE: PROJECT WORKSPACE (shared for both types)
# ─────────────────────────────────────────────

def render_project_workspace(proj_type: str):
    settings   = load_settings()
    projects   = load_projects()
    filtered   = projects[projects["type"] == proj_type].copy()

    default_steps = int(settings.get(
        "inspiration_steps" if proj_type == "inspiration" else "script_steps", 3
    ))
    raw_labels = settings.get(
        "inspiration_labels" if proj_type == "inspiration" else "script_labels", ""
    )
    default_labels = [l.strip() for l in raw_labels.split(",") if l.strip()]

    icon      = "🎬" if proj_type == "inspiration" else "📝"
    type_name = "Video Inspiration" if proj_type == "inspiration" else "Script"

    # ── Top bar ──
    h_col, btn_col = st.columns([3, 1])
    with h_col:
        st.markdown(
            f'<div style="font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;'
            f'letter-spacing:-0.03em;color:#e8eaf0;padding-bottom:0.15rem;">'
            f'{icon} {type_name} Projects</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="font-size:0.8rem;color:#6b7280;">'
            f'{len(filtered)} project{"s" if len(filtered)!=1 else ""} · '
            f'Manual AI workflow — write prompt → copy to ChatGPT → paste output</div>',
            unsafe_allow_html=True
        )
    with btn_col:
        if st.button("＋  New Project", use_container_width=True, type="primary"):
            st.session_state.show_new_project_form = not st.session_state.get("show_new_project_form", False)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── New project form ──
    if st.session_state.get("show_new_project_form", False):
        with st.container():
            st.markdown(
                '<div class="settings-card" style="border-color:rgba(99,102,241,0.35);">',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<h4 style="margin-bottom:0.75rem">Create {type_name} Project</h4>',
                unsafe_allow_html=True
            )
            fc1, fc2 = st.columns([2, 1])
            with fc1:
                proj_name = st.text_input(
                    "Project Name", placeholder="e.g. Nike Air Max Analysis",
                    key="new_proj_name"
                )
                context = st.text_input(
                    "Context / Notes (optional)",
                    placeholder="e.g. Target audience, product, angle…",
                    key="new_proj_context"
                )
            with fc2:
                num_steps = st.number_input(
                    "Number of Steps",
                    min_value=1, max_value=12,
                    value=default_steps,
                    key="new_proj_steps"
                )
            # Dynamic label editors
            st.markdown(
                '<div class="section-label" style="margin-top:0.5rem">Step Labels</div>',
                unsafe_allow_html=True
            )
            label_cols = st.columns(min(int(num_steps), 4))
            step_labels = []
            for i in range(int(num_steps)):
                col_idx = i % 4
                with label_cols[col_idx]:
                    default_label = default_labels[i] if i < len(default_labels) else f"Step {i+1}"
                    lbl = st.text_input(
                        f"Step {i+1}",
                        value=default_label,
                        key=f"new_label_{i}"
                    )
                    step_labels.append(lbl)

            cr_col, cancel_col = st.columns([1, 1])
            with cr_col:
                if st.button("✓  Create Project", type="primary", use_container_width=True, key="create_proj_btn"):
                    if proj_name.strip():
                        pid = create_project(
                            proj_name.strip(), proj_type,
                            int(num_steps), context.strip(), step_labels
                        )
                        st.session_state.selected_project = pid
                        st.session_state.show_new_project_form = False
                        st.success(f"Project '{proj_name}' created!")
                        st.rerun()
                    else:
                        st.warning("Please enter a project name.")
            with cancel_col:
                if st.button("✕  Cancel", use_container_width=True, key="cancel_new_proj"):
                    st.session_state.show_new_project_form = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── No project selected → show list ──
    selected_id = st.session_state.get("selected_project")
    if not selected_id or (not filtered.empty and selected_id not in filtered["id"].values):
        if filtered.empty:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">✦</div>
                <div class="empty-state-title">No projects yet</div>
                <div class="empty-state-desc">Click "＋ New Project" to create your first workflow.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            _render_project_list(filtered)
        return

    # ── Project selected → show workspace ──
    proj_row = filtered[filtered["id"] == selected_id]
    if proj_row.empty:
        st.session_state.selected_project = None
        st.rerun()
        return

    proj = proj_row.iloc[0]
    steps_df = load_steps(selected_id)
    done, total = get_step_completion(steps_df)

    # Header
    project_header(proj["name"], proj_type, total, done, str(proj.get("context", "")))

    # Actions bar
    act1, act2, act3, act_sp = st.columns([1, 1, 1, 3])
    with act1:
        if st.button("← All Projects", use_container_width=True):
            st.session_state.selected_project = None
            st.rerun()
    with act2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with act3:
        if st.button("🗑 Delete", use_container_width=True):
            st.session_state[f"confirm_delete_{selected_id}"] = True

    if st.session_state.get(f"confirm_delete_{selected_id}"):
        st.warning(f"⚠️ Delete project '{proj['name']}'? This cannot be undone.")
        cd1, cd2 = st.columns([1, 1])
        with cd1:
            if st.button("Yes, Delete", key="confirm_del_yes", type="primary"):
                delete_project(selected_id)
                st.session_state.selected_project = None
                st.session_state.pop(f"confirm_delete_{selected_id}", None)
                st.rerun()
        with cd2:
            if st.button("Cancel", key="confirm_del_no"):
                st.session_state.pop(f"confirm_delete_{selected_id}", None)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # Pipeline track
    pipeline_track(steps_df, total)

    # Steps
    for i in range(1, total + 1):
        rows = steps_df[steps_df["step_num"] == i]
        if not rows.empty:
            step_card(rows.iloc[0], selected_id, i, total)
        else:
            step_card(pd.Series({
                "label": f"Step {i}", "prompt": "", "output": ""
            }), selected_id, i, total)


def _render_project_list(filtered: pd.DataFrame):
    """Show grid of project cards."""
    sorted_df = filtered.sort_values("updated_at", ascending=False)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # 2-column grid
    cols = st.columns(2, gap="medium")
    for idx, (_, proj) in enumerate(sorted_df.iterrows()):
        with cols[idx % 2]:
            steps_df  = load_steps(proj["id"])
            done, tot = get_step_completion(steps_df)
            pct       = int(done / tot * 100) if tot else 0
            updated   = str(proj.get("updated_at", ""))[:10]
            ctx_txt   = str(proj.get("context", ""))
            ctx_short = ctx_txt[:55] + "…" if len(ctx_txt) > 55 else ctx_txt

            status_color = "#22c55e" if done == tot else ("#f59e0b" if done > 0 else "#374151")
            bar_width    = pct

            st.markdown(f"""
            <div class="step-card" style="cursor:pointer;padding:0;">
                <div style="padding:1.1rem 1.25rem;">
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
                        <span style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e8eaf0;">{proj['name']}</span>
                    </div>
                    <div style="font-size:0.75rem;color:#6b7280;margin-bottom:0.75rem;">{ctx_short or "No context added"}</div>
                    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                        <span class="badge">{tot} steps</span>
                        <span class="badge {'badge-green' if done==tot else 'badge-amber' if done>0 else ''}">{done}/{tot} done</span>
                        <span style="font-size:0.7rem;color:#4b5563;margin-left:auto;">{updated}</span>
                    </div>
                    <div style="height:4px;background:#1f2937;border-radius:99px;overflow:hidden;">
                        <div style="height:100%;width:{bar_width}%;background:{status_color};border-radius:99px;transition:width 0.4s;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open Project →", key=f"open_{proj['id']}", use_container_width=True):
                st.session_state.selected_project = proj["id"]
                st.rerun()

        if idx % 2 == 1:
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────

def render_settings():
    st.markdown(
        '<div style="font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;'
        'letter-spacing:-0.03em;color:#e8eaf0;padding-bottom:0.15rem;">'
        '⚙️ Settings</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-size:0.8rem;color:#6b7280;margin-bottom:1.5rem;">'
        'Global defaults · Stored in Cloudflare R2</div>',
        unsafe_allow_html=True
    )

    settings = load_settings()

    # ── Inspiration defaults ──
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown('<h4>🎬 Video Inspiration Pipeline</h4>', unsafe_allow_html=True)
    st.markdown('<p>Default number of steps and step labels for new inspiration projects.</p>', unsafe_allow_html=True)

    insp_steps = st.number_input(
        "Default Steps", min_value=1, max_value=12,
        value=int(settings.get("inspiration_steps", 3)),
        key="s_insp_steps"
    )
    insp_labels_raw = settings.get("inspiration_labels", "Raw Analysis,Inspiration Cards,Creative Amplification")
    insp_labels = st.text_input(
        "Step Labels (comma-separated)",
        value=insp_labels_raw,
        key="s_insp_labels",
        help="One label per step, comma-separated. Extra labels are ignored."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Script defaults ──
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown('<h4>📝 Script Pipeline</h4>', unsafe_allow_html=True)
    st.markdown('<p>Default number of steps and step labels for new script projects.</p>', unsafe_allow_html=True)

    script_steps = st.number_input(
        "Default Steps", min_value=1, max_value=12,
        value=int(settings.get("script_steps", 4)),
        key="s_script_steps"
    )
    script_labels_raw = settings.get("script_labels", "Script Generation,Conversion Optimization,Creative Enhancement,Remotion Formatting")
    script_labels = st.text_input(
        "Step Labels (comma-separated)",
        value=script_labels_raw,
        key="s_script_labels",
        help="One label per step, comma-separated."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Workflow tips ──
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown('<h4>💡 Workflow Tips</h4>', unsafe_allow_html=True)
    st.markdown("""
    <p>How to use this system effectively:</p>
    <ul style="font-size:0.82rem;color:#9ca3af;line-height:1.8;">
        <li><b style="color:#e8eaf0;">Write a prompt</b> in the Prompt editor for each step.</li>
        <li>Click <b style="color:#a5b4fc;">📋 Copy Prompt</b> to reveal the full prompt text.</li>
        <li>Paste it into <b style="color:#e8eaf0;">ChatGPT</b> and run it.</li>
        <li>Copy ChatGPT's response and paste it into <b style="color:#a5b4fc;">💬 ChatGPT Output</b>.</li>
        <li>Click <b style="color:#4ade80;">💾 Save Output</b> — the step is marked complete.</li>
        <li>Use the <b style="color:#e8eaf0;">Pipeline Track</b> at the top to see your progress.</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾 Save All Settings", type="primary"):
        new_settings = {
            "inspiration_steps": str(int(insp_steps)),
            "script_steps":      str(int(script_steps)),
            "inspiration_labels": insp_labels.strip(),
            "script_labels":      script_labels.strip(),
        }
        save_settings(new_settings)
        st.success("✓ Settings saved to Cloudflare R2.")


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────

def render_home():
    projects = load_projects()
    total    = len(projects)
    insp     = len(projects[projects["type"] == "inspiration"])
    scr      = len(projects[projects["type"] == "script"])

    st.markdown("""
    <div style="padding:2rem 0 1rem 0;">
        <div style="font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
            letter-spacing:-0.04em;color:#e8eaf0;line-height:1.1;margin-bottom:0.5rem;">
            Creative Video Ads OS
        </div>
        <div style="font-size:0.9rem;color:#6b7280;max-width:500px;">
            A manual creative intelligence system. Write prompts → run in ChatGPT → paste & store outputs.
            No AI APIs. Just structured thinking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    c1, c2, c3 = st.columns(3)
    for col, label, val, clr in [
        (c1, "Total Projects", total, "#6366f1"),
        (c2, "Inspiration", insp, "#22c55e"),
        (c3, "Script", scr, "#f59e0b"),
    ]:
        with col:
            col.markdown(f"""
            <div class="settings-card" style="border-color:rgba(255,255,255,0.05);text-align:center;padding:1.25rem;">
                <div style="font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;color:{clr};">{val}</div>
                <div style="font-size:0.8rem;color:#6b7280;margin-top:0.25rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Quick actions
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("🎬  Start Video Inspiration Project", use_container_width=True, type="primary"):
            st.session_state.page = "inspiration"
            st.session_state.show_new_project_form = True
            st.rerun()
    with qa2:
        if st.button("📝  Start Script Project", use_container_width=True):
            st.session_state.page = "script"
            st.session_state.show_new_project_form = True
            st.rerun()

    if not projects.empty:
        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:Syne,sans-serif;font-size:0.95rem;font-weight:700;'
            'color:#e8eaf0;margin-bottom:0.75rem;">Recent Activity</div>',
            unsafe_allow_html=True
        )
        recent = projects.sort_values("updated_at", ascending=False).head(5)
        for _, proj in recent.iterrows():
            steps_df  = load_steps(proj["id"])
            done, tot = get_step_completion(steps_df)
            pct = int(done / tot * 100) if tot else 0
            type_icon = "🎬" if proj["type"] == "inspiration" else "📝"
            updated   = str(proj.get("updated_at", ""))[:10]
            st.markdown(f"""
            <div class="step-card" style="margin-bottom:0.4rem;">
                <div style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem 1.1rem;">
                    <span style="font-size:1.1rem;">{type_icon}</span>
                    <span style="font-family:Syne,sans-serif;font-size:0.9rem;font-weight:600;color:#e8eaf0;flex:1;">{proj['name']}</span>
                    <span class="badge">{pct}%</span>
                    <span style="font-size:0.7rem;color:#4b5563;">{updated}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────

page = st.session_state.page

if page == "inspiration":
    render_project_workspace("inspiration")
elif page == "script":
    render_project_workspace("script")
elif page == "settings":
    render_settings()
else:
    render_home()
