import os
import requests
from urllib.parse import quote
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Emprunt, Livre
from .serializers import EmpruntSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


CATALOGUE_BASE_URL = os.getenv("CATALOGUE_BASE_URL", "http://127.0.0.1:8001")


class EmpruntViewSet(viewsets.ModelViewSet):
    queryset = Emprunt.objects.all().order_by("-date_emprunt")
    serializer_class = EmpruntSerializer
    def emprunter(self, request):
        livre_id = request.data.get("livre_id")
        user_id = request.data.get("user_id")

        if not livre_id or not user_id:
            return Response({"error": "Champs manquants"}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier disponibilité du livre
        livre = Livre.objects.filter(id=livre_id, disponible=True).first()
        if not livre:
            return Response({"error": "Livre indisponible"}, status=status.HTTP_400_BAD_REQUEST)

        # Créer l’emprunt
        emprunt = Emprunt.objects.create(
            utilisateur_id=user_id,
            livre_id=livre_id
        )
        # Mettre le livre en indisponible
        livre.disponible = False
        livre.save()

        return Response({"message": "Emprunt créé avec succès 🎉", "emprunt_id": emprunt.id}, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        return self.emprunter(request)

    @action(detail=False, methods=["get"])
    def disponibles(self, request):
        q = request.query_params.get("q")
        url = f"{CATALOGUE_BASE_URL}/api/books/?disponible=true"
        if q:
            url += f"&q={quote(q)}"
        try:
            r = requests.get(url, timeout=5)
            return Response(r.json(), status=r.status_code)
        except requests.RequestException:
            return Response({"detail": "Catalogue injoignable"}, status=502)

    @action(detail=False, methods=["post"])
    def emprunter(self, request):
        try:
            utilisateur_id = int(request.data.get("utilisateur_id"))
            livre_id = int(request.data.get("livre_id"))
        except (TypeError, ValueError):
            return Response({"detail": "utilisateur_id et livre_id doivent être des entiers"}, status=400)

        try:
            r = requests.get(f"{CATALOGUE_BASE_URL}/api/books/{livre_id}/", timeout=5)
        except requests.RequestException:
            return Response({"detail": "Catalogue injoignable"}, status=502)

        if r.status_code == 404:
            return Response({"detail": "Livre introuvable"}, status=404)
        if r.status_code != 200:
            return Response({"detail": "Erreur catalogue"}, status=502)
        livre = r.json()

        if not livre.get("disponible", False):
            return Response({"detail": "Livre indisponible"}, status=400)

        try:
            pr = requests.patch(f"{CATALOGUE_BASE_URL}/api/books/{livre_id}/reserver/", timeout=5)
        except requests.RequestException:
            return Response({"detail": "Catalogue injoignable"}, status=502)
        if pr.status_code >= 400:
            return Response({"detail": "Échec réservation livre"}, status=400)

        try:
            obj = Emprunt.objects.create(utilisateur_id=utilisateur_id, livre_id=livre_id)
        except Exception as e:
            try:
                requests.patch(f"{CATALOGUE_BASE_URL}/api/books/{livre_id}/restituer/", timeout=5)
            except requests.RequestException:
                pass
            return Response({"detail": "Impossible de créer l'emprunt (déjà en cours ?)", "error": str(e)}, status=400)

        return Response(self.get_serializer(obj).data, status=201)

    @action(detail=True, methods=["post"])
    def rendre(self, request, pk=None):
        obj = self.get_object()
        if obj.statut == "RENDU":
            return Response({"detail": "Déjà rendu"}, status=400)

        try:
            pr = requests.patch(f"{CATALOGUE_BASE_URL}/api/books/{obj.livre_id}/restituer/", timeout=5)
        except requests.RequestException:
            return Response({"detail": "Catalogue injoignable"}, status=502)
        if pr.status_code >= 400:
            return Response({"detail": "Échec restitution livre"}, status=400)

        obj.statut = "RENDU"
        obj.date_retour = timezone.now()
        obj.save()
        return Response(self.get_serializer(obj).data)


def emprunts_page(request):
    emprunts = Emprunt.objects.all()
    return render(request, "emprunts/emprunts_list.html", {"emprunts": emprunts})

class EmpruntForm(forms.Form):
    livre_id = forms.IntegerField(widget=forms.HiddenInput())

@login_required
def emprunts_list(request):
    emprunts = Emprunt.objects.filter(utilisateur_id=request.user.id)
    return render(request, "emprunts/list.html", {"emprunts": emprunts})

@login_required
def emprunt_detail(request, pk):
    emprunt = get_object_or_404(Emprunt, pk=pk, utilisateur_id=request.user.id)
    return render(request, "emprunts/detail.html", {"emprunt": emprunt})

@login_required
def emprunt_new(request, livre_id=None):
    if request.method == "POST":
        form = EmpruntForm(request.POST)
        if form.is_valid():
            Emprunt.objects.create(
                utilisateur_id=request.user.id,
                livre_id=form.cleaned_data["livre_id"]
            )
            return redirect("emprunts_list")
    else:
        form = EmpruntForm(initial={"livre_id": livre_id})
    return render(request, "emprunts/new.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def nouvel_emprunt(request, livre_id):
    r = requests.get(f"{CATALOGUE_BASE_URL}/api/books/{livre_id}/")
    if r.status_code != 200:
        messages.error(request, "Livre introuvable ou catalogue injoignable")
        return redirect("catalogue_page")

    livre = r.json()

    if request.method == "POST":
        utilisateur_id = request.POST.get("utilisateur_id")
        try:
            pr = requests.post("http://127.0.0.1:8002/api/loans/emprunter/", json={
                "utilisateur_id": utilisateur_id,
                "livre_id": livre_id,
            })
            if pr.status_code == 201:
                messages.success(request, "Livre emprunté avec succès 🎉")
                return redirect("catalogue_page")
            else:
                messages.error(request, f"Erreur: {pr.json().get('detail', 'Impossible d’emprunter')}")
        except requests.RequestException:
            messages.error(request, "Erreur de communication avec le service d’emprunt")

    return render(request, "emprunts/nouvel_emprunt.html", {"livre": livre})