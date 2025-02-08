from picamzero import Camera

cam = Camera()

cam.capture_sequence("sequence", numImages = 3, interval = 3)