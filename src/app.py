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
import numpy as np

# Initialise controller
light = light.LightController()
cam = cam.StereoCamera()
numberplate = numberplate.Numberplate()

# -----------------------------------------------------------
# Side config
st.set_page_config(page_title="Stereo Image Capture", page_icon="📷", layout="wide")

# Deactivate statistic collection
# st.browser.gatherUsageStats = False

# -----------------------------------------------------------
# Session
# Generate an empty black image (HxW, RGB)
width, height = cam.get_cam_dims()['left']  
empty_black_image = np.zeros((height, width, 3), dtype=np.uint8)

default_session_state = {
    'light-brightness': 100,
    'light-switch': False,
    'label-input': '',
    'numberplate-input': '',
    'last-image-left': empty_black_image,  
    'last-image-right': empty_black_image,
    'cam-config': {
        # 'exposure': 10000,  
        # 'shutter_speed': 10000,  
        # 'iso': 100,  
    },
}

# Set if not present
for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Initialize camera controls in session state
for control in cam.CONTROLS.keys():
    potential_options = cam.get_camera_options()
    if f'cam-config-slider-{control}' not in st.session_state:
        st.session_state[f'cam-config-slider-{control}'] = potential_options[control]['default']
    if f'cam-config-text-{control}' not in st.session_state:
        st.session_state[f'cam-config-text-{control}'] = potential_options[control]['default']

# -----------------------------------------------------------
# Image preview
st.title("Stereo Image Capture")
col1, col2 = st.columns(2)
with col1:
    frame_window_left = st.image(st.session_state.get('last-image-left', []), channels="RGB")
with col2:
    frame_window_right = st.image(st.session_state.get('last-image-right', []), channels="RGB")

left_btn_col, middle_btn_col, right_btn_col = st.columns(3)

with left_btn_col:
    # Button Cam Preview
    if st.button("📷 Capture Camera Preview"):
        left_frame, right_frame = cam.get_preview()
        # Update State
        frame_window_left.image(left_frame, channels="RGB")
        frame_window_right.image(right_frame, channels="RGB")
        # Update session state with the captured frames
        st.session_state['last-image-left'] = left_frame
        st.session_state['last-image-right'] = right_frame

#-----------------------------------------------------------
with middle_btn_col:
    # Button to take pic
    label = st.session_state.get('label-input', '')
    current_numberplate = st.session_state.get('numberplate-input', '')
    take_photo_disabled = numberplate.full or not bool(label.strip()) or not bool(current_numberplate.strip())
    if st.button("📷 Take Photo", disabled=take_photo_disabled): 
        new_left_img, new_right_img = cam.capture_images(label=st.session_state.get("label-input", ""), numberplate = numberplate)

        # Update state
        frame_window_left.image(new_left_img, channels="RGB")
        frame_window_right.image(new_right_img, channels="RGB")
        # Update session state with new images
        st.session_state['last-image-left'] = new_left_img
        st.session_state['last-image-right'] = new_right_img

# -----------------------------------------------------------
# Delete last images
disable_delte_btn = not cam.can_delete_last_images()
with right_btn_col:
    if st.button("🗑️ Delete Last Images", disabled=disable_delte_btn ):
        cam.delete_last_images(numberplate)
        # Clear the image windows
        frame_window_left.image(empty_black_image, channels="RGB")
        frame_window_right.image(empty_black_image, channels="RGB")
        # Clear session state images
        st.session_state['last-image-left'] = empty_black_image
        st.session_state['last-image-right'] = empty_black_image

# -----------------------------------------------------------
# Label input (in mm)
tyre_label = st.text_input("📐 Profile Depth", value=st.session_state.get("label-iput",""), placeholder="in mm", key="label-input")
# -----------------------------------------------------------
# Numberplate input
numberplate_input = st.text_input("🚗 Numberplate", value=st.session_state.get("numberplate-input", ""), placeholder="Format: S-AB-1234", key="numberplate-input").upper()

# numberplate.numberplate = numberplate_input
numberplate.numberplate = st.session_state.get("numberplate-input", "").upper()

if not numberplate.validate():
    st.warning("❌ Numberplate format is invalid")

if numberplate.full:
    st.warning("❗ Numberplate is full. Please delete some entries before adding new ones.")
# -----------------------------------------------------------
# Light control
# Light config (slider & toggle)
col1_light, col2_light = st.columns([3, 1])

brightness = col1_light.slider( "☀️ Brightness", value=st.session_state.get("light-brightness", 100), min_value=1, max_value=100, key="light-brightness")
light.set_brightness(st.session_state['light-brightness'] / 100.0)

light_on = col2_light.toggle("💡 Light", value=st.session_state.get("light-switch", False), key="light-switch")
light.turn(light_on)

# -----------------------------------------------------------
# Camera controls
new_controls = {}
cam_options = cam.get_camera_options()

save_col_1, save_col_2, save_col_3, save_col_4 = st.columns([2,1, 2, 1])
with save_col_1:
    config_name = st.text_input(
        "📂 Config Name",
        
    )

with save_col_2:
    # Button for saving camera config
    if st.button("💾 Save Camera Config"):
        cam.save_cam_config(config_name)
        # st.success("Camera configuration saved successfully!")

with save_col_3:
    # Selection of available camera controls
    selected_control_file = st.selectbox(
        "📸 Select Camera Control File",
        options=cam.get_saved_configs(),
    )



with save_col_4:
    # Button for loading camera config
    if st.button("📂 Load Camera Config"):
        control_values = cam.load_config(selected_control_file)
        # Update session state with loaded config
        for control in control_values.keys():
            st.session_state[f'cam-config-slider-{control}'] = control_values[control]
            st.session_state[f'cam-config-text-{control}'] = control_values[control]

def update_cam_config_text(control):
    st.session_state[f'cam-config-text-{control}'] = st.session_state[f'cam-config-slider-{control}']

def update_cam_config_slider(control):
    st.session_state[f'cam-config-slider-{control}'] = st.session_state[f'cam-config-text-{control}']

for control in cam.CONTROLS.keys():
    # Update session (cam-config) with default values if not present
    if control not in st.session_state['cam-config']:
        st.session_state['cam-config'][control] = cam_options[control]['default']

with st.container(height=400):
    st.subheader(f"Camera Controls: {cam.current_config}")
    for control in cam_options.keys():
        # control_col_1, control_col_2 = st.columns([3, 1])

        # with control_col_1:
        control_input_slider = st.slider(
                f"🎛️ {control}",
                min_value=cam_options[control]['min'],
                max_value=cam_options[control]['max'],
                # value=cam_options[control]['default'],
                value=st.session_state[f'cam-config-slider-{control}'],
                key=f"cam-config-slider-{control}",
                on_change=update_cam_config_text,
                args=(control,)
            )
        new_controls[control] = control_input_slider

        # with control_col_2:
        #     text_input = st.text_input(
        #         f"🎛️ {control} (Value)",
        #         # value=cam_options[control]['default'],
        #         value=str(st.session_state[f'cam-config-text-{control}']),
        #         key=f"cam-config-text-{control}",
        #         on_change=update_cam_config_slider,
        #         args=(control,)
        #     )

# Update session state with new controls
st.session_state['cam-config'] = new_controls
# Apply new controls to cameras
session_controls = st.session_state.get('cam-config', {})
cam.adjust_config(session_controls)

# for control, value in st.session_state['cam-config'].items():
#     print(f"Control: {control}, Value: {value}")

    

