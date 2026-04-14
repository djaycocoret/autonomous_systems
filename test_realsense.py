import numpy as np
import pyrealsense2 as rs

config = rs.config()

# 2. Tell the config what you want (Stream, Width, Height, Format, FPS)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.accel)
# config.enable_stream(rs.stream.gyro)

# 1. Pipeline setup
pipeline = rs.pipeline()
pipeline.start()

# pipeline.start(config)

try:
    while True:
        # 2. Wait for a coherent set of frames
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        frames = pipeline.wait_for_frames()

        # 3. CONVERSION: This is where the magic happens
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        print(depth_image)

finally:
    pipeline.stop()
