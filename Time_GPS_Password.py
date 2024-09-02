import time
from geopy.geocoders import Nominatim

def generate_live_password():
    # Get current time
    current_time = int(time.time())

    # Get current GPS coordinates (latitude and longitude)
    geolocator = Nominatim(user_agent="live_password_generator")
    location = geolocator.geocode("Your_Location_Name_or_Coordinates")
    if location:
        latitude = location.latitude
        longitude = location.longitude
    else:
        # Use default coordinates if unable to get location
        latitude, longitude = 0.0, 0.0

    # Create a password-like string using time and coordinates
    live_password = f"{current_time}_{latitude}_{longitude}"

    return live_password

if __name__ == "__main__":
    password = generate_live_password()
    print("Generated Live Password:", password)
