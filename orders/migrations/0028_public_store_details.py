from django.db import migrations


def populate_verified_details(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    # Public details checked against map, store directory, and delivery listings in November 2026.
    details = {
        "110": {"homepage_address": "110 Canaveral Plaza Blvd, Cocoa Beach, FL 32931", "latitude": "28.355954", "longitude": "-80.610089"},
        "1850": {"homepage_address": "1850 N Courtenay Pkwy #101, Merritt Island, FL 32953", "latitude": "28.389651", "longitude": "-80.701813", "homepage_delivery_url": "https://www.doordash.com/en-US/convenience/store/spirits2u-merritt-island-29346394/", "homepage_hours": "Daily 8 AM – 10 PM", "daily": ["8 AM – 10 PM"] * 7},
        "3210": {"homepage_address": "3210 S Fiske Blvd #104, Rockledge, FL 32955", "latitude": "28.306653", "longitude": "-80.742047"},
        "6300": {"homepage_address": "6300 N Wickham Rd #119, Melbourne, FL 32940", "latitude": "28.213357", "longitude": "-80.673693"},
        "1317": {"homepage_name": "Melbourne", "homepage_city": "Melbourne", "homepage_address": "1317 S Babcock St, Melbourne, FL 32901", "latitude": "28.088473", "longitude": "-80.621727", "homepage_delivery_url": "https://www.doordash.com/convenience/store/spirits-2u-melbourne-29346356/", "homepage_hours": "Daily 8 AM – midnight", "daily": ["8 AM – midnight"] * 7},
        "1516": {"homepage_name": "Palm Bay Road", "homepage_city": "Palm Bay", "homepage_address": "1516 Palm Bay Rd NE, Palm Bay, FL 32905", "latitude": "28.034680", "longitude": "-80.626826", "homepage_delivery_url": "https://www.doordash.com/convenience/store/spirits2u-palm-bay-28656373/", "homepage_hours": "Sun–Thu 8 AM – midnight · Fri–Sat 8 AM – 2 AM", "daily": ["8 AM – midnight"] * 4 + ["8 AM – 2 AM", "8 AM – 2 AM", "8 AM – midnight"]},
        "190": {"homepage_name": "Malabar Road", "homepage_city": "Palm Bay", "homepage_address": "190 Malabar Rd SW #111, Palm Bay, FL 32907", "latitude": "27.997027", "longitude": "-80.675161", "homepage_hours": "Sun–Thu 8 AM – 10 PM · Fri–Sat 8 AM – 11 PM", "daily": ["8 AM – 10 PM"] * 4 + ["8 AM – 11 PM", "8 AM – 11 PM", "8 AM – 10 PM"]},
        "3085": {"homepage_name": "Jupiter Boulevard", "homepage_city": "Palm Bay", "homepage_address": "3085 Jupiter Blvd SE #8, Palm Bay, FL 32909", "latitude": "27.987952", "longitude": "-80.661975", "homepage_hours": "Sun–Thu 9 AM – midnight · Fri–Sat 9 AM – 2 AM", "daily": ["9 AM – midnight"] * 4 + ["9 AM – 2 AM", "9 AM – 2 AM", "9 AM – midnight"]},
        "6939": {"homepage_name": "Pappy's Liquors & Tavern", "homepage_city": "Fort Pierce", "homepage_address": "6939 Okeechobee Rd, Fort Pierce, FL 34945", "latitude": "27.413282", "longitude": "-80.395262", "homepage_hours": "Daily 9 AM – 2 AM", "daily": ["9 AM – 2 AM"] * 7},
    }
    days = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    for number, values in details.items():
        for store in Store.objects.filter(number=number, active=True):
            updates = {}
            for field, value in values.items():
                if field == "daily":
                    for day, hours in zip(days, value):
                        key = f"{day}_hours"
                        if not getattr(store, key):
                            updates[key] = hours
                elif getattr(store, field) in (None, ""):
                    updates[field] = value
            if updates:
                Store.objects.filter(pk=store.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [("orders", "0027_store_friday_hours_store_is_manual_store_latitude_and_more")]
    operations = [migrations.RunPython(populate_verified_details, migrations.RunPython.noop)]
