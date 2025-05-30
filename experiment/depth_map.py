import cv2
import numpy as np
import matplotlib.pyplot as plt

# === Load stereo images ===
left_img = cv2.imread('img/test_l.png', cv2.IMREAD_GRAYSCALE)
right_img = cv2.imread('img/test_r.png', cv2.IMREAD_GRAYSCALE)


# === Stereo Matcher (SGBM) with optimized parameters ===
window_size = 5
min_disp = 0
num_disp = 160  # Increased for better depth resolution (must be divisible by 16)

stereo = cv2.StereoSGBM_create(
    minDisparity=min_disp,
    numDisparities=num_disp,
    blockSize=7,  # Smaller block size for finer details
    P1=8 * 3 * window_size**2,
    P2=32 * 3 * window_size**2,
    disp12MaxDiff=1,
    uniquenessRatio=10,  # Lower for more matches
    speckleWindowSize=50,
    speckleRange=1,  # Tighter speckle range
    preFilterCap=63,
    mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)

# === Compute Disparity Map ===
disparity = stereo.compute(left_img, right_img).astype(np.float32) / 16.0

# === Convert to Depth Map in millimeters ===
# Camera parameters for IMX219
focal_length_mm = 2.6  # Focal length in mm
baseline_mm = 60.0     # Baseline in mm

# Calculate focal length in pixels
sensor_width_mm = 3.68  # 1/4" sensor is 3.68mm 
image_width_px = left_img.shape[1]
focal_length_px = (focal_length_mm * image_width_px) / sensor_width_mm

# Depth in mm = (focal_length_px * baseline_mm) / disparity
depth_map_mm = (focal_length_px * baseline_mm) / (disparity + 1e-6)  # Add small value to avoid division by zero

# Filter out invalid depths (too close or too far)
valid_depth_mask = (disparity > min_disp)
depth_map_mm[~valid_depth_mask] = 0

# === Visualize Results ===
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.imshow(left_img, 'gray')
plt.title("Left Image")

plt.subplot(1, 3, 2)
plt.imshow(disparity, 'gray')
plt.title("Disparity Map")
plt.colorbar()

plt.subplot(1, 3, 3)
plt.imshow(depth_map_mm, cmap='plasma', vmin=0, vmax=5)  # Scale for 0-5m range
plt.title("Depth Map (mm)")
plt.colorbar()

plt.tight_layout()
plt.show()

# === Save 16-bit depth map ===
depth_map_16bit = np.uint16(np.clip(depth_map_mm, 0, 65535))  # 0-65535 mm range
cv2.imwrite('depth_map_mm.png', depth_map_16bit)

# Optional: Apply median filter to reduce noise
filtered_depth = cv2.medianBlur(depth_map_16bit, 3)
cv2.imwrite('filtered_depth_map_mm.png', filtered_depth)


# Example: Threshold to isolate nearby objects (tires)
tire_depth_mask = (depth_map_mm > 200) & (depth_map_mm < 1500)  # Adjust for your expected tire distance
tire_depth = depth_map_mm.copy()
tire_depth[~tire_depth_mask] = 0

plt.imshow(tire_depth, cmap='plasma', vmin=0, vmax=4)
plt.title("Tire Depth (mm)")
plt.colorbar()
plt.show()