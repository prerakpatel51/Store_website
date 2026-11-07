from django.db import migrations


def feature_reference_stores(apps, schema_editor):
    Store = apps.get_model("orders", "Store")
    HomePageContent = apps.get_model("orders", "HomePageContent")
    HomePageContent.objects.get_or_create(pk=1)
    featured = (
        ("110", "Cocoa Beach", 1),
        ("1850", "Merritt Island", 2),
        ("3210", "Rockledge", 3),
        ("6300", "Suntree", 4),
    )
    for number, city, order in featured:
        for store in Store.objects.filter(number=number, name__icontains="SPIRITS2U", active=True):
            updates = {}
            if not store.homepage_name:
                updates["homepage_name"] = city
            if not store.homepage_city:
                updates["homepage_city"] = city
            if store.homepage_order == 100:
                updates["homepage_order"] = order
            if updates:
                Store.objects.filter(pk=store.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [("orders", "0025_homepagecontent_store_homepage_address_and_more")]

    operations = [migrations.RunPython(feature_reference_stores, migrations.RunPython.noop)]
