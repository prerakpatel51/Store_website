from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from orders import views

urlpatterns = [
    path("admin/age-logs/", admin.site.admin_view(views.age_logs_admin_view), name="age-log-admin"),
    path("admin/", admin.site.urls),
    path("age-check/", views.AgeCheckView.as_view(), name="age-check"),
    path("media/homepage/<path:filename>", views.public_homepage_image, name="public-homepage-image"),
    path("", views.HomeView.as_view(), name="home"),
    path("stores/<slug:public_slug>/", views.PublicStoreDetailView.as_view(), name="public-store-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
