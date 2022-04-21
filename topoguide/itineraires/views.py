from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Itineraire, Sortie

class ItinerairesView(generic.ListView):
    template_name = 'itineraires/itineraires.html'
    context_object_name = 'route_list'
    
    def get_queryset(self):
        return Itineraire.objects.order_by('title')

def sorties(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire,pk=itineraire_id)
    return render(request,
                  'itineraires/sorties.html',
                  {'itineraire_id':itineraire.id})

"""
class SortiesView(generic.DetailView):
    model = Itineraire
    album = get_object_or_404(Sortie, pk=model.id)
""" 