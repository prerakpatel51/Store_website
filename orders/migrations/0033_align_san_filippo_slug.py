from django.db import migrations


def align_san_filippo_slug(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    Store.objects.filter(number="1181", public_slug="spirits2u-1181-1181").update(
        public_slug="san-filippo-1181"
    )


class Migration(migrations.Migration):
    dependencies = [("orders", "0032_map_remaining_public_locations")]
    operations = [migrations.RunPython(align_san_filippo_slug, migrations.RunPython.noop)]
