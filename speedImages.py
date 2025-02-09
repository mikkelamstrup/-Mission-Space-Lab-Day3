from exif import Image
from datetime import datetime, timedelta
from picamzero import Camera
import cv2
import math
import time

# Initialize camera
cam = Camera()

# Function to capture images at regular intervals
def capture_image(image_name):
    cam.take_photo(image_name)

# Function to extract timestamp from image metadata
def get_time(image_path):
    with open(image_path, 'rb') as image_file:
        img = Image(image_file)
        time_str = img.get("datetime_original")
        return datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')

# Function to calculate time difference between two images
def get_time_difference(image1, image2):
    time1 = get_time(image1)
    time2 = get_time(image2)
    return (time2 - time1).total_seconds()

# Convert images to OpenCV format
def convert_to_cv(image1, image2):
    img1_cv = cv2.imread(image1, 0)  # Load as grayscale
    img2_cv = cv2.imread(image2, 0)
    return img1_cv, img2_cv

# Detect features using ORB algorithm
def calculate_features(image1_cv, image2_cv, feature_number=1000):
    orb = cv2.ORB_create(nfeatures=feature_number)
    keypoints1, descriptors1 = orb.detectAndCompute(image1_cv, None)
    keypoints2, descriptors2 = orb.detectAndCompute(image2_cv, None)
    return keypoints1, keypoints2, descriptors1, descriptors2

# Match features between two images using Brute Force Matcher
def calculate_matches(descriptors1, descriptors2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    return sorted(matches, key=lambda x: x.distance)

# Extract matching coordinates from keypoints
def find_matching_coordinates(keypoints1, keypoints2, matches):
    coordinates1, coordinates2 = [], []
    for match in matches:
        pt1 = keypoints1[match.queryIdx].pt  # Coordinates in Image 1
        pt2 = keypoints2[match.trainIdx].pt  # Coordinates in Image 2
        coordinates1.append(pt1)
        coordinates2.append(pt2)
    return coordinates1, coordinates2

# Calculate mean pixel displacement between matching points
def calculate_mean_distance(coords1, coords2):
    total_distance = 0
    for (x1, y1), (x2, y2) in zip(coords1, coords2):
        total_distance += math.hypot(x2 - x1, y2 - y1)
    return total_distance / len(coords1)

# Convert pixel displacement to km and calculate speed
def calculate_speed_in_kmps(feature_distance, gsd, time_difference):
    distance_km = (feature_distance * gsd) / 100000  # Convert to kilometers
    return distance_km / time_difference  # Speed in km/s

# Main execution loop
if __name__ == "__main__":
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=10)

    previous_image = None
    all_speeds = []

    print("Starting ISS speed measurement...")

    while datetime.now() < end_time:
        image_name = f"photo_{datetime.now().strftime('%H%M%S')}.jpg"
        capture_image(image_name)
        time.sleep(30)  # Wait 30 seconds between images

        if previous_image:
            time_difference = get_time_difference(previous_image, image_name)
            img1_cv, img2_cv = convert_to_cv(previous_image, image_name)
            keypoints1, keypoints2, descriptors1, descriptors2 = calculate_features(img1_cv, img2_cv)
            matches = calculate_matches(descriptors1, descriptors2)
            coords1, coords2 = find_matching_coordinates(keypoints1, keypoints2, matches)
            mean_distance = calculate_mean_distance(coords1, coords2)
            
            GSD = 12648  # Ground Sampling Distance for ISS camera
            speed = calculate_speed_in_kmps(mean_distance, GSD, time_difference)
            all_speeds.append(speed)

            print(f"Calculated speed: {speed:.4f} km/s")

        previous_image = image_name  # Update for next loop

    # Compute final average speed
    final_speed = sum(all_speeds) / len(all_speeds) if all_speeds else 0

    # Save result in result.txt
    with open("result.txt", "w") as file:
        file.write(f"{final_speed:.5g}")

    print("Measurement completed. Final speed saved.")