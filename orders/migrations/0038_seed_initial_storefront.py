import json
from pathlib import Path

from django.conf import settings
from django.db import migrations


def seed_initial_storefront(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    HomePageContent = apps.get_model("orders", "HomePageContent")
    fixture_path = Path(settings.BASE_DIR) / "orders" / "fixtures" / "initial_storefront.json"
    for record in json.loads(fixture_path.read_text(encoding="utf-8")):
        fields = record["fields"].copy()
        fields.pop("created_at", None)
        fields.pop("updated_at", None)
        if record["model"] == "orders.store":
            number = fields.pop("number")
            Store.objects.using(schema_editor.connection.alias).get_or_create(number=number, defaults=fields)
        elif record["model"] == "orders.homepagecontent":
            if not HomePageContent.objects.using(schema_editor.connection.alias).exists():
                HomePageContent.objects.using(schema_editor.connection.alias).create(**fields)


class Migration(migrations.Migration):
    dependencies = [("orders", "0037_delete_apirequestlog_and_more")]
    operations = [migrations.RunPython(seed_initial_storefront, migrations.RunPython.noop)]
