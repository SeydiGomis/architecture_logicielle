from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpruntViewSet
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register(r'loans', EmpruntViewSet)

urlpatterns = [
    # API
    path("api/", include(router.urls)),

    # Auth
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Front emprunts
    path("mes-emprunts/", views.emprunts_list, name="emprunts_list"),
    path("mes-emprunts/<int:pk>/", views.emprunt_detail, name="emprunt_detail"),
    path("nouveau/<int:livre_id>/", views.nouvel_emprunt, name="nouvel_emprunt"),
]
