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
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:           #0d0f14;
    --surface:      #13161e;
    --surface2:     #1a1e28;
    --border:       #252a36;
    --border2:      #2e3445;
    --text:         #e8eaf0;
    --text-muted:   #6b7280;
    --text-dim:     #9ca3af;
    --accent:       #6366f1;
    --accent2:      #818cf8;
    --accent-glow:  rgba(99,102,241,0.15);
    --green:        #22c55e;
    --amber:        #f59e0b;
    --radius:       10px;
    --radius-lg:    16px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1100px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }
[data-testid="stSidebarNav"] { display: none; }
.sidebar-logo {
    font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800;
    letter-spacing: -0.03em; padding: 1rem 0 0.25rem 0;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sidebar-tagline {
    font-size: 0.68rem; color: var(--text-muted); letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 1.25rem;
}
.sidebar-section {
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-muted);
    padding: 0.5rem 0 0.3rem 0; border-top: 1px solid var(--border); margin-top: 0.5rem;
}

/*
 * ✅ FIX 1: Renamed from .badge to .ados-tag
 * Streamlit 1.36+ ships its own .badge component styles that made our
 * <span class="badge"> render as large blue circles instead of pills.
 */
.ados-tag {
    display: inline-flex; align-items: center;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.04em;
    padding: 0.2rem 0.65rem; border-radius: 99px;
    background: var(--accent-glow); border: 1px solid rgba(99,102,241,0.3);
    color: var(--accent2); text-transform: uppercase; white-space: nowrap;
}
.ados-tag-green {
    background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: #4ade80;
}
.ados-tag-amber {
    background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); color: #fbbf24;
}

/*
 * Project header — flat structure so st.html() renders cleanly.
 */
.proj-header-wrap {
    background: var(--surface2); border: 1px solid var(--border);
    border-top: 2px solid var(--accent); border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem; margin-bottom: 1.25rem;
    display: flex; align-items: center; gap: 1rem;
}
.proj-header-icon { font-size: 2rem; line-height: 1; }
.proj-header-name {
    font-family: 'Syne', sans-serif; font-size: 1.35rem; font-weight: 700;
    color: var(--text); letter-spacing: -0.02em; margin-bottom: 0.4rem;
}
.proj-header-meta { display: flex; gap: 0.6rem; flex-wrap: wrap; align-items: center; }
.proj-ctx { font-size: 0.75rem; color: var(--text-muted); }

/* Pipeline */
.pip-wrap { display: flex; align-items: center; overflow-x: auto; padding: 0.5rem 0 1rem 0; }
.pip-node { display: flex; flex-direction: column; align-items: center; gap: 0.35rem; flex-shrink: 0; }
.pip-circle {
    width: 32px; height: 32px; border-radius: 50%;
    background: var(--surface2); border: 2px solid var(--border2);
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--text-muted);
}
.pip-circle-done { background: rgba(34,197,94,0.15); border-color: var(--green); color: var(--green); }
.pip-label { font-size: 0.58rem; color: var(--text-muted); text-align: center; white-space: nowrap; max-width: 58px; overflow: hidden; text-overflow: ellipsis; }
.pip-conn { height: 2px; width: 24px; background: var(--border2); flex-shrink: 0; margin-bottom: 1.4rem; }
.pip-conn-done { background: rgba(34,197,94,0.4); }

/* Step card header */
.step-hdr {
    background: var(--surface2); border: 1px solid var(--border);
    border-bottom: none; border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    padding: 0.75rem 1.25rem; display: flex; align-items: center;
    gap: 0.75rem; margin-top: 0.75rem;
}
.step-num-pill {
    font-family: 'DM Mono', monospace; font-size: 0.65rem; font-weight: 500;
    color: var(--accent2); background: var(--accent-glow);
    border: 1px solid rgba(99,102,241,0.3); border-radius: 6px;
    padding: 0.15rem 0.5rem; letter-spacing: 0.05em;
}
.step-title-txt {
    font-family: 'Syne', sans-serif; font-size: 0.92rem;
    font-weight: 600; color: var(--text); flex: 1;
}
.step-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--border2); }
.step-dot-done  { background: var(--green); box-shadow: 0 0 5px var(--green); }
.step-dot-partial { background: var(--amber); }

/* Project list card */
.proj-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 1.1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.proj-card-name { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem; }
.proj-card-ctx  { font-size: 0.74rem; color: var(--text-muted); margin-bottom: 0.6rem; }
.proj-card-meta { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.proj-card-date { font-size: 0.68rem; color: #374151; margin-left: auto; }
.prog-bar-bg    { height: 4px; background: #1f2937; border-radius: 99px; overflow: hidden; }
.prog-bar-fill  { height: 100%; border-radius: 99px; }

/* Misc */
.sec-label {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.4rem;
}
.prompt-copy-box {
    background: #0a0c10; border: 1px solid var(--border); border-left: 3px solid var(--accent);
    border-radius: var(--radius); padding: 0.75rem 1rem; font-family: 'DM Mono', monospace;
    font-size: 0.78rem; color: #a5b4fc; white-space: pre-wrap; word-break: break-word;
    max-height: 180px; overflow-y: auto; margin-bottom: 0.5rem;
}
/* Resolved prompt — variables replaced, ready to copy */
.prompt-copy-box-resolved {
    background: #071510; border: 1px solid rgba(34,197,94,0.3);
    border-left: 3px solid var(--green);
    border-radius: var(--radius); padding: 0.75rem 1rem; font-family: 'DM Mono', monospace;
    font-size: 0.78rem; color: #86efac; white-space: pre-wrap; word-break: break-word;
    max-height: 200px; overflow-y: auto; margin-bottom: 0.5rem;
}
/* Notes expander */
div[data-testid="stExpander"].notes-exp summary {
    background: rgba(245,158,11,0.05) !important;
    border-color: rgba(245,158,11,0.2) !important;
}
/* Download button */
.stDownloadButton button {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    transition: all 0.15s !important;
}
.stDownloadButton button:hover {
    border-color: var(--green) !important; color: #4ade80 !important;
    background: rgba(34,197,94,0.08) !important;
}
/* Variable hint inline code */
.var-hint code { background: rgba(99,102,241,0.2); border-radius:4px; padding:0.05rem 0.3rem; font-size:0.72rem; }
.settings-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 1.25rem; margin-bottom: 1rem;
}

/* Widget overrides */
.stTextArea textarea {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.875rem !important;
}
.stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px var(--accent-glow) !important; }
.stTextInput input {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important; color: var(--text) !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px var(--accent-glow) !important; }
.stButton button {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; transition: all 0.15s !important;
}
.stButton button:hover { border-color: var(--accent) !important; color: var(--accent2) !important; background: var(--accent-glow) !important; }
div[data-testid="stExpander"] { background: transparent !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
div[data-testid="stExpander"] summary { background: var(--surface2) !important; border-radius: var(--radius) !important; font-size: 0.85rem !important; color: var(--text-dim) !important; }
.stNumberInput input { background: var(--surface2) !important; border: 1px solid var(--border2) !important; color: var(--text) !important; border-radius: var(--radius) !important; }
div[data-testid="stMarkdownContainer"] p { color: var(--text-dim); font-size: 0.875rem; }
.stSuccess { background: rgba(34,197,94,0.1) !important; border: 1px solid rgba(34,197,94,0.3) !important; border-radius: var(--radius) !important; }
.stInfo    { background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: var(--radius) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.25) !important; border-radius: var(--radius) !important; }
hr { border-color: var(--border) !important; margin: 0.75rem 0 !important; }
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
    get_r2().put_object(Bucket=st.secrets["R2_BUCKET"], Key=key, Body=buf.getvalue())


# ─────────────────────────────────────────────
# DATA SCHEMAS
# ─────────────────────────────────────────────

PROJECTS_KEY  = "ados/projects.parquet"
SETTINGS_KEY  = "ados/settings.parquet"
PROJECT_COLS  = ["id", "name", "type", "num_steps", "context", "notes", "created_at", "updated_at"]
STEP_COLS     = ["project_id", "step_num", "label", "prompt", "output", "updated_at"]
SETTINGS_COLS = ["key", "value"]


def steps_key(pid: str) -> str:
    return f"ados/steps/{pid}.parquet"


# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────

def load_projects() -> pd.DataFrame:
    return load_parquet(PROJECTS_KEY, PROJECT_COLS)


def save_projects(df: pd.DataFrame):
    save_parquet(df, PROJECTS_KEY)


def load_steps(pid: str) -> pd.DataFrame:
    df = load_parquet(steps_key(pid), STEP_COLS)
    if not df.empty and "step_num" in df.columns:
        # ✅ FIX 3a: cast to int — Parquet stores int64; Python int comparison otherwise fails
        df["step_num"] = df["step_num"].astype(int)
    return df


def save_steps(df: pd.DataFrame, pid: str):
    if not df.empty and "step_num" in df.columns:
        df["step_num"] = df["step_num"].astype(int)
    save_parquet(df, steps_key(pid))


def _clean(val) -> str:
    """
    ✅ FIX 3b: convert any Parquet value to a clean string.
    Treats None / NaN / 'nan' as empty string so completion is detected correctly.
    """
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


def get_step_completion(steps_df: pd.DataFrame) -> tuple:
    total = len(steps_df)
    if total == 0:
        return 0, 0
    done = int(steps_df["output"].apply(_clean).ne("").sum())
    return done, total


def load_settings() -> dict:
    df = load_parquet(SETTINGS_KEY, SETTINGS_COLS)
    defaults = {
        "inspiration_steps":  "3",
        "script_steps":       "4",
        "inspiration_labels": "Raw Analysis,Inspiration Cards,Creative Amplification",
        "script_labels":      "Script Generation,Conversion Optimization,Creative Enhancement,Remotion Formatting",
        # Default prompts per step — empty by default, editable in Settings
        "inspiration_prompt_1": "",
        "inspiration_prompt_2": "",
        "inspiration_prompt_3": "",
        "script_prompt_1": "",
        "script_prompt_2": "",
        "script_prompt_3": "",
        "script_prompt_4": "",
    }
    if df.empty:
        return defaults
    result = defaults.copy()
    for _, row in df.iterrows():
        result[str(row["key"])] = str(row["value"])
    return result


def get_default_prompts(settings: dict, proj_type: str, num_steps: int) -> list:
    """Return list of default prompts for each step, from settings."""
    prefix = "inspiration_prompt_" if proj_type == "inspiration" else "script_prompt_"
    return [_clean(settings.get(f"{prefix}{i}", "")) for i in range(1, num_steps + 1)]


def save_settings(s: dict):
    save_parquet(pd.DataFrame([{"key": k, "value": v} for k, v in s.items()], columns=SETTINGS_COLS), SETTINGS_KEY)


def create_project(name: str, proj_type: str, num_steps: int, context: str,
                   labels: list, default_prompts: list = None) -> str:
    pid = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    projects = load_projects()
    new_proj_df = pd.DataFrame([{
        "id": pid, "name": name, "type": proj_type,
        "num_steps": num_steps, "context": context,
        "notes": "", "created_at": now, "updated_at": now,
    }])
    combined = pd.concat([projects, new_proj_df], ignore_index=True)
    # ensure notes column exists for older data
    if "notes" not in combined.columns:
        combined["notes"] = ""
    save_projects(combined)
    steps_rows = [{
        "project_id": pid, "step_num": int(i),
        "label": labels[i-1] if i-1 < len(labels) else f"Step {i}",
        "prompt": (default_prompts[i-1] if default_prompts and i-1 < len(default_prompts) else ""),
        "output": "", "updated_at": now,
    } for i in range(1, num_steps + 1)]
    save_steps(pd.DataFrame(steps_rows, columns=STEP_COLS), pid)
    return pid


def delete_project(pid: str):
    projects = load_projects()
    save_projects(projects[projects["id"] != pid])


# ─────────────────────────────────────────────
# DUPLICATE / EXPORT / NOTES
# ─────────────────────────────────────────────

def duplicate_project(pid: str) -> str:
    """Clone a project: copy all prompts, reset all outputs."""
    projects = load_projects()
    orig_row = projects[projects["id"] == pid]
    if orig_row.empty:
        return ""
    orig      = orig_row.iloc[0]
    new_pid   = str(uuid.uuid4())[:8]
    now       = datetime.utcnow().isoformat()
    new_name  = f"{orig['name']} (copy)"
    new_row   = pd.DataFrame([{
        "id": new_pid, "name": new_name, "type": orig["type"],
        "num_steps": orig["num_steps"],
        "context":   _clean(orig.get("context", "")),
        "notes":     _clean(orig.get("notes",   "")),
        "created_at": now, "updated_at": now,
    }])
    combined = pd.concat([projects, new_row], ignore_index=True)
    if "notes" not in combined.columns:
        combined["notes"] = ""
    save_projects(combined)

    # Copy steps — keep prompts and labels, blank outputs
    orig_steps = load_steps(pid)
    if not orig_steps.empty:
        new_steps = orig_steps.copy()
        new_steps["project_id"] = new_pid
        new_steps["output"]     = ""
        new_steps["updated_at"] = now
        save_steps(new_steps, new_pid)
    return new_pid


def save_project_notes(pid: str, notes: str):
    """Persist freeform notes on a project."""
    projects = load_projects()
    if "notes" not in projects.columns:
        projects["notes"] = ""
    now = datetime.utcnow().isoformat()
    projects.loc[projects["id"] == pid, "notes"]      = notes
    projects.loc[projects["id"] == pid, "updated_at"] = now
    save_projects(projects)


def export_project_markdown(proj: pd.Series, steps_df: pd.DataFrame) -> str:
    """Generate a clean Markdown export of a project."""
    type_label = "Video Inspiration" if proj["type"] == "inspiration" else "Script"
    done, total = get_step_completion(steps_df)
    lines = [
        f"# {proj['name']}",
        f"",
        f"**Type:** {type_label}  ",
        f"**Steps:** {done}/{total} completed  ",
        f"**Created:** {str(proj.get('created_at',''))[:10]}  ",
        f"**Updated:** {str(proj.get('updated_at',''))[:10]}  ",
    ]
    ctx = _clean(proj.get("context", ""))
    if ctx:
        lines += ["", f"**Context:** {ctx}"]
    notes = _clean(proj.get("notes", ""))
    if notes:
        lines += ["", "## Notes", "", notes]
    lines += ["", "---", ""]

    for _, row in steps_df.sort_values("step_num").iterrows():
        step_num = int(row["step_num"])
        label    = _clean(row.get("label", f"Step {step_num}"))
        prompt   = _clean(row.get("prompt", ""))
        output   = _clean(row.get("output", ""))
        lines += [f"## Step {step_num} — {label}", ""]
        if prompt:
            lines += ["### Prompt", "", prompt, ""]
        if output:
            lines += ["### Output", "", output, ""]
        lines += ["---", ""]

    return "
".join(lines)


def resolve_prompt_variables(prompt: str, steps_df: pd.DataFrame, current_step: int) -> tuple[str, list]:
    """
    Replace {{step_N}} placeholders with actual step outputs.
    Returns (resolved_prompt, list_of_missing_vars).
    Only resolves steps < current_step (previous steps).
    """
    import re
    resolved  = prompt
    missing   = []
    for match in re.finditer(r"\{\{step_(\d+)\}\}", prompt):
        n   = int(match.group(1))
        tag = match.group(0)
        row = steps_df[steps_df["step_num"] == n]
        if not row.empty and _clean(row.iloc[0]["output"]):
            resolved = resolved.replace(tag, _clean(row.iloc[0]["output"]))
        else:
            resolved = resolved.replace(tag, f"[OUTPUT STEP {n} NOT YET AVAILABLE]")
            missing.append(n)
    return resolved, missing


def _upsert_step_field(pid: str, step_num: int, field: str, value: str):
    steps = load_steps(pid)
    now   = datetime.utcnow().isoformat()
    mask  = steps["step_num"] == int(step_num)   # ✅ FIX 3a applied here too
    if mask.any():
        steps.loc[mask, field]        = value
        steps.loc[mask, "updated_at"] = now
    else:
        new_row = pd.DataFrame([{
            "project_id": pid, "step_num": int(step_num),
            "label": f"Step {step_num}", "prompt": "", "output": "",
            "updated_at": now,
        }])
        new_row[field] = value
        steps = pd.concat([steps, new_row], ignore_index=True)
    save_steps(steps, pid)
    projects = load_projects()
    projects.loc[projects["id"] == pid, "updated_at"] = now
    save_projects(projects)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

for _k, _v in {"page": "home", "selected_project": None, "show_new_project_form": False}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">AdOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">Creative Video Ads OS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)

        for icon, label, pg in [
            ("🎬", "Video Inspiration", "inspiration"),
            ("📝", "Script Projects",   "script"),
            ("⚙️",  "Settings",          "settings"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg
                st.session_state.selected_project = None
                st.rerun()

        cur = st.session_state.page
        if cur in ("inspiration", "script"):
            projects = load_projects()
            filtered = projects[projects["type"] == cur]
            if not filtered.empty:
                st.markdown('<div class="sidebar-section">Recent Projects</div>', unsafe_allow_html=True)
                for _, proj in filtered.sort_values("updated_at", ascending=False).head(8).iterrows():
                    lbl = proj["name"][:22] + "…" if len(proj["name"]) > 22 else proj["name"]
                    sel = st.session_state.selected_project == proj["id"]
                    if st.button(("▶ " if sel else "  ") + lbl, key=f"sb_{proj['id']}", use_container_width=True):
                        st.session_state.selected_project = proj["id"]
                        st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.65rem;color:#374151;text-align:center;">'
            'Manual AI workflow · No APIs<br>Data stored in Cloudflare R2</div>',
            unsafe_allow_html=True,
        )


render_sidebar()


# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────

def _tag(text: str, variant: str = "") -> str:
    """Return an .ados-tag span — safely renamed away from Streamlit's .badge."""
    cls = f"ados-tag ados-tag-{variant}" if variant else "ados-tag"
    return f'<span class="{cls}">{text}</span>'


def project_header(name: str, proj_type: str, num_steps: int, done: int, context: str):
    """
    ✅ FIX 2: uses st.html() (Streamlit 1.36+) instead of st.markdown().
    st.html() renders arbitrary HTML without Streamlit's markdown sanitizer
    mangling nested closing </div> tags into visible text.
    """
    icon  = "🎬" if proj_type == "inspiration" else "📝"
    tlabel = "Video Inspiration" if proj_type == "inspiration" else "Script Project"
    pct   = int(done / num_steps * 100) if num_steps else 0

    if done == num_steps and num_steps > 0:
        status = _tag("✓ Complete", "green")
    elif done > 0:
        status = _tag(f"{pct}% Done", "amber")
    else:
        status = _tag("Not Started")

    ctx = (
        f'<span class="proj-ctx">· {context[:70]}{"…" if len(context)>70 else ""}</span>'
        if context else ""
    )
    st.html(f"""
    <div class="proj-header-wrap">
        <span class="proj-header-icon">{icon}</span>
        <div>
            <div class="proj-header-name">{name}</div>
            <div class="proj-header-meta">
                {_tag(tlabel)}
                {_tag(f"{done}/{num_steps} Steps")}
                {status}
                {ctx}
            </div>
        </div>
    </div>
    """)


def pipeline_track(steps_df: pd.DataFrame, num_steps: int):
    """✅ FIX 2: uses st.html() for safe nested HTML rendering."""
    html = ""
    for i in range(1, num_steps + 1):
        row       = steps_df[steps_df["step_num"] == i]
        has_out   = not row.empty and _clean(row.iloc[0]["output"]) != ""
        label     = str(row.iloc[0]["label"])[:12] if not row.empty else f"Step {i}"
        circ_cls  = "pip-circle pip-circle-done" if has_out else "pip-circle"
        html += f'<div class="pip-node"><div class="{circ_cls}">{i}</div><div class="pip-label">{label}</div></div>'
        if i < num_steps:
            conn_cls = "pip-conn pip-conn-done" if has_out else "pip-conn"
            html += f'<div class="{conn_cls}"></div>'
    st.html(f'<div class="pip-wrap">{html}</div>')


def step_card_header(label: str, step_num: int, has_out: bool, has_pr: bool):
    """✅ FIX 2: flat single-div via st.html()."""
    dot_cls = "step-dot step-dot-done" if has_out else ("step-dot step-dot-partial" if has_pr else "step-dot")
    st.html(f"""
    <div class="step-hdr">
        <span class="step-num-pill">STEP {step_num}</span>
        <span class="step-title-txt">{label}</span>
        <span class="{dot_cls}"></span>
    </div>
    """)


def step_card(step_row: pd.Series, pid: str, step_num: int, num_steps: int,
              steps_df: pd.DataFrame = None):
    label  = str(step_row.get("label",  f"Step {step_num}"))
    prompt = _clean(step_row.get("prompt", ""))
    output = _clean(step_row.get("output", ""))
    has_out = output != ""
    has_pr  = prompt != ""

    # Detect {{step_N}} variables in prompt
    import re
    has_vars = bool(re.search(r"{{step_\d+}}", prompt)) if prompt else False

    step_card_header(label, step_num, has_out, has_pr)

    col_p, col_o = st.columns(2, gap="medium")

    with col_p:
        with st.expander("✏️  Prompt", expanded=not has_out):
            # Variable hint
            if has_vars:
                st.html(
                    "<div style='font-size:0.7rem;color:#818cf8;background:rgba(99,102,241,0.1);"
                    "border:1px solid rgba(99,102,241,0.25);border-radius:7px;"
                    "padding:0.35rem 0.65rem;margin-bottom:0.5rem;'>"
                    "&#x26A1; Ce prompt contient des variables "
                    "<code style='background:rgba(99,102,241,0.2);border-radius:4px;"
                    "padding:0.05rem 0.3rem;font-size:0.72rem;'>{{step_N}}</code>"
                    " — elles seront résolues automatiquement au moment de la copie."
                    "</div>"
                )

            st.markdown('<div class="sec-label">🔧 Prompt</div>', unsafe_allow_html=True)
            new_prompt = st.text_area(
                "Prompt", value=prompt, height=180,
                key=f"p_{pid}_{step_num}", label_visibility="collapsed",
                placeholder=(
                    "Écris ton prompt ChatGPT ici…\n\n"
                    "💡 Astuce : utilise {{step_1}}, {{step_2}}… pour injecter "
                    "automatiquement l'output d'une étape précédente."
                ),
            )
            sc, cc = st.columns(2)
            with sc:
                if st.button("💾 Sauvegarder", key=f"sp_{pid}_{step_num}"):
                    _upsert_step_field(pid, step_num, "prompt", new_prompt)
                    st.success("Prompt sauvegardé.")
                    st.rerun()
            with cc:
                if st.button("📋 Copier", key=f"cp_{pid}_{step_num}"):
                    st.session_state[f"showcopy_{pid}_{step_num}"] = True

            if st.session_state.get(f"showcopy_{pid}_{step_num}"):
                # Resolve variables if steps_df provided
                display_prompt = new_prompt or "(aucun prompt)"
                missing_vars   = []
                if steps_df is not None and has_vars:
                    display_prompt, missing_vars = resolve_prompt_variables(
                        new_prompt, steps_df, step_num
                    )
                    if missing_vars:
                        mv_list = ", ".join(f"step_{n}" for n in missing_vars)
                        st.warning(f"⚠️ Variables non disponibles : {mv_list}")

                box_style = "prompt-copy-box-resolved" if (has_vars and not missing_vars) else "prompt-copy-box"
                st.markdown(
                    f'<div class="{box_style}">{display_prompt}</div>',
                    unsafe_allow_html=True,
                )
                if has_vars and not missing_vars:
                    st.caption("✅ Variables résolues — texte prêt à coller dans ChatGPT.")
                else:
                    st.caption("☝️ Sélectionne tout → copie → colle dans ChatGPT.")
                if st.button("✕ Fermer", key=f"dis_{pid}_{step_num}"):
                    st.session_state[f"showcopy_{pid}_{step_num}"] = False

    with col_o:
        with st.expander("💬  Output ChatGPT", expanded=True):
            st.markdown('<div class="sec-label">📥 Colle la réponse ChatGPT ici</div>', unsafe_allow_html=True)
            new_output = st.text_area(
                "Output", value=output, height=200,
                key=f"o_{pid}_{step_num}", label_visibility="collapsed",
                placeholder="Colle ici la réponse de ChatGPT après avoir lancé ton prompt…",
            )
            so, clr = st.columns(2)
            with so:
                if st.button("💾 Sauvegarder", key=f"so_{pid}_{step_num}", type="primary"):
                    _upsert_step_field(pid, step_num, "output", new_output)
                    st.success("Output sauvegardé !")
                    st.rerun()
            with clr:
                if has_out and st.button("🗑 Effacer", key=f"cl_{pid}_{step_num}"):
                    _upsert_step_field(pid, step_num, "output", "")
                    st.rerun()

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PROJECT WORKSPACE
# ─────────────────────────────────────────────

def render_project_workspace(proj_type: str):
    settings = load_settings()
    projects = load_projects()
    filtered = projects[projects["type"] == proj_type].copy()

    def_steps    = int(settings.get("inspiration_steps" if proj_type=="inspiration" else "script_steps", 3))
    raw_labels   = settings.get("inspiration_labels" if proj_type=="inspiration" else "script_labels", "")
    def_labels   = [l.strip() for l in raw_labels.split(",") if l.strip()]
    def_prompts  = get_default_prompts(settings, proj_type, 12)  # fetch up to 12 default prompts

    icon      = "🎬" if proj_type == "inspiration" else "📝"
    type_name = "Video Inspiration" if proj_type == "inspiration" else "Script"

    h_col, btn_col = st.columns([3, 1])
    with h_col:
        st.markdown(
            f'<div style="font-family:Syne,sans-serif;font-size:1.55rem;font-weight:800;'
            f'letter-spacing:-0.03em;color:#e8eaf0;">{icon} {type_name} Projects</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="font-size:0.78rem;color:#6b7280;">'
            f'{len(filtered)} project{"s" if len(filtered)!=1 else ""} · '
            f'Write prompt → copy to ChatGPT → paste output</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        if st.button("＋  New Project", use_container_width=True, type="primary"):
            st.session_state.show_new_project_form = not st.session_state.get("show_new_project_form", False)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    # ── New project form ──
    if st.session_state.get("show_new_project_form"):
        with st.container(border=True):
            st.markdown(f"**Create {type_name} Project**")
            fc1, fc2 = st.columns([2, 1])
            with fc1:
                proj_name = st.text_input("Project Name", placeholder="e.g. Nike Air Max Analysis", key="np_name")
                context   = st.text_input("Context / Notes (optional)", placeholder="Target audience, product, angle…", key="np_ctx")
            with fc2:
                num_steps = st.number_input("Number of Steps", min_value=1, max_value=12, value=def_steps, key="np_steps")

            st.markdown('<div class="sec-label" style="margin-top:0.25rem">Step Labels</div>', unsafe_allow_html=True)
            label_cols  = st.columns(min(int(num_steps), 4))
            step_labels = []
            for i in range(int(num_steps)):
                with label_cols[i % 4]:
                    step_labels.append(st.text_input(
                        f"Step {i+1}", key=f"nl_{i}",
                        value=def_labels[i] if i < len(def_labels) else f"Step {i+1}",
                    ))

            cr, ca = st.columns(2)
            with cr:
                if st.button("✓  Create Project", type="primary", use_container_width=True, key="do_create"):
                    if proj_name.strip():
                        pid = create_project(proj_name.strip(), proj_type, int(num_steps), context.strip(), step_labels, def_prompts)
                        st.session_state.selected_project      = pid
                        st.session_state.show_new_project_form = False
                        st.success(f"Project '{proj_name}' created!")
                        st.rerun()
                    else:
                        st.warning("Please enter a project name.")
            with ca:
                if st.button("✕  Cancel", use_container_width=True, key="do_cancel"):
                    st.session_state.show_new_project_form = False
                    st.rerun()

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── No project selected ──
    selected_id = st.session_state.get("selected_project")
    if not selected_id or selected_id not in filtered["id"].values:
        if filtered.empty:
            st.html("""
            <div class="settings-card" style="text-align:center;padding:3.5rem 2rem;">
                <div style="font-size:2.5rem;margin-bottom:0.75rem;">✦</div>
                <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:#9ca3af;margin-bottom:0.4rem;">No projects yet</div>
                <div style="font-size:0.82rem;color:#6b7280;">Click "＋ New Project" to create your first workflow.</div>
            </div>
            """)
        else:
            _render_project_list(filtered)
        return

    # ── Project workspace ──
    proj_row = filtered[filtered["id"] == selected_id]
    if proj_row.empty:
        st.session_state.selected_project = None
        st.rerun()
        return

    proj     = proj_row.iloc[0]
    steps_df = load_steps(selected_id)
    done, total = get_step_completion(steps_df)

    project_header(proj["name"], proj_type, total, done, str(proj.get("context", "")))

    # ── Actions bar ──
    a1, a2, a3, a4, a5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2])
    with a1:
        if st.button("← Projets", use_container_width=True):
            st.session_state.selected_project = None
            st.rerun()
    with a2:
        if st.button("📋 Dupliquer", use_container_width=True):
            new_pid = duplicate_project(selected_id)
            if new_pid:
                st.session_state.selected_project = new_pid
                st.success("Projet dupliqué !")
                st.rerun()
    with a3:
        md_export = export_project_markdown(proj, steps_df)
        safe_name = proj["name"].replace(" ", "_").replace("/", "-")[:40]
        st.download_button(
            "⬇️ Export .md",
            data=md_export.encode("utf-8"),
            file_name=f"{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with a4:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    with a5:
        if st.button("🗑 Supprimer", use_container_width=True):
            st.session_state[f"cdel_{selected_id}"] = True

    if st.session_state.get(f"cdel_{selected_id}"):
        st.warning(f"⚠️ Supprimer le projet '{proj['name']}'? Action irréversible.")
        d1, d2 = st.columns(2)
        with d1:
            if st.button("Oui, supprimer", key="del_yes", type="primary"):
                delete_project(selected_id)
                st.session_state.selected_project = None
                st.session_state.pop(f"cdel_{selected_id}", None)
                st.rerun()
        with d2:
            if st.button("Annuler", key="del_no"):
                st.session_state.pop(f"cdel_{selected_id}", None)

    # ── Project Notes ──
    current_notes = _clean(proj.get("notes", ""))
    with st.expander("📓  Notes du projet", expanded=bool(current_notes)):
        new_notes = st.text_area(
            "Notes",
            value=current_notes,
            height=110,
            key=f"notes_{selected_id}",
            label_visibility="collapsed",
            placeholder="Ajoute des notes libres ici : contexte, idées, références, brief client…",
        )
        if st.button("💾 Sauvegarder les notes", key=f"save_notes_{selected_id}"):
            save_project_notes(selected_id, new_notes)
            st.success("Notes sauvegardées.")
            st.rerun()

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    pipeline_track(steps_df, total)

    for i in range(1, total + 1):
        rows = steps_df[steps_df["step_num"] == i]
        row  = rows.iloc[0] if not rows.empty else pd.Series({"label": f"Step {i}", "prompt": "", "output": ""})
        step_card(row, selected_id, i, total, steps_df=steps_df)


def _render_project_list(filtered: pd.DataFrame):
    cols = st.columns(2, gap="medium")
    for idx, (_, proj) in enumerate(filtered.sort_values("updated_at", ascending=False).iterrows()):
        with cols[idx % 2]:
            steps_df  = load_steps(proj["id"])
            done, tot = get_step_completion(steps_df)
            pct       = int(done / tot * 100) if tot else 0
            updated   = str(proj.get("updated_at", ""))[:10]
            ctx_txt   = str(proj.get("context", ""))
            ctx_short = ctx_txt[:55] + "…" if len(ctx_txt) > 55 else ctx_txt
            bar_color = "#22c55e" if done == tot and tot > 0 else ("#f59e0b" if done > 0 else "#374151")
            tag_v     = "green" if done == tot and tot > 0 else ("amber" if done > 0 else "")

            # ✅ FIX 2: st.html() — no stray </div> in the page
            st.html(f"""
            <div class="proj-card">
                <div class="proj-card-name">{proj['name']}</div>
                <div class="proj-card-ctx">{ctx_short or "No context added"}</div>
                <div class="proj-card-meta">
                    {_tag(f"{tot} steps")}
                    {_tag(f"{done}/{tot} done", tag_v)}
                    <span class="proj-card-date">{updated}</span>
                </div>
                <div class="prog-bar-bg">
                    <div class="prog-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
                </div>
            </div>
            """)

            if st.button("Open →", key=f"open_{proj['id']}", use_container_width=True):
                st.session_state.selected_project = proj["id"]
                st.rerun()


# ─────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────

def _settings_prompt_section(settings: dict, proj_type: str, num_steps: int,
                              labels: list, collected: dict):
    """
    Render per-step prompt editors for one pipeline type.
    Writes widget values into `collected` dict so the caller can save them.
    """
    prefix    = "inspiration_prompt_" if proj_type == "inspiration" else "script_prompt_"
    type_icon = "🎬" if proj_type == "inspiration" else "📝"
    type_name = "Video Inspiration" if proj_type == "inspiration" else "Script"

    st.markdown(
        f'<div style="font-size:0.78rem;color:#6b7280;margin:0.25rem 0 0.75rem 0;">'
        f'Ces prompts seront pré-remplis automatiquement lors de la création d\'un nouveau projet {type_name}.</div>',
        unsafe_allow_html=True,
    )

    for i in range(1, num_steps + 1):
        key_name = f"{prefix}{i}"
        step_label = labels[i-1] if i-1 < len(labels) else f"Step {i}"

        # Step header
        st.html(f"""
        <div style="display:flex;align-items:center;gap:0.6rem;
             padding:0.55rem 0.9rem;
             background:#1a1e28;border:1px solid #252a36;
             border-bottom:none;
             border-radius:10px 10px 0 0;margin-top:0.75rem;">
            <span style="font-family:'DM Mono',monospace;font-size:0.65rem;
                  color:#818cf8;background:rgba(99,102,241,0.15);
                  border:1px solid rgba(99,102,241,0.3);border-radius:6px;
                  padding:0.15rem 0.5rem;">STEP {i}</span>
            <span style="font-family:Syne,sans-serif;font-size:0.88rem;
                  font-weight:600;color:#e8eaf0;">{step_label}</span>
        </div>
        """)

        current_val = _clean(settings.get(key_name, ""))
        new_val = st.text_area(
            f"Prompt par défaut — Step {i}",
            value=current_val,
            height=130,
            key=f"dp_{proj_type}_{i}",
            label_visibility="collapsed",
            placeholder=f"Prompt par defaut - etape {i} ({step_label})\n\nCe texte sera pre-rempli dans chaque nouveau projet.",
        )
        collected[key_name] = new_val


def render_settings():
    st.markdown(
        '<div style="font-family:Syne,sans-serif;font-size:1.55rem;font-weight:800;'
        'letter-spacing:-0.03em;color:#e8eaf0;">⚙️ Settings</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:0.78rem;color:#6b7280;margin-bottom:1.25rem;">'
        'Paramètres globaux · Sauvegardés dans Cloudflare R2</div>',
        unsafe_allow_html=True,
    )

    settings = load_settings()
    collected = {}   # will hold ALL keys to save

    # ── Tabs: one per pipeline type ──
    tab_insp, tab_script, tab_guide = st.tabs(["🎬  Video Inspiration", "📝  Script", "💡  Guide"])

    # ════════════════════════════════════════════
    # TAB 1 — INSPIRATION
    # ════════════════════════════════════════════
    with tab_insp:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("**Structure du pipeline**")
            c1, c2 = st.columns([1, 2])
            with c1:
                insp_steps = st.number_input(
                    "Nombre d'étapes par défaut", min_value=1, max_value=12,
                    value=int(settings.get("inspiration_steps", 3)), key="s_is",
                )
                collected["inspiration_steps"] = str(int(insp_steps))
            with c2:
                insp_labels_raw = st.text_input(
                    "Labels des étapes (séparés par des virgules)",
                    value=settings.get("inspiration_labels", ""),
                    key="s_il",
                )
                collected["inspiration_labels"] = insp_labels_raw.strip()

        insp_labels = [l.strip() for l in insp_labels_raw.split(",") if l.strip()]

        with st.container(border=True):
            st.markdown("**✏️ Prompts par défaut — Video Inspiration**")
            _settings_prompt_section(settings, "inspiration", int(insp_steps), insp_labels, collected)

    # ════════════════════════════════════════════
    # TAB 2 — SCRIPT
    # ════════════════════════════════════════════
    with tab_script:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("**Structure du pipeline**")
            c1, c2 = st.columns([1, 2])
            with c1:
                script_steps = st.number_input(
                    "Nombre d'étapes par défaut", min_value=1, max_value=12,
                    value=int(settings.get("script_steps", 4)), key="s_ss",
                )
                collected["script_steps"] = str(int(script_steps))
            with c2:
                script_labels_raw = st.text_input(
                    "Labels des étapes (séparés par des virgules)",
                    value=settings.get("script_labels", ""),
                    key="s_sl",
                )
                collected["script_labels"] = script_labels_raw.strip()

        script_labels = [l.strip() for l in script_labels_raw.split(",") if l.strip()]

        with st.container(border=True):
            st.markdown("**✏️ Prompts par défaut — Script**")
            _settings_prompt_section(settings, "script", int(script_steps), script_labels, collected)

    # ════════════════════════════════════════════
    # TAB 3 — GUIDE
    # ════════════════════════════════════════════
    with tab_guide:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**💡 Comment utiliser AdOS**")
            st.markdown("""
**Dans Settings :**
- Définis le **nombre d'étapes** et les **labels** pour chaque pipeline.
- Écris un **prompt par défaut** pour chaque étape — il sera pré-rempli automatiquement lors de la création de chaque nouveau projet.

**Dans un projet :**
- Les prompts par défaut sont déjà en place — modifie-les si besoin.
- Clique **📋 Copy Prompt** → sélectionne tout le texte → colle dans ChatGPT.
- Copie la réponse de ChatGPT → colle dans **💬 ChatGPT Output** → **💾 Save Output**.
- Le point de l'étape devient **vert** et la pipeline track se met à jour.
            """)

    # ── Save button (outside tabs, always visible) ──
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    if st.button("💾 Sauvegarder tous les paramètres", type="primary"):
        # Merge with existing settings so we don't lose keys not on screen
        existing = load_settings()
        existing.update(collected)
        save_settings(existing)
        st.success("✓ Paramètres sauvegardés dans Cloudflare R2.")


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────

def render_home():
    projects = load_projects()
    total = len(projects)
    insp  = int((projects["type"] == "inspiration").sum()) if not projects.empty else 0
    scr   = int((projects["type"] == "script").sum())      if not projects.empty else 0

    st.markdown("""
    <div style="padding:1.5rem 0 1rem 0;">
        <div style="font-family:Syne,sans-serif;font-size:2.1rem;font-weight:800;
            letter-spacing:-0.04em;color:#e8eaf0;line-height:1.15;margin-bottom:0.5rem;">
            Creative Video Ads OS
        </div>
        <div style="font-size:0.875rem;color:#6b7280;max-width:480px;">
            Manual AI workflow. Write prompts → run in ChatGPT → paste &amp; store outputs.
            No AI APIs — just structured thinking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, lbl, val, clr in [
        (c1, "Total Projects", total, "#6366f1"),
        (c2, "Inspiration",    insp,  "#22c55e"),
        (c3, "Script",         scr,   "#f59e0b"),
    ]:
        with col:
            st.html(f"""
            <div class="settings-card" style="text-align:center;padding:1.25rem;">
                <div style="font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;color:{clr};">{val}</div>
                <div style="font-size:0.78rem;color:#6b7280;margin-top:0.2rem;">{lbl}</div>
            </div>
            """)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("🎬  New Video Inspiration Project", use_container_width=True, type="primary"):
            st.session_state.page = "inspiration"
            st.session_state.show_new_project_form = True
            st.rerun()
    with qa2:
        if st.button("📝  New Script Project", use_container_width=True):
            st.session_state.page = "script"
            st.session_state.show_new_project_form = True
            st.rerun()

    if not projects.empty:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.92rem;font-weight:700;color:#e8eaf0;margin-bottom:0.5rem;">Recent Activity</div>', unsafe_allow_html=True)
        for _, proj in projects.sort_values("updated_at", ascending=False).head(5).iterrows():
            steps_df  = load_steps(proj["id"])
            done, tot = get_step_completion(steps_df)
            pct       = int(done / tot * 100) if tot else 0
            icon      = "🎬" if proj["type"] == "inspiration" else "📝"
            updated   = str(proj.get("updated_at", ""))[:10]
            tag_v     = "green" if done == tot and tot > 0 else ("amber" if done > 0 else "")
            st.html(f"""
            <div class="proj-card" style="padding:0.75rem 1.1rem;margin-bottom:0.3rem;">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                    <span style="font-size:1.1rem;">{icon}</span>
                    <span style="font-family:Syne,sans-serif;font-size:0.88rem;font-weight:600;color:#e8eaf0;flex:1;">{proj['name']}</span>
                    {_tag(f"{pct}%", tag_v)}
                    <span style="font-size:0.68rem;color:#374151;">{updated}</span>
                </div>
            </div>
            """)


# ─────────────────────────────────────────────
# ROUTER
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
