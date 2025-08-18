from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Livre
from .serializers import LivreSerializer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm


class LivreViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.all().order_by("-created_at")
    serializer_class = LivreSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        dispo = self.request.query_params.get("disponible") 
        if q:
            qs = qs.filter(
                Q(titre__icontains=q) |
                Q(auteur__icontains=q) |
                Q(categorie__icontains=q)
            )
        if dispo is not None:
            if dispo.lower() in ("true", "1", "yes"):
                qs = qs.filter(disponible=True)
            elif dispo.lower() in ("false", "0", "no"):
                qs = qs.filter(disponible=False)
        return qs

    @action(detail=True, methods=["patch"])
    def reserver(self, request, pk=None):
        livre = self.get_object()
        if not livre.disponible:
            return Response({"detail": "Déjà indisponible"}, status=400)
        livre.disponible = False
        livre.save()
        return Response(self.get_serializer(livre).data)

    @action(detail=True, methods=["patch"])
    def restituer(self, request, pk=None):
        livre = self.get_object()
        if livre.disponible:
            return Response({"detail": "Déjà disponible"}, status=400)
        livre.disponible = True
        livre.save()
        return Response(self.get_serializer(livre).data)
    
    def catalogue_page(request):
        return render(request, "catalogue.html")
    
# --- API REST ---
class BookViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.all()
    serializer_class = LivreSerializer

# --- Page HTML ---
def catalogue_page(request):
    livres = Livre.objects.all()
    return render(request, "catalogue.html", {"livres": livres})

def catalogue_list(request):
    livres = Livre.objects.all()
    return render(request, "catalogue/list.html", {"livres": livres})

def catalogue_detail(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    return render(request, "catalogue/detail.html", {"livre": livre})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})