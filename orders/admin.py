from django.contrib import admin

from django.contrib.auth.models import Group, User

from .models import HomePageContent, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    change_list_template = "admin/orders/store/change_list.html"
    list_display = ("number", "public_name", "homepage_city", "homepage_phone", "homepage_visible", "active")
    list_filter = ("active", "homepage_visible")
    search_fields = ("number", "name", "homepage_name", "homepage_city")
    list_editable = ("homepage_visible",)
    fieldsets = (
        ("Store", {"fields": ("number", "name", "homepage_name", "active", "homepage_visible", "homepage_order", "public_slug")}),
        ("Contact and ordering", {"fields": ("homepage_city", "homepage_address", "homepage_phone", "homepage_delivery_url", "homepage_directions_url")}),
        ("Store photo and map", {"fields": ("homepage_image", "latitude", "longitude"), "description": "Add latitude and longitude to show this store on the map."}),
        ("Store hours", {"fields": ("monday_hours", "tuesday_hours", "wednesday_hours", "thursday_hours", "friday_hours", "saturday_hours", "sunday_hours", "homepage_hours"), "description": "Enter daily hours as visitors should see them, such as 9 AM – 10 PM."}),
    )
@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Branding", {"fields": ("logo_image",)}),
        ("Home page hero", {"fields": ("eyebrow", "headline", "headline_accent", "intro", "hero_image", "hero_point_one", "hero_point_two", "hero_point_three", "search_placeholder", "search_button_text", "nearby_button_text")}),
        ("Home page locations and map", {"fields": ("locations_eyebrow", "locations_heading", "locations_intro", "map_eyebrow", "map_heading", "map_intro")}),
        ("Store pages", {"fields": ("store_eyebrow", "store_hours_heading", "store_back_text", "store_call_text", "store_directions_text", "store_delivery_text")}),
        ("Footer", {"fields": ("footer_tagline", "footer_explore_heading", "footer_locations_text", "footer_map_text", "footer_visit_heading", "footer_visit_text", "footer_delivery_text", "footer_legal_text")}),
        ("Age verification page", {"fields": ("age_background_image", "age_eyebrow", "age_heading", "age_intro", "age_birthdate_label", "age_yes_text", "age_no_text", "age_note")}),
    )

    def has_add_permission(self, request):
        return not HomePageContent.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


# The admin is dedicated to the public storefront.
for model in (Group, User):
    if admin.site.is_registered(model):
        admin.site.unregister(model)

admin.site.site_header = "Spirits2U site administration"
admin.site.site_title = "Spirits2U admin"
admin.site.index_title = "Manage stores and site content"
