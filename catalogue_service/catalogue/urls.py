from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivreViewSet, catalogue_page

router = DefaultRouter()
router.register(r'books', LivreViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("catalogue/", catalogue_page, name="catalogue_page"),
]
