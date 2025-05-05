#!/usr/bin/env python3
# main.py  ── Streamlit wrapper around text_to_speech() + conversion()
###############################################################################
import os, sys, pathlib, tempfile
import streamlit as st
from pathlib import Path
import runpy
import subprocess

###############################################################################
# 1)  Ensure we’re running inside the correct venv
#VENV_PYTHON = "/home/nicole/code/nicole-baltodano/hackaton/audio-env/bin/python"
#if sys.executable != VENV_PYTHON:            # re‑exec under audio‑env
#    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

###############################################################################
# 2)  Make helper modules importable
ROOT_DIR = pathlib.Path(__file__).resolve().parent
RVC_DIR  = ROOT_DIR / "Retrieval-based-Voice-Conversion-WebUI"

sys.path.insert(0, str(RVC_DIR))             # RVC repo
sys.path.insert(0, str(ROOT_DIR))            # convert_method / audio_generation

from convert_method   import conversion
from audio_generation import text_to_speech   # ← your existing helper
import runpy
###############################################################################
# 3)  Streamlit UI
st.set_page_config(page_title="RVC Demo", page_icon="🎤", layout="centered")
st.title("👋 Hey, I'm Virtual David!")


col1, col2 = st.columns(2)
with col1:
    text = st.text_area("Type text (optional)", height=150)
with col2:
    uploaded = st.file_uploader("…or upload a WAV file", type=["wav"])

with st.expander("Advanced RVC settings ⚙️", expanded=False):
    index_rate    = st.slider("Index blend (index_rate)",     0.00, 1.00, 0.30, 0.01)
    filter_radius = st.slider("Denoiser blur (filter_radius)", 0,    7,    1)
    resample_sr   = st.selectbox(
        "Output sample‑rate (resample_sr)",
        options=[0, 32000, 44100, 48000],
        index=0,  # 0 means “keep model SR”
        format_func=lambda v: "Keep model SR" if v == 0 else f"{v//1000} kHz"
    )
    rms_mix_rate  = st.slider("RMS mix (rms_mix_rate)",       0.00, 1.00, 0.15, 0.01)
    protect       = st.slider("Formant protect (protect)",    0.00, 1.00, 0.40, 0.01)


if st.button("🗣️ Be David"):
    if not uploaded and not text.strip():
        st.error("Please type some text **or** upload a WAV file 🙂")
        st.stop()

    # keep everything in a temp dir
    #tmp_dir  = tempfile.TemporaryDirectory()
    tts_path = Path("output.wav")

    # 1️⃣  Source preparation --------------------------------------------------
    if uploaded:                                   # user supplied audio
        tts_path.write_bytes(uploaded.read())      # save upload ➜ tts.wav
    else:                                          # generate from text
        with st.spinner("Converting text to speech…"):
            text_to_speech(text)


    #voice conversion
    with st.spinner("Converting to David's voice "):

        rvc_path = conversion(index_rate, filter_radius, resample_sr, rms_mix_rate, protect)

    # Playback & download
    audio_bytes = rvc_path.read_bytes()
    st.success("Done!  Listen below ⬇️")
    st.audio(audio_bytes, format="audio/wav")
    st.download_button(
        "⬇️ Download WAV",
        data=audio_bytes,
        file_name="converted.wav",
        mime="audio/wav"
    )

    #go back to root dir
    os.chdir(ROOT_DIR)

# ── Define your root and Wav2Lip directories ────────────────────────────────                              # .../hackaton
WAV2LIP_APP = os.path.join(ROOT_DIR, "video_training", "Wav2Lip")
VIDEO_PY    = os.path.join(WAV2LIP_APP, "video.py")
SYNCED_OUT  = os.path.join(ROOT_DIR, "synced.mp4")

st.title("🎥 Roll Camera: David’s Video")

if st.button("Run video.py"):
    with st.spinner("Spawning video.py…"):
        # Launch in a fresh process:
        proc = subprocess.Popen(
            [sys.executable, VIDEO_PY],
            cwd=WAV2LIP_APP
        )
        proc.wait()  # blocks here, but in *that* subprocess
    # once proc exits, *all* its memory is returned to the OS
    if proc.returncode != 0:
        st.error(f"video.py exited with code {proc.returncode}")
    elif not os.path.exists(SYNCED_OUT):
        st.error("Expected output not found!")
    else:
        st.success("✅ video.py finished—here’s your result:")
        st.video(SYNCED_OUT)