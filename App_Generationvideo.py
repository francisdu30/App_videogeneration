import streamlit as st
import pandas as pd
import boto3
import io
from datetime import datetime

# =========================
# R2 CONNECTION
# =========================

@st.cache_resource
def get_r2():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{st.secrets['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=st.secrets["R2_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["R2_SECRET_KEY"],
        region_name="auto"
    )

def load_parquet(key, cols):
    try:
        obj = get_r2().get_object(Bucket=st.secrets["R2_BUCKET"], Key=key)
        return pd.read_parquet(io.BytesIO(obj["Body"].read()))
    except Exception:
        return pd.DataFrame(columns=cols)

def save_parquet(df, key):
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    get_r2().put_object(Bucket=st.secrets["R2_BUCKET"], Key=key, Body=buf.getvalue())

# =========================
# DATA FILES
# =========================

VIDEO_FILE = "video_projects.parquet"
SCRIPT_FILE = "script_projects.parquet"
SETTINGS_FILE = "settings.parquet"

video_df = load_parquet(VIDEO_FILE, ["id", "name", "created_at"])
script_df = load_parquet(SCRIPT_FILE, ["id", "name", "created_at"])
settings_df = load_parquet(SETTINGS_FILE, ["key", "value"])

# =========================
# SETTINGS HELPERS
# =========================

def get_setting(key, default):
    if key in settings_df["key"].values:
        return int(settings_df[settings_df["key"] == key]["value"].iloc[0])
    return default

def set_setting(key, value):
    global settings_df
    if key in settings_df["key"].values:
        settings_df.loc[settings_df["key"] == key, "value"] = value
    else:
        settings_df = pd.concat([settings_df, pd.DataFrame([{
            "key": key,
            "value": value
        }])])
    save_parquet(settings_df, SETTINGS_FILE)

# =========================
# UI HELPERS
# =========================

def render_header(title, subtitle, steps):
    st.markdown(f"""
    <div style="
        padding:14px;
        border-radius:12px;
        background:#111;
        color:white;
        margin-bottom:15px;
    ">
        <h2 style="margin:0">{title}</h2>
        <small>{subtitle}</small><br>
        <small>Steps: {steps}</small>
    </div>
    """, unsafe_allow_html=True)

def step_card(project_id, step_index, prefix):
    st.markdown(f"### 🧩 Step {step_index}")

    prompt_key = f"{prefix}_prompt_{project_id}_{step_index}"
    output_key = f"{prefix}_output_{project_id}_{step_index}"

    with st.expander("✏️ Prompt (editable)", expanded=False):
        st.text_area("Prompt", key=prompt_key, height=140)

    with st.expander("💬 ChatGPT Output", expanded=True):
        st.text_area("Response", key=output_key, height=180)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save", key=f"save_{prompt_key}"):
            st.success("Saved")

    with col2:
        st.button("📋 Copy", key=f"copy_{prompt_key}")

# =========================
# SIDEBAR NAVIGATION
# =========================

st.sidebar.title("🎬 Creative OS")

mode = st.sidebar.radio(
    "Navigation",
    ["📁 Video Inspiration", "🎥 Script Projects", "⚙️ Settings"]
)

st.sidebar.divider()
st.sidebar.caption("Manual Prompt Engineering System")

# =========================
# SETTINGS PAGE
# =========================

if mode == "⚙️ Settings":

    st.title("⚙️ Global Settings")

    insp_steps = st.number_input(
        "Default Inspiration Steps",
        1, 10,
        value=get_setting("insp_steps", 3)
    )

    script_steps = st.number_input(
        "Default Script Steps",
        1, 10,
        value=get_setting("script_steps", 4)
    )

    if st.button("Save Settings"):
        set_setting("insp_steps", insp_steps)
        set_setting("script_steps", script_steps)
        st.success("Settings updated")

# =========================
# VIDEO INSPIRATION SYSTEM
# =========================

elif mode == "📁 Video Inspiration":

    st.title("📁 Video Inspiration System")

    # CREATE PROJECT
    st.subheader("➕ Create Project")

    new_name = st.text_input("Project name")

    if st.button("Create Video Project"):
        if new_name:
            new_id = int(video_df["id"].max() + 1) if not video_df.empty else 1

            video_df = pd.concat([video_df, pd.DataFrame([{
                "id": new_id,
                "name": new_name,
                "created_at": str(datetime.now())
            }])])

            save_parquet(video_df, VIDEO_FILE)
            st.success("Project created")

    st.divider()

    if not video_df.empty:

        selected = st.selectbox("Select project", video_df["name"])
        project_id = video_df[video_df["name"] == selected]["id"].iloc[0]

        steps = get_setting("insp_steps", 3)

        render_header(
            selected,
            "Video → Inspiration Pipeline",
            steps
        )

        for i in range(1, steps + 1):
            step_card(project_id, i, "video")

# =========================
# SCRIPT SYSTEM
# =========================

elif mode == "🎥 Script Projects":

    st.title("🎥 Script System")

    # CREATE PROJECT
    st.subheader("➕ Create Script Project")

    new_name = st.text_input("Project name")

    if st.button("Create Script Project"):
        if new_name:
            new_id = int(script_df["id"].max() + 1) if not script_df.empty else 1

            script_df = pd.concat([script_df, pd.DataFrame([{
                "id": new_id,
                "name": new_name,
                "created_at": str(datetime.now())
            }])])

            save_parquet(script_df, SCRIPT_FILE)
            st.success("Created")

    st.divider()

    if not script_df.empty:

        selected = st.selectbox("Select project", script_df["name"])
        project_id = script_df[script_df["name"] == selected]["id"].iloc[0]

        steps = get_setting("script_steps", 4)

        render_header(
            selected,
            "Script → Remotion Pipeline",
            steps
        )

        for i in range(1, steps + 1):
            step_card(project_id, i, "script")