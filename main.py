mode =  ['ai_mode','manual_mode','hybrid_mode']
default_mode = mode[0]
#hybrid logic later
from amenity.find_cafe_restaurant import find_cafes_and_restaurants
from utils.geocode import geocode
place =  input("Enter the place name: ")

lat1, long1 = geocode(place)
if lat1 is None:
    print("Place not found. Please check the name and try again.")
else:
    nearby_places = find_cafes_and_restaurants(lat1, long1, radius_m=3000)
    for place in nearby_places:
        print(f"{place['name']} ({place['type']}): {place['road_km']} km, {place['road_min']} min")

