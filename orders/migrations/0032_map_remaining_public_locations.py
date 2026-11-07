from django.db import migrations


def map_remaining_locations(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    details = {
        "1181": {"homepage_name": "San Filippo", "homepage_city": "Palm Bay", "homepage_address": "1181 San Filippo Dr SE #500, Palm Bay, FL 32909", "latitude": "27.952925", "longitude": "-80.628516"},
        "6940": {"homepage_name": "Pappy's Bar", "homepage_city": "Fort Pierce", "homepage_address": "6939 Okeechobee Rd, Fort Pierce, FL 34945", "latitude": "27.413282", "longitude": "-80.395262"},
    }
    for number, fields in details.items():
        for store in Store.objects.filter(number=number, active=True):
            updates = {field: value for field, value in fields.items() if getattr(store, field) in (None, "")}
            if updates:
                Store.objects.filter(pk=store.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [("orders", "0031_seed_public_phones")]
    operations = [migrations.RunPython(map_remaining_locations, migrations.RunPython.noop)]
