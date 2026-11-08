import json
import re
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse


ADDRESS = re.compile(r"^(?P<street>.+), (?P<city>[^,]+), (?P<state>[A-Z]{2}) (?P<zip>\d{5}(?:-\d{4})?)$")
HOURS = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\s*[–-]\s*(?:(\d{1,2})(?::(\d{2}))?\s*(AM|PM)|(midnight))\s*$", re.I)


def public_url(request, path):
    base = settings.PUBLIC_SITE_URL or request.build_absolute_uri("/")
    return urljoin(base.rstrip("/") + "/", path.lstrip("/"))


def home_seo(request, content):
    title = content.seo_title or "Spirits2U | Beer, Wine & Spirits Stores in Florida"
    description = content.seo_description or (
        "Find a Spirits2U near you in Florida. See local store hours, phone numbers, "
        "directions, and DoorDash ordering at participating locations."
    )
    return {"seo_title": title, "seo_description": description, "canonical_url": public_url(request, reverse("home"))}


def store_seo(request, store):
    title = store.seo_title or f"{store.public_name} (Store {store.number}) | Spirits2U"
    location = store.homepage_address or store.homepage_city or "Florida"
    options = ["check store hours", "get directions"]
    if store.homepage_phone:
        options.append("call the store")
    if store.homepage_delivery_url:
        options.append("order on DoorDash")
    option_text = " and ".join(options) if len(options) == 2 else f"{', '.join(options[:-1])}, and {options[-1]}"
    description = store.seo_description or f"Find Spirits2U {store.public_name} at {location}. See how to {option_text}."
    url = public_url(request, reverse("public-store-detail", args=[store.public_slug]))
    return {
        "seo_title": title,
        "seo_description": description,
        "canonical_url": url,
        "store_schema_json": store_schema_json(store, url),
    }


def store_schema_json(store, url):
    schema = {"@context": "https://schema.org", "@type": "Store", "name": store.public_name, "url": url}
    address_match = ADDRESS.fullmatch(store.homepage_address)
    if address_match:
        address = address_match.groupdict()
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": address["street"],
            "addressLocality": address["city"],
            "addressRegion": address["state"],
            "postalCode": address["zip"],
            "addressCountry": "US",
        }
    elif store.homepage_address:
        schema["address"] = store.homepage_address
    if store.homepage_phone:
        schema["telephone"] = store.homepage_phone
    if store.latitude is not None and store.longitude is not None:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": float(store.latitude),
            "longitude": float(store.longitude),
        }
    specifications = []
    for day, hours in store.daily_hours:
        match = HOURS.fullmatch(hours)
        if match:
            open_hour, open_minute, open_meridiem, close_hour, close_minute, close_meridiem, midnight = match.groups()
            specifications.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": day,
                "opens": _clock(open_hour, open_minute, open_meridiem),
                "closes": "00:00" if midnight else _clock(close_hour, close_minute, close_meridiem),
            })
    if specifications:
        schema["openingHoursSpecification"] = specifications
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _clock(hour, minute, meridiem):
    hour = int(hour) % 12 + (12 if meridiem.upper() == "PM" else 0)
    return f"{hour:02}:{int(minute or 0):02}"
