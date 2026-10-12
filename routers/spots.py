from fastapi import APIRouter
from amenity import find_cafe_restaurant
from amenity.find_cafe_restaurant import find_cafes_and_restaurants
from tourism import find_tourism
from tourism.find_tourism import find_tourism_nearby
from leisure.find_leisure import find_leisure
from malls_shop.find_shopping import find_mall_shopping

router = APIRouter(prefix="/spots", tags=["spots"])


@router.get("/cafes")
def cafes_endpoint(lat: float, lng: float, radius_m: int = 2500):
    return find_cafes_and_restaurants(lat, lng, radius_m)


@router.get("/tourism")
def tourism_endpoint(lat: float, lng: float, radius_m: int = 3000):
    return find_tourism_nearby(lat, lng, radius_m)


@router.get("/leisure")
def leisure_endpoint(lat: float, lng: float, radius_m: int = 3000):
    return find_leisure(lat, lng, radius_m)


@router.get("/shopping")
def shopping_endpoint(lat: float, lng: float, radius_m: int = 3000):
    return find_mall_shopping(lat, lng, radius_m)


@router.get("/nearby")
def nearby_endpoint(lat: float, lng: float, radius_m: int = 3000):
    """All four categories combined, sorted by road distance."""
    all_places = (
        find_cafes_and_restaurants(lat, lng, radius_m)
        + find_tourism_nearby(lat, lng, radius_m)
        + find_leisure(lat, lng, radius_m)
        + find_mall_shopping(lat, lng, radius_m)
    )
    return sorted(all_places, key=lambda p: p.get("road_km", 999))