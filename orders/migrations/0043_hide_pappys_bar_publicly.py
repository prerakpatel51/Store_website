from django.db import migrations


def hide_pappys_bar(apps, schema_editor):
    store = apps.get_model('orders', 'Store')
    store.objects.filter(number='6940').update(homepage_visible=False)


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0042_map_store_name_labels'),
    ]

    operations = [
        migrations.RunPython(hide_pappys_bar, migrations.RunPython.noop),
    ]
