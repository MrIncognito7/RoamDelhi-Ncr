import folium
from folium.plugins import MarkerCluster

spots = [
    {"name": "India Gate", "lat": 28.6129, "lng": 77.2295, "type": "outdoor", "budget": "low"},
    {"name": "National Museum", "lat": 28.6112, "lng": 77.2190, "type": "indoor", "budget": "low"},
    # ...load your real dataset here (JSON or CSV)
]

center = (28.6129, 77.2295)
m = folium.Map(location=center, zoom_start=14, tiles="OpenStreetMap")

# 3 km search radius around the destination
folium.Circle(center, radius=3000, color="blue", fill=False).add_to(m)

cluster = MarkerCluster().add_to(m)
for s in spots:
    color = "green" if s["type"] == "outdoor" else "purple"
    folium.Marker(
        (s["lat"], s["lng"]),
        popup=f"<b>{s['name']}</b><br>{s['type']} · {s['budget']} budget",
        tooltip=s["name"],
        icon=folium.Icon(color=color),
    ).add_to(cluster)

m.save("map.html")   # double-click map.html to open it