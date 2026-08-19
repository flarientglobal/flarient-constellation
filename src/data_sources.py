"""Fetch upstream space weather data directly from NOAA SWPC and NASA NeoWS.
Zero-cost: all endpoints are free and public. No Base44 credits consumed.
"""
import json, os, sys, urllib.request, urllib.error, datetime

TIMEOUT = 15

def _fetch_json(url):
    """Fetch JSON from a URL with timeout and error handling."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Flarient-Constellation/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[DATA] Failed to fetch {url}: {e}", file=sys.stderr)
        return None

def fetch_kp():
    """Current planetary K-index from NOAA SWPC."""
    data = _fetch_json("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json")
    if not data or not isinstance(data, list) or not data:
        return None
    latest = data[-1]
    return {"kp": latest.get("kp_index", latest.get("kp", 0)), "time_tag": latest.get("time_tag")}

def fetch_solar_wind():
    """Solar wind speed, density, and Bz from NOAA SWPC."""
    mag = _fetch_json("https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json")
    plasma = _fetch_json("https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json")
    bz = speed = density = None
    if mag and isinstance(mag, list) and len(mag) > 1:
        headers, row = mag[0], mag[-1]
        for i, h in enumerate(headers):
            if h == "bz_gsm" and i < len(row):
                try: bz = float(row[i])
                except: pass
    if plasma and isinstance(plasma, list) and len(plasma) > 1:
        headers, row = plasma[0], plasma[-1]
        for i, h in enumerate(headers):
            if h == "speed" and i < len(row):
                try: speed = float(row[i])
                except: pass
            if h == "density" and i < len(row):
                try: density = float(row[i])
                except: pass
    return {"bz": bz, "speed": speed, "density": density}

def fetch_flares():
    """Latest X-ray flare class from NOAA SWPC GOES."""
    data = _fetch_json("https://services.swpc.noaa.gov/json/goes/primary/xray-flares-6-hour.json")
    if not data or not isinstance(data, list) or not data:
        return None
    latest = data[-1]
    return {"class": latest.get("class", "unknown"), "time_tag": latest.get("time_tag")}

def fetch_neo():
    """Near-Earth objects from NASA NeoWS (DEMO_KEY is free, 30 req/hour)."""
    today = datetime.date.today().isoformat()
    url = f"https://api.nasa.gov/neo/rest/v1/feed?api_key=DEMO_KEY&start_date={today}&end_date={today}"
    data = _fetch_json(url)
    if not data:
        return {"count": 0, "objects": []}
    neos = []
    for date_key, objects in (data.get("near_earth_objects") or {}).items():
        for obj in objects:
            cad = (obj.get("close_approach_data") or [{}])[0]
            neos.append({
                "id": obj.get("id"),
                "name": obj.get("name"),
                "diameter_m": round((obj.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_max", 0)), 1),
                "is_hazardous": obj.get("is_potentially_hazardous_asteroid", False),
                "miss_distance_km": round(float(cad.get("miss_distance", {}).get("kilometers", 0))),
                "velocity_km_s": round(float(cad.get("relative_velocity", {}).get("kilometers_per_second", 0)), 1),
            })
    return {"count": data.get("element_count", len(neos)), "objects": neos}

def fetch_all():
    """Aggregate all upstream data into a normalized snapshot."""
    print("[DATA] Fetching upstream space weather data...")
    kp = fetch_kp() or {}
    wind = fetch_solar_wind() or {}
    flare = fetch_flares() or {}
    neo = fetch_neo() or {}
    snapshot = {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kp": kp.get("kp", 0),
        "kp_time": kp.get("time_tag"),
        "bz": wind.get("bz"),
        "solar_wind_speed": wind.get("speed"),
        "solar_wind_density": wind.get("density"),
        "flare_class": flare.get("class", "unknown"),
        "flare_time": flare.get("time_tag"),
        "neo_count": neo.get("count", 0),
        "neo_objects": neo.get("objects", []),
    }
    print(f"[DATA] Kp={snapshot['kp']}, Bz={snapshot['bz']}, Wind={snapshot['solar_wind_speed']}, Flare={snapshot['flare_class']}, NEOs={snapshot['neo_count']}")
    return snapshot