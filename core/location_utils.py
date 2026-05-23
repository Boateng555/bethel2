"""Detect user location and pick the nearest Bethel church."""
import math
import unicodedata

import requests
from django.conf import settings

from .models import Church, GlobalSettings


CITY_SLUG_ALTERNATIVES = {
    'dusseldorf': ('Düsseldorf', 'Duesseldorf', 'Dusseldorf'),
    'duesseldorf': ('Düsseldorf', 'Duesseldorf', 'Dusseldorf'),
    'frankfurt': ('Frankfurt', 'Frankfurt am Main'),
    'frankfurt-am-main': ('Frankfurt', 'Frankfurt am Main'),
    'hamburg': ('Hamburg',),
    'cologne': ('Köln', 'Cologne', 'Koeln'),
    'koln': ('Köln', 'Cologne', 'Koeln'),
    'koeln': ('Köln', 'Cologne', 'Koeln'),
}

COUNTRY_ALIASES = {
    'germany': ('germany', 'deutschland', 'de', 'bundesrepublik deutschland'),
    'deutschland': ('germany', 'deutschland', 'de'),
    'ghana': ('ghana', 'gh'),
    'united kingdom': ('united kingdom', 'uk', 'england', 'great britain', 'gb'),
    'uk': ('united kingdom', 'uk', 'england', 'great britain', 'gb'),
    'united states': ('united states', 'usa', 'us', 'united states of america'),
    'usa': ('united states', 'usa', 'us'),
    'netherlands': ('netherlands', 'holland', 'nl', 'the netherlands'),
}


def normalize_city(name: str) -> str:
    if not name:
        return ''
    text = unicodedata.normalize('NFKD', str(name).lower().strip())
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text.replace('ß', 'ss').replace('-', ' ')


def normalize_country(name: str) -> str:
    if not name:
        return ''
    text = unicodedata.normalize('NFKD', str(name).lower().strip())
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text.replace('-', ' ')


def cities_match(user_city: str, church_city: str) -> bool:
    if not user_city or not church_city:
        return False
    a = normalize_city(user_city)
    b = normalize_city(church_city)
    return a == b or a in b or b in a or a.split()[0] == b.split()[0]


def countries_match(user_country: str, church_country: str) -> bool:
    if not user_country or not church_country:
        return False
    a = normalize_country(user_country)
    b = normalize_country(church_country)
    if a == b or a in b or b in a:
        return True
    for aliases in COUNTRY_ALIASES.values():
        if a in aliases and b in aliases:
            return True
    return False


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _redirect_settings():
    try:
        gs = GlobalSettings.get_settings()
        return {
            'min_score': getattr(gs, 'local_church_redirect_min_score', 100),
            'max_distance_km': getattr(gs, 'local_church_redirect_max_distance_km', None) or 400,
            'metro_radius_km': getattr(gs, 'local_church_metro_radius_km', None) or 100,
        }
    except Exception:
        return {
            'min_score': getattr(settings, 'LOCAL_CHURCH_REDIRECT_MIN_SCORE', 100),
            'max_distance_km': getattr(settings, 'LOCAL_CHURCH_REDIRECT_MAX_DISTANCE_KM', 400),
            'metro_radius_km': getattr(settings, 'LOCAL_CHURCH_METRO_RADIUS_KM', 100),
        }


def get_client_ip(request) -> str:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_user_location(request):
    """
    Returns (country, city, latitude, longitude).
    Prefers saved session GPS, then IP geolocation.
    """
    session_lat = request.session.get('user_lat')
    session_lon = request.session.get('user_lon')
    if session_lat is not None and session_lon is not None:
        return (
            request.session.get('user_country'),
            request.session.get('user_city'),
            float(session_lat),
            float(session_lon),
        )

    ip = get_client_ip(request)
    country = city = None
    lat = lon = None

    try:
        response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            country = data.get('country_name')
            city = data.get('city')
            lat = data.get('latitude')
            lon = data.get('longitude')
    except Exception:
        pass

    if not country:
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    country = data.get('country')
                    city = data.get('city')
                    lat = data.get('lat')
                    lon = data.get('lon')
        except Exception:
            pass

    if ip in ('127.0.0.1', 'localhost', '::1'):
        return 'Germany', 'Düsseldorf', 51.2277, 6.7735

    if lat is not None and lon is not None:
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            lat = lon = None

    return country, city, lat, lon


def churches_in_country(churches, country):
    if not country:
        return []
    return [c for c in churches if c.country and countries_match(country, c.country)]


def find_closest_by_coordinates(churches, user_lat, user_lon, max_distance_km=None):
    if user_lat is None or user_lon is None:
        return None, None
    cfg = _redirect_settings()
    max_km = max_distance_km if max_distance_km is not None else cfg['max_distance_km']
    best = None
    best_dist = float('inf')
    for church in churches:
        if church.latitude is None or church.longitude is None:
            continue
        dist = haversine_km(user_lat, user_lon, church.latitude, church.longitude)
        if dist < best_dist:
            best_dist = dist
            best = church
    if best is not None and best_dist <= max_km:
        return best, best_dist
    return None, None


def find_nearest_church(country, city, user_lat=None, user_lon=None, request=None):
    """
    Pick the church for the visitor's current city or country.
    Priority: city name → nearby GPS → only church in country → saved preference.
    """
    churches = list(Church.objects.filter(is_active=True, is_approved=True))
    if not churches:
        return None
    if len(churches) == 1:
        return churches[0]

    cfg = _redirect_settings()
    metro_km = cfg['metro_radius_km']
    max_km = cfg['max_distance_km']

    lat, lon = user_lat, user_lon
    if request:
        if lat is None:
            lat = request.session.get('user_lat')
        if lon is None:
            lon = request.session.get('user_lon')

    # 1) Same city (anywhere in the city → that church)
    if city:
        for church in churches:
            if church.city and cities_match(city, church.city):
                if not country or not church.country or countries_match(country, church.country):
                    return church

    in_country = churches_in_country(churches, country) if country else []

    # 2) Nearest church by coordinates (within city/metro or country)
    if lat is not None and lon is not None:
        pool = in_country if in_country else churches
        closest, dist = find_closest_by_coordinates(pool, lat, lon, max_distance_km=max_km)
        if closest:
            if len(in_country) <= 1 or dist <= metro_km:
                return closest
            if city and closest.city and cities_match(city, closest.city):
                return closest

    # 3) Only one Bethel in this country → everyone in the land goes there
    if in_country and len(in_country) == 1:
        return in_country[0]

    # 4) Country + coordinates: nearest in country even if farther (e.g. rural Germany)
    if in_country and lat is not None and lon is not None:
        closest, _dist = find_closest_by_coordinates(in_country, lat, lon, max_distance_km=max_km)
        if closest:
            return closest

    # 5) Country name only (no coords) — match if score threshold met
    if country and in_country:
        if city:
            for church in in_country:
                if church.city and cities_match(city, church.city):
                    return church
        if len(in_country) == 1:
            return in_country[0]

    # 6) Previously saved church (returning visitor)
    if request and request.session.get('user_church_id'):
        try:
            return Church.objects.get(
                pk=request.session['user_church_id'],
                is_active=True,
                is_approved=True,
            )
        except Church.DoesNotExist:
            pass

    return None


def churches_for_location_json():
    """Churches with coordinates for browser-side nearest detection."""
    result = []
    for church in Church.objects.filter(is_active=True, is_approved=True):
        if church.latitude is None or church.longitude is None:
            continue
        result.append({
            'id': str(church.id),
            'city': church.city or '',
            'lat': float(church.latitude),
            'lon': float(church.longitude),
        })
    return result


def church_location_redirect(church):
    from django.urls import reverse

    country_slug = (church.country or '').lower().replace(' ', '-').strip('-')
    city_slug = (church.city or '').lower().replace(' ', '-').strip('-')
    if country_slug and city_slug:
        return reverse('church_detail_by_location', args=[country_slug, city_slug])
    return reverse('church_home', args=[church.id])


def save_user_location_session(request, church, lat=None, lon=None, gps_confirmed=False):
    request.session['user_church_id'] = str(church.id)
    request.session['user_city'] = church.city
    request.session['user_country'] = church.country
    if lat is not None and lon is not None:
        request.session['user_lat'] = float(lat)
        request.session['user_lon'] = float(lon)
    if gps_confirmed:
        request.session['user_gps_confirmed'] = True
    request.session.modified = True


def city_names_for_slug(city_slug: str):
    city_name = city_slug.replace('-', ' ').title()
    names = [city_name]
    key = city_slug.lower()
    if key in CITY_SLUG_ALTERNATIVES:
        names = list(CITY_SLUG_ALTERNATIVES[key])
    return names
