import uuid
import re

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Store(TimeStampedModel):
    number = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    homepage_visible = models.BooleanField(default=True, help_text="Show this active store on the public home page.")
    homepage_name = models.CharField(max_length=120, blank=True, help_text="Optional public name; defaults to the store name.")
    public_slug = models.SlugField(max_length=180, unique=True, null=True, blank=True, help_text="Name-based public URL; generated automatically when empty.")
    homepage_city = models.CharField(max_length=120, blank=True)
    homepage_address = models.CharField(max_length=255, blank=True)
    homepage_phone = models.CharField(max_length=30, blank=True, help_text="Public store phone number, including area code.")
    homepage_hours = models.CharField(max_length=120, blank=True, help_text="Plain text hours; leave empty if unverified.")
    monday_hours = models.CharField(max_length=80, blank=True)
    tuesday_hours = models.CharField(max_length=80, blank=True)
    wednesday_hours = models.CharField(max_length=80, blank=True)
    thursday_hours = models.CharField(max_length=80, blank=True)
    friday_hours = models.CharField(max_length=80, blank=True)
    saturday_hours = models.CharField(max_length=80, blank=True)
    sunday_hours = models.CharField(max_length=80, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    homepage_image = models.ImageField(upload_to="homepage/stores/", blank=True)
    homepage_delivery_url = models.URLField(blank=True)
    homepage_directions_url = models.URLField(blank=True)
    homepage_order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ["number", "name"]

    def __str__(self):
        return f"{self.number} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.public_slug:
            base = slugify(f"{self.homepage_name or self.name}-{self.number}")[:165] or f"store-{self.pk or uuid.uuid4().hex[:8]}"
            candidate = base
            suffix = 2
            while Store.objects.filter(public_slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.public_slug = candidate
        super().save(*args, **kwargs)

    @property
    def public_name(self):
        return self.homepage_name or self.name

    @property
    def daily_hours(self):
        return [(day, getattr(self, f"{day.lower()}_hours")) for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")]

    @property
    def today_hours(self):
        today = timezone.localdate().strftime("%A").lower()
        return getattr(self, f"{today}_hours") or self.homepage_hours

    @property
    def phone_href(self):
        return re.sub(r"[^0-9+]", "", self.homepage_phone)


class HomePageContent(TimeStampedModel):
    logo_image = models.ImageField(upload_to="homepage/branding/", blank=True, help_text="Optional replacement for the Spirits2U logo.")
    eyebrow = models.CharField(max_length=100, default="YOUR NEIGHBORHOOD SPIRITS STORE")
    headline = models.CharField(max_length=120, default="Great Selection.")
    headline_accent = models.CharField(max_length=120, default="Greater Service.")
    intro = models.TextField(default="Discover beer, wine and spirits with a friendly local team ready to help.")
    hero_image = models.ImageField(upload_to="homepage/hero/", blank=True)
    store_hero_image = models.ImageField(upload_to="homepage/store-hero/", blank=True, help_text="Optional image behind the store page heading; uses the default store hero when empty.")
    locations_heading = models.CharField(max_length=120, default="Find a Spirits2U Near You")
    locations_intro = models.CharField(max_length=255, default="Explore our neighborhood stores and find the one that is right for you.")
    hero_point_one = models.CharField(max_length=80, default="Helpful staff")
    hero_point_two = models.CharField(max_length=80, default="Local stores")
    hero_point_three = models.CharField(max_length=80, default="Great selection")
    search_placeholder = models.CharField(max_length=100, default="Search city, store or ZIP")
    nearby_button_text = models.CharField(max_length=80, default="Use my location")
    search_button_text = models.CharField(max_length=60, default="Search")
    locations_eyebrow = models.CharField(max_length=80, default="OUR LOCATIONS")
    map_eyebrow = models.CharField(max_length=80, default="EXPLORE THE AREA")
    map_heading = models.CharField(max_length=120, default="Find us on the map")
    map_intro = models.CharField(max_length=255, default="Tap a numbered marker to see the store name, hours and a link to its page.")
    store_eyebrow = models.CharField(max_length=100, default="YOUR NEIGHBORHOOD SPIRITS STORE")
    store_hours_heading = models.CharField(max_length=100, default="Store hours")
    store_back_text = models.CharField(max_length=80, default="All locations")
    store_directions_text = models.CharField(max_length=80, default="Get directions")
    store_call_text = models.CharField(max_length=40, default="Call")
    store_delivery_text = models.CharField(max_length=80, default="Order on DoorDash")
    footer_tagline = models.CharField(max_length=255, default="Your neighborhood destination for beer, wine and spirits.")
    footer_explore_heading = models.CharField(max_length=80, default="Explore")
    footer_visit_heading = models.CharField(max_length=80, default="Visit us")
    footer_visit_text = models.CharField(max_length=255, default="Find store hours, directions and phone numbers on each location page.")
    footer_delivery_text = models.CharField(max_length=255, default="DoorDash ordering is available at select stores.")
    footer_legal_text = models.CharField(max_length=255, default="For adults 21 and older. Please enjoy responsibly.")
    footer_locations_text = models.CharField(max_length=80, default="All locations")
    footer_map_text = models.CharField(max_length=80, default="Store map")
    age_background_image = models.ImageField(upload_to="homepage/age-check/", blank=True)
    age_eyebrow = models.CharField(max_length=80, default="WELCOME TO SPIRITS2U")
    age_heading = models.CharField(max_length=120, default="Are you 21 years or older?")
    age_intro = models.CharField(max_length=255, default="Please enter your birthdate and answer before continuing.")
    age_note = models.CharField(max_length=255, default="Your birthdate, calculated age, answer, IP address, and visit result are recorded.")
    age_birthdate_label = models.CharField(max_length=80, default="Your birthdate")
    age_yes_text = models.CharField(max_length=80, default="Yes, I am 21 or older")
    age_no_text = models.CharField(max_length=80, default="No, I am under 21")

    class Meta:
        verbose_name = "Site content"
        verbose_name_plural = "Site content"

    def __str__(self):
        return "Site content"
