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
import uuid
import time

# Initialise controller
light = light.LightController()
cam = cam.StereoCamera()
numberplate = numberplate.Numberplate()

# -----------------------------------------------------------
# Side config
st.set_page_config(page_title="Stereo Image Capture", page_icon="📷", layout="wide")


# -----------------------------------------------------------
# Image preview
st.title("Stereo Image Capture")
col1, col2 = st.columns(2)
with col1:
    frame_window_left = st.image([])
with col2:
    frame_window_right = st.image([])

# Cam Preview
if st.button("📷 Capture Camera Preview"):
    left_frame, right_frame = cam.get_frames()
    frame_window_left.image(left_frame, channels="RGB")
    frame_window_right.image(right_frame, channels="RGB")




# -----------------------------------------------------------
# Label input (in mm)
tyre_label = st.text_input("📐 Profile Depth", placeholder="in mm", key="label-input")

# -----------------------------------------------------------
# Numberplate input
numberplate_input = st.text_input("🚗 Numberplate", placeholder="Format: S-AB-1234", key="numberplate-input").upper()
if numberplate_input:
    if not numberplate.validate(numberplate_input):
        st.warning("❌ Numberplate format is invalid")
    else:
        if numberplate.is_full(numberplate_input):
            st.warning("⚠️ This numberplate was already inserted 4 times before.")
        else:
            numberplate.add(numberplate_input)
            st.success("✅ Numberplate added successfully!")
            
# -----------------------------------------------------------
# Light control
# Light config (slider & toggle)
col1_light, col2_light = st.columns([3, 1])

brightness = col1_light.slider( "☀️ Brightness", min_value=1, max_value=100, value=100, key="light-brightness")
light.set_brightness(brightness / 100.0)

light_on = col2_light.toggle("💡 Light", value=False, key="light-switch")
light.turn(light_on)

# -----------------------------------------------------------
# Button to take pic
take_photo_disabled = not tyre_label.strip()
if st.button("📷 Take Photo", disabled=take_photo_disabled):
    try:
        unqiue_id = str(uuid.uuid4())

        left_filename = f"{unqiue_id}_{tyre_label}_L.jpg"
        right_filename = f"{unqiue_id}_{tyre_label}_R.jpg"
        cam.capture_images(left_path=left_filename, right_path=right_filename)
        st.success(f"Photots saved:{left_filename} & {right_filename}")
    except Exception as e:
        st.error(f"Error capturing images: {e}")

# -----------------------------------------------------------
# Clean-Up
if cam:
    cam.close()


