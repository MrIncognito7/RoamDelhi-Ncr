mode =  ['ai_mode','manual_mode','hybrid_mode']
default_mode = mode[0]
#hybrid logic later

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import spots

app = FastAPI(title="RoamDelhiNCR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spots.router)


@app.get("/")
def root():
    return {"status": "ok"}
















'''
from amenity.find_cafe_restaurant import find_cafes_and_restaurants
from utils.geocode import geocode
place =  input("Enter the place name: ")

lat1, long1 = geocode(place)
if lat1 is None:
    print("Place not found. Please check the name and try again.")
else:
    nearby_places = find_cafes_and_restaurants(lat1, long1, radius_m=3000)
    for place in nearby_places:
        print(f"{place['name']} ({place['type']}): {place['road_km']} km,{place['lat']} , {place['lng']}")


'''

