# RoamDelhi-NCR API

A FastAPI backend that finds cafes, restaurants, tourist spots, leisure
spots, and shopping spots near any location in Delhi NCR, with real
road distance and travel time (via OSRM), sourced live from
OpenStreetMap/Overpass.

> ignore `t.py` — scratch/testing file, not part of the API

---

## 1. Setup

```bash
# from the project root
python3 -m pip install fastapi uvicorn requests --break-system-packages
```

Make sure every folder that's imported from has an `__init__.py`
(`amenity/`, `tourism/`, `leisure/`, `malls_shop/`, `utils/`,
`routers/`) — without it, imports will fail with
`ModuleNotFoundError`.

## 2. Running the server

```bash
cd ~/Documents/RoamDelhiNcr   # project root — wherever main.py lives
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload` restarts the server automatically when you save a file
- `--host 0.0.0.0` makes it reachable from an emulator or a phone on
  the same network, not just `localhost`
- Stop the server with `Ctrl+C`

**Interactive docs** (test every endpoint from the browser, no extra
tools needed):

```
http://127.0.0.1:8000/docs
```

---

## 3. Endpoints

All endpoints are `GET` requests and return JSON. None require login
yet — that's being added later.

### `GET /`

Health check.

```
GET /
```

```json
{ "status": "ok" }
```

---

### `GET /spots/cafes`

Cafes and restaurants near a point.

| Param | Type | Required | Default | Notes |
|---|---|---|---|---|
| `lat` | float | yes | — | Latitude of the origin |
| `lng` | float | yes | — | Longitude of the origin |
| `radius_m` | int | no | `2500` | Search radius in meters |

```
GET /spots/cafes?lat=28.6129&lng=77.2295
GET /spots/cafes?lat=28.6129&lng=77.2295&radius_m=1500
```

---

### `GET /spots/tourism`

Museums, attractions, galleries, viewpoints, etc.

| Param | Type | Required | Default |
|---|---|---|---|
| `lat` | float | yes | — |
| `lng` | float | yes | — |
| `radius_m` | int | no | `3000` |

```
GET /spots/tourism?lat=28.6129&lng=77.2295
```

---

### `GET /spots/leisure`

Parks, gardens, sports centres, and similar leisure spots.

| Param | Type | Required | Default |
|---|---|---|---|
| `lat` | float | yes | — |
| `lng` | float | yes | — |
| `radius_m` | int | no | `3000` |

```
GET /spots/leisure?lat=28.6129&lng=77.2295
```

---

### `GET /spots/shopping`

Malls, department stores, and shops.

| Param | Type | Required | Default |
|---|---|---|---|
| `lat` | float | yes | — |
| `lng` | float | yes | — |
| `radius_m` | int | no | `3000` |

```
GET /spots/shopping?lat=28.6129&lng=77.2295
```

---

### `GET /spots/nearby`

All four categories combined (cafes, tourism, leisure, shopping),
merged into one list and sorted by road distance. Slowest endpoint,
since it calls all four finders in sequence.

| Param | Type | Required | Default |
|---|---|---|---|
| `lat` | float | yes | — |
| `lng` | float | yes | — |
| `radius_m` | int | no | `3000` |

```
GET /spots/nearby?lat=28.6129&lng=77.2295
```

---

## 4. Response shape

Every `/spots/*` endpoint returns a JSON array of place objects:

```json
[
  {
    "name": "Triveni Terrace Cafe",
    "lat": 28.6247,
    "lng": 77.2311,
    "type": "cafe",
    "road_km": 0.62,
    "road_min": 3
  },
  {
    "name": "Sorento",
    "lat": 28.6198,
    "lng": 77.2287,
    "type": "restaurant",
    "road_km": 0.85,
    "road_min": 4
  }
]
```

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Place name |
| `lat` / `lng` | float | Coordinates |
| `type` | string | Category tag (`cafe`, `restaurant`, `museum`, `park`, `mall`, etc.) |
| `road_km` | float | Real road distance from the origin, via OSRM |
| `road_min` | int | Free-flow drive time in minutes (no live traffic) |

Results are always sorted by `road_km` ascending (nearest first), and
only include places within the requested `radius_m`.

---

## 5. Example: calling it from Flutter

```dart
final uri = Uri.parse('http://10.0.2.2:8000/spots/nearby')
    .replace(queryParameters: {'lat': '28.6129', 'lng': '77.2295'});
final res = await http.get(uri);
final places = jsonDecode(res.body) as List;
```

- Android **emulator**: use `10.0.2.2` to reach your computer's
  `localhost`
- Real **phone**: use your computer's Wi-Fi IP instead (e.g.
  `http://192.168.1.5:8000`), both devices on the same network

---

## 6. Known limitations (current state)

- No authentication yet — every endpoint is public
- No rate limiting — avoid hammering `/spots/nearby` repeatedly
  while testing, since each call makes several live Overpass/OSRM
  requests
- No caching — the same coordinates re-run the full search every
  time
- Travel time is free-flow only (no live traffic)
- Data comes entirely from OpenStreetMap, so coverage for small/local
  spots (e.g. street food stalls) can be incomplete

## 7. Planned next

- Curated spots file (verified local data) checked before falling
  back to live search (hybrid mode)
- Login (`/register`, `/login`) and premium-gated spots
- Caching to speed up repeat requests