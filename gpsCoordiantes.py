from astro_pi_orbit import ISS
from picamzero import Camera

iss = ISS()

def get_gps_coordinates(iss):
    point = iss.coordinates()
    return (point.latitude.signed_dms(), point.longitude.signed_dms())  

cam = Camera()

cam.take_photo("gps_image1.jpg", gps_coordinates=get_gps_coordinates(iss))  