from django.db import migrations


VERIFIED_HOURS = {
    "110": ("Daily 9 AM – midnight", ["9 AM – midnight"] * 7),
    "1181": (
        "Sun–Thu 9 AM – midnight · Fri–Sat 9 AM – 2 AM",
        ["9 AM – midnight"] * 4 + ["9 AM – 2 AM"] * 2 + ["9 AM – midnight"],
    ),
    "3210": ("Daily 8 AM – midnight", ["8 AM – midnight"] * 7),
    "6300": (
        "Sun–Thu 8 AM – 10 PM · Fri–Sat 8 AM – midnight",
        ["8 AM – 10 PM"] * 4 + ["8 AM – midnight"] * 2 + ["8 AM – 10 PM"],
    ),
}
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def add_verified_hours(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    for number, (summary, daily_hours) in VERIFIED_HOURS.items():
        store = Store.objects.using(schema_editor.connection.alias).filter(number=number).first()
        if store is None:
            continue
        updates = {}
        if not store.homepage_hours:
            updates["homepage_hours"] = summary
        for day, hours in zip(DAYS, daily_hours):
            field = f"{day}_hours"
            if not getattr(store, field):
                updates[field] = hours
        if updates:
            Store.objects.using(schema_editor.connection.alias).filter(pk=store.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [("orders", "0038_seed_initial_storefront")]
    operations = [migrations.RunPython(add_verified_hours, migrations.RunPython.noop)]
