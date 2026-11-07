from datetime import date

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from .age_gate import append_age_log, clear_age_logs, read_age_logs, safe_public_path
from .models import HomePageContent, Store


@method_decorator(never_cache, name="dispatch")
class HomeView(TemplateView):
    template_name = "orders/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homepage"] = HomePageContent.objects.first() or HomePageContent()
        context["public_stores"] = list(Store.objects.filter(active=True, homepage_visible=True).order_by("homepage_order", "number", "name"))
        context["public_store_count"] = len(context["public_stores"])
        context["map_stores"] = [
            {
                "name": store.public_name,
                "number": store.number,
                "city": store.homepage_city,
                "address": store.homepage_address,
                "hours": store.today_hours,
                "latitude": float(store.latitude),
                "longitude": float(store.longitude),
                "url": reverse("public-store-detail", args=[store.public_slug]),
            }
            for store in context["public_stores"]
            if store.latitude is not None and store.longitude is not None
        ]
        return context


@method_decorator(never_cache, name="dispatch")
class PublicStoreDetailView(TemplateView):
    template_name = "orders/store_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = get_object_or_404(Store, public_slug=kwargs["public_slug"], active=True, homepage_visible=True)
        context["homepage"] = HomePageContent.objects.first() or HomePageContent()
        return context


@method_decorator(never_cache, name="dispatch")
class AgeCheckView(TemplateView):
    template_name = "orders/age_check.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_path"] = safe_public_path(self.request.GET.get("next"))
        context["today"] = timezone.localdate().isoformat()
        context["homepage"] = HomePageContent.objects.first() or HomePageContent()
        return context

    def post(self, request, *args, **kwargs):
        next_path = safe_public_path(request.POST.get("next"))
        answer = request.POST.get("answer", "")
        today = timezone.localdate()
        try:
            birthdate = date.fromisoformat(request.POST.get("birthdate", ""))
        except (TypeError, ValueError):
            birthdate = None
        age = None
        if birthdate and birthdate <= today:
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        valid_birthdate = age is not None and 0 <= age <= 120
        allowed = bool(valid_birthdate and age >= 21 and answer == "yes")
        append_age_log(request, birthdate.isoformat() if valid_birthdate else None, age if valid_birthdate else None, answer, allowed, next_path)
        if allowed:
            if next_path == "/":
                request.session["age_verified_via_home"] = True
            else:
                request.session["age_gate_allowed_path"] = next_path
            return redirect(next_path)
        if not valid_birthdate or answer not in ("yes", "no"):
            error = "Please enter a valid birthdate and answer the question."
        elif age < 21:
            error = "You must be 21 or older to enter this site."
        else:
            error = "Your birthdate and answer do not agree."
        return render(request, self.template_name, {
            "next_path": next_path,
            "birthdate": birthdate.isoformat() if valid_birthdate else "",
            "today": today.isoformat(),
            "error": error,
            "homepage": HomePageContent.objects.first() or HomePageContent(),
        }, status=403)


@never_cache
def age_logs_admin_view(request):
    if not request.user.is_active or not request.user.is_staff or not request.user.is_superuser:
        raise PermissionDenied
    if request.method == "POST":
        clear_age_logs()
        messages.success(request, "Age verification log file cleared.")
        return redirect("age-log-admin")
    return render(request, "admin/orders/age_logs.html", {
        **admin.site.each_context(request),
        "title": "Age verification logs",
        "records": read_age_logs(),
    })
