import json
import tempfile
from pathlib import Path

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from .admin import StoreAdmin
from .models import HomePageContent, Store


class PublicStorefrontTests(TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        settings_context = self.settings(AGE_VERIFICATION_LOG_PATH=str(Path(directory.name) / "ages.jsonl"))
        settings_context.enable()
        self.addCleanup(settings_context.disable)
        self.log_file = Path(directory.name) / "ages.jsonl"
        self.store, _ = Store.objects.update_or_create(
            number="1850",
            defaults={
                "name": "SPIRITS2U 1850", "homepage_name": "Merritt Island",
                "monday_hours": "8 AM – 10 PM", "homepage_phone": "(321) 452-4808",
                "homepage_delivery_url": "https://www.doordash.com/store/example/",
                "latitude": "28.389651", "longitude": "-80.701813",
            },
        )

    def test_store_page_shows_hours_and_delivery(self):
        store_url = reverse("public-store-detail", args=[self.store.public_slug])
        self.assertEqual(store_url, "/stores/merritt-island-1850/")
        self.assertEqual(self.client.get(store_url).status_code, 302)
        self.client.post(reverse("age-check"), {"next": store_url, "birthdate": "1990-01-01", "answer": "yes"})
        response = self.client.get(store_url)
        self.assertContains(response, "Merritt Island")
        self.assertContains(response, "8 AM – 10 PM")
        self.assertContains(response, "(321) 452-4808")
        self.assertContains(response, "https://www.doordash.com/store/example/")
        self.assertContains(response, "Call (321) 452-4808")
        self.assertContains(response, 'class="store-detail-hero-photo"')
        self.assertContains(response, "/static/orders/homepage/store-hero.")
        self.assertNotContains(response, 'class="store-detail-photo"')
        self.assertNotContains(response, "Photo coming soon")
        self.assertNotContains(response, 'class="store-visit-panel"')
        site_content = HomePageContent.objects.first()
        site_content.store_hero_image = "homepage/store-hero/custom.jpg"
        site_content.save(update_fields=["store_hero_image"])
        self.client.post(reverse("age-check"), {"next": store_url, "birthdate": "1990-01-01", "answer": "yes"})
        self.assertContains(self.client.get(store_url), "/media/homepage/store-hero/custom.jpg")
        self.assertEqual(self.client.get(store_url).status_code, 302)

    def test_home_hides_staff_sign_in_and_exposes_nearby_store(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 302)
        self.client.post(reverse("age-check"), {"next": "/", "birthdate": "1990-01-01", "answer": "yes"}, REMOTE_ADDR="192.0.2.12")
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="find-nearby"')
        self.assertContains(response, 'data-latitude="28.389651"')
        self.assertContains(response, 'id="store-map"')
        self.assertContains(response, 'id="store-map-data"')
        self.assertNotContains(response, 'class="landing-location-photo"')
        self.assertNotContains(response, 'class="store-map-list"')
        self.assertContains(response, "Store map")
        self.assertNotContains(response, "Staff sign in")
        self.assertNotContains(response, "Neighborhood stores")
        self.assertNotContains(response, "Local, helpful people")
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("public-store-detail", args=[self.store.public_slug])).status_code, 200)
        self.assertEqual(len(self.log_file.read_text().splitlines()), 1)
        record = json.loads(self.log_file.read_text().splitlines()[0])
        self.assertEqual((record["birthdate"], record["age"], record["ip"], record["allowed"]), ("1990-01-01", timezone.localdate().year - 1990, "192.0.2.12", True))

    def test_underage_denied_and_admin_can_clear_log(self):
        response = self.client.post(reverse("age-check"), {"next": "/", "birthdate": "2010-01-01", "answer": "no"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(json.loads(self.log_file.read_text().splitlines()[0])["allowed"])
        admin_user = get_user_model().objects.create_superuser(username="age-admin", password="test-pass-123")
        self.client.force_login(admin_user)
        self.assertContains(self.client.get(reverse("age-log-admin")), "2010-01-01")
        self.assertEqual(self.client.post(reverse("age-log-admin")).status_code, 302)
        self.assertEqual(self.log_file.read_text(), "")

    def test_age_boundary_uses_birthdate(self):
        today = timezone.localdate()
        turning_21 = date(today.year - 21, today.month, today.day)
        day_before_21 = turning_21 + timedelta(days=1)
        denied = self.client.post(reverse("age-check"), {"next": "/", "birthdate": day_before_21.isoformat(), "answer": "yes"})
        self.assertEqual(denied.status_code, 403)
        allowed = self.client.post(reverse("age-check"), {"next": "/", "birthdate": turning_21.isoformat(), "answer": "yes"})
        self.assertEqual(allowed.status_code, 302)

    def test_admin_can_add_public_store_fields(self):
        request = RequestFactory().get("/admin/orders/store/add/")
        request.user = get_user_model()(username="admin", is_superuser=True, is_staff=True)
        form = StoreAdmin(Store, AdminSite()).get_form(request)
        for field in ("number", "name", "homepage_image", "homepage_phone", "public_slug", "monday_hours", "homepage_delivery_url", "latitude"):
            self.assertIn(field, form.base_fields)

    def test_admin_is_focused_on_stores_and_site_content(self):
        admin_user = get_user_model().objects.create_superuser(username="site-admin", password="test-pass-123")
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "Manage stores")
        self.assertContains(response, "Edit site content")
        self.assertContains(response, "age verification logs")
        self.assertNotContains(response, "Store order lists")
        self.assertEqual(self.client.get("/admin/orders/product/").status_code, 404)
        store_admin = self.client.get(reverse("admin:orders_store_add"))
        self.assertEqual(store_admin.status_code, 200)
        self.assertContains(store_admin, 'href="/admin/age-logs/">ID verification logs</a>')
        content_admin = self.client.get(reverse("admin:orders_homepagecontent_change", args=[HomePageContent.objects.first().pk]))
        self.assertContains(content_admin, 'name="store_hero_image"')

    def test_site_content_changes_public_pages(self):
        content = HomePageContent.objects.first() or HomePageContent()
        content.map_heading = "Our store map"
        content.age_heading = "Please confirm your age"
        content.save()
        self.assertContains(self.client.get(reverse("age-check")), "Please confirm your age")
        self.client.post(reverse("age-check"), {"next": "/", "birthdate": "1990-01-01", "answer": "yes"})
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Our store map")
        self.assertNotContains(response, "Store order lists")
        self.client.force_login(get_user_model().objects.create_superuser(username="content-admin", password="test-pass-123"))
        self.assertNotContains(self.client.get(reverse("home")), "Store order lists")

    def test_admin_can_create_a_public_store(self):
        admin_user = get_user_model().objects.create_superuser(username="new-store-admin", password="test-pass-123")
        self.client.force_login(admin_user)
        response = self.client.post(reverse("admin:orders_store_add"), {
            "number": "4444", "name": "New Palm Bay Store", "homepage_name": "Palm Bay Central",
            "active": "on", "homepage_visible": "on", "homepage_order": "100",
            "homepage_city": "Palm Bay", "homepage_address": "4444 Example Road, Palm Bay, FL 32909",
            "homepage_phone": "(321) 555-4444", "homepage_delivery_url": "https://www.doordash.com/store/example/",
            "monday_hours": "9 AM – 10 PM", "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        created = Store.objects.get(number="4444")
        self.assertEqual(created.public_slug, "palm-bay-central-4444")
        self.assertEqual(created.monday_hours, "9 AM – 10 PM")

    def test_legacy_internal_routes_are_not_exposed(self):
        for path in (
            "/orders/1/", "/inventory/", "/bulk-orders/", "/bulk-orders/1/",
            "/ops/", "/users/", "/deliveries/", "/deliveries/new/",
            "/deliveries/review/", "/api/health/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
