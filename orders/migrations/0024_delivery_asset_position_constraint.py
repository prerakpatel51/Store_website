from django.db import migrations, models


def normalize_asset_positions(apps, schema_editor):
    DeliveryAsset = apps.get_model("orders", "DeliveryAsset")
    groups = DeliveryAsset.objects.values_list("delivery_id", "category").distinct()
    for delivery_id, category in groups.iterator():
        rows = list(
            DeliveryAsset.objects.filter(delivery_id=delivery_id, category=category).order_by(
                "position", "created_at", "pk"
            )
        )
        changed = []
        for position, row in enumerate(rows):
            if row.position != position:
                row.position = position
                changed.append(row)
        if changed:
            DeliveryAsset.objects.bulk_update(changed, ["position"])


class Migration(migrations.Migration):
    dependencies = [("orders", "0023_taskexecutionmetric")]

    operations = [
        migrations.RunPython(normalize_asset_positions, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="deliveryasset",
            constraint=models.UniqueConstraint(
                fields=("delivery", "category", "position"),
                name="unique_delivery_asset_category_position",
            ),
        ),
    ]
