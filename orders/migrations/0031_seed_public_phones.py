from django.db import migrations


def seed_phones(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    verified = {
        "1850": "(321) 452-4808",
        "3210": "(321) 509-1045",
        "1317": "(321) 802-4293",
        "1516": "(321) 345-4531",
        "190": "(321) 722-1109",
        "3085": "(321) 914-3479",
        "6939": "(772) 466-6939",
    }
    for number, phone in verified.items():
        Store.objects.filter(number=number, homepage_phone="").update(homepage_phone=phone)


class Migration(migrations.Migration):
    dependencies = [("orders", "0030_store_public_slug")]
    operations = [migrations.RunPython(seed_phones, migrations.RunPython.noop)]
