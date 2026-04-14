import numpy as np
import pyrealsense2 as rs

pipeline = rs.pipeline()
config = rs.config()

# 2. Configure streams (Lower FPS is better for Pi stability)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

# config.enable_stream(rs.stream.accel)
# config.enable_stream(rs.stream.gyro)


try:
    pipeline.start(config)
except Exception as e:
    print(f"Could not start: {e}")
    exit()

try:
    while True:
        # ONLY CALL THIS ONCE PER LOOP
        frames = pipeline.wait_for_frames()

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Get IMU data from the SAME frameset
        accel_frame = frames.first_or_default(rs.stream.accel)
        gyro_frame = frames.first_or_default(rs.stream.gyro)

        if not depth_frame or not color_frame:
            continue

        # Convert images
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        if accel_frame and gyro_frame:
            accel = accel_frame.as_motion_frame().get_motion_data()
            gyro = gyro_frame.as_motion_frame().get_motion_data()
            print(
                f"Accel: {accel.x:.2f}, {accel.y:.2f}, {accel.z:.2f} | Gyro: {gyro.x:.2f}"
            )

finally:
    pipeline.stop()
