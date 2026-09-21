import requests
import time
radius_m = 3000  #default radius in meters
from utils.by_road import road_distances
URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]
HEADERS = {"User-Agent": "RoamDelhiNCR/0.1 (personal learning project)"}


def overpass_nearby(lat, lng, radius_m):
    query = f"""
    [out:json][timeout:25];
    (

      nwr(around:{radius_m},{lat},{lng})["amenity"~"cafe|restaurant"];
    );
    out center tags;
    """
    for url in URLS:
        for attempt in range(2):
            r = requests.post(url, data={"data": query}, headers=HEADERS, timeout=40)
            if r.status_code == 200:
                try:
                    return r.json()["elements"]
                except ValueError:
                    print("200 but not JSON:", r.text[:300])
            else:
                print(f"{url} -> {r.status_code}: {r.text[:200]}")
            time.sleep(3)  # wait before retrying
    return []

def find_cafes_and_restaurants(lat, lng, radius_m):
    t = time.time()
    elements = overpass_nearby(lat, lng, radius_m)
    print(f"Overpass: {len(elements)} elements in {time.time() - t:.1f}s")

    places = []
    for el in elements:
        tags = el.get("tags", {})
        plat = el.get("lat") or el.get("center", {}).get("lat")
        plng = el.get("lon") or el.get("center", {}).get("lon")
        if tags.get("name") and plat and plng:
            places.append({"name": tags["name"], "lat": plat, "lng": plng,
                           "type": tags.get("amenity")})

    t = time.time()
    places = road_distances((lat, lng), places)
    print(f"OSRM: {len(places)} places in {time.time() - t:.1f}s")

    places = [p for p in places
              if p.get("road_km") is not None and p["road_km"] <= radius_m / 1000]
    return sorted(places, key=lambda p: p["road_km"])






