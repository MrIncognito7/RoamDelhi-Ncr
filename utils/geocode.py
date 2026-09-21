from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="RoamDelhiNCR/0.1", timeout=10)
geocode_limited = RateLimiter(geolocator.geocode, min_delay_seconds=1)

CITIES = ["delhi", "noida", "gurgaon", "gurugram", "ghaziabad", "faridabad"]

def geocode(query):
    q = query if any(c in query.lower() for c in CITIES) else f"{query}, Delhi"
    loc = geocode_limited(q, country_codes="in")
    if loc is None:
        return None
    return loc.latitude, loc.longitude
