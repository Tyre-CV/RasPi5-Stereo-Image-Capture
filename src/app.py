"""
Entry point for the Streamlit application.

This module initializes and runs the Streamlit app, setting up the user interface and handling user interactions.
"""

import sys
# Ensures local modules are accessible
sys.path.append("./src")

import streamlit as st
import light
import cam
import numberplate
import time

# Initialise controller
light = light.LightController()
cam = cam.StereoCamera()
numberplate = numberplate.Numberplate()

# Side config
st.set_page_config(page_title="Stereo Image Capture", page_icon="📷", layout="wide")


# Cam Preview
st.title("Stereo Image Capture")
run = st.checkbox("📷 Start Camera Preview")

if run:
    left_frame, right_frame = cam.get_frames()
    print("Left frame shape:", left_frame.shape)
    print("Right frame shape:", right_frame.shape)
    col1, col2 = st.columns(2)
    with col1:
        frame_window_left = st.image([])
        frame_window_left.image(left_frame, caption="Left Camera", channels="RGB")
    with col2:
        frame_window_right = st.image([])
        frame_window_right.image(right_frame, caption="Right Camera", channels="RGB")
else:
    cam.close()


# Label input (in mm)
label = st.text_input("📐 Profile Depth", placeholder="in mm")
# Numberplate input
numberplate_input = st.text_input("🚗 Numberplate", placeholder="Format: S-AB-1234").upper()
if numberplate_input:
    if not numberplate.validate(numberplate_input):
        st.warning("❌ Numberplate format is invalid")
    else:
        if numberplate.is_duplicate(numberplate_input):
            st.warning("⚠️ This numberplate was already inserted before.")
        else:
            numberplate.add(numberplate_input)
            st.success("✅ Numberplate added successfully!")
# Light config (slider & toggle)
col1_light, col2_light = st.columns([3, 1])

brightness = col1_light.slider("☀️ Brightness", min_value=1, max_value=100, value=100)
light.set_brightness(brightness / 100.0)
 
light_on = col2_light.toggle("💡 Light", value=False)
light.turn(light_on)


# Button to take pic
st.button("📷 Take Photo")
# Cam-Config
