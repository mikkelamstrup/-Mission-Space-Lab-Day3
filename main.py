# Importer nødvendige biblioteker
from astro_pi_orbit import ISS
from picamzero import Camera
from datetime import datetime, timedelta
from pathlib import Path
import math

# Initialiser Astro Pi hardware
cam = Camera()
iss = ISS()

# Definer lagringsmappe (relativ sti)
base_folder = Path(__file__).parent.resolve()

# Funktion til at hente GPS-koordinater
def get_gps_coordinates():
    point = iss.coordinates()
    return (point.latitude.degrees, point.longitude.degrees)

# Funktion til at beregne afstand mellem to GPS-koordinater
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Jordens radius i km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c  # Afstand i km

# Starttidspunkt
start_time = datetime.now()
end_time = start_time + timedelta(minutes=10)

# Liste til at gemme billeder og GPS-data
image_data = []

print("Programmet starter - optager billeder i 10 minutter...")

# Kør i 10 minutter
while datetime.now() < end_time:
    # Hent tid & GPS-koordinater
    timestamp = datetime.now()
    latitude, longitude = get_gps_coordinates()
    
    # Generér filnavn og gem billede
    image_name = f"{timestamp.strftime('%H%M%S')}.jpg"
    cam.take_photo(str(base_folder / image_name), gps_coordinates=(latitude, longitude))
    
    # Gem data
    image_data.append((timestamp, latitude, longitude))
    
    # Vent 30 sekunder
    if datetime.now() < end_time:
        sleep(30)

# Beregn ISS-hastighed baseret på første og sidste billede
if len(image_data) >= 2:
    t1, lat1, lon1 = image_data[0]
    t2, lat2, lon2 = image_data[-1]

    # Beregn afstand i km
    distance = haversine(lat1, lon1, lat2, lon2)
    
    # Beregn tid i sekunder
    time_elapsed = (t2 - t1).total_seconds()
    
    # Beregn hastighed i km/s
    speed_km_s = distance / time_elapsed

    # Gem resultat i `result.txt` (formateret til 5 signifikante cifre)
    result_file = base_folder / "result.txt"
    with open(result_file, "w", buffering=1) as file:
        file.write(f"{speed_km_s:.5f}")

    print(f"ISS-hastighed beregnet: {speed_km_s:.5f} km/s")
    print(f"Data gemt i {result_file}")

else:
    print("Fejl: Ikke nok billeder taget til at beregne hastighed.")

print("Programmet er færdigt. ISS-mission afsluttet.")