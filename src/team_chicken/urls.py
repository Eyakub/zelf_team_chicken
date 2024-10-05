from django.contrib import admin
from django.urls import path

from chickenapi.views import ContentAPIView, ContentStatsAPIView, CategoryListView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/contents/stats/", ContentStatsAPIView.as_view(), name="api-contents-stats"),
    path("api/contents/", ContentAPIView.as_view(), name="api-contents"),
    path("api/categories/", CategoryListView.as_view(), name='api-category')
]
