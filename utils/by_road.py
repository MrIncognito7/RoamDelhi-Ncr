import requests

HEADERS = {"User-Agent": "RoamDelhiNCR/0.1"}

def road_distances(origin, places, chunk=90):
    for i in range(0, len(places), chunk):
        batch = places[i:i + chunk]
        coords = [f"{origin[1]},{origin[0]}"] + [f"{p['lng']},{p['lat']}" for p in batch]
        url = "https://router.project-osrm.org/table/v1/driving/" + ";".join(coords)
        try:
            r = requests.get(url,
                             params={"sources": 0, "annotations": "distance,duration"},
                             headers=HEADERS, timeout=30)
            data = r.json()
        except Exception as e:
            print("OSRM failed:", e)
            continue
        if data.get("code") != "Ok":
            print("OSRM error:", data)
            continue
        for p, d, t in zip(batch, data["distances"][0][1:], data["durations"][0][1:]):
            p["road_km"] = round(d / 1000, 2) if d is not None else None
            p["road_min"] = round(t / 60) if t is not None else None
    return places

