from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views import generic
from .models import Itineraire, Sortie
from django.db.models import Q

class IndexView(generic.ListView):
    """View for the main page aka the list of routes
    """
    template_name = 'itineraires/itineraires.html'
    context_object_name = 'route_list'
    
    def get_queryset(self):
        """Gets the itineraires and filters them alphabetically

        Returns:
            Itineraire[] : The sorted itineraires
        """
        result = Itineraire.objects.order_by('title')

        query = self.request.GET.get('search_term')
        if query:
            result = result.filter(Q(description__icontains = query) | Q(title__icontains = query))
        return result

class RouteDetailView(generic.DetailView) :
    """View for a route along with its trips
    """
    model = Itineraire
    template_name = "itineraires/sorties.html"
    def get_context_data(self, **kwargs):
        """Adds the context variables needed for the html to work
        """
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Gets the route
        route = self.get_object()
        # Could be context_object_name = 'route'
        context['route'] = route
        # Gets all trips on this route
        context['trip_list'] = Sortie.objects.all().filter(route=route)
        return context

class TripDetailView(generic.DetailView) :
    """View for a trip showing every information
    """
    model = Sortie
    template_name = 'itineraires/sortie.html'
    def get_context_data(self, **kwargs):
        """Adds the context variables needed for the html to work
        """
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Gets the trip
        trip = self.get_object()
        # Could be context_object_name = 'trip'
        context['trip'] = trip
        # Gets the route of the trip for more lisibility
        context['route'] = trip.route
        return context

class TripCreateView(generic.CreateView):
    """View for the creation of a new trip
    """
    model = Sortie 
    fields = ['date','actual_duration','number_people','group_xp','weather',
              'difficulty_felt']
    
    def get_context_data(self, **kwargs):
        """Adds the context variables needed for the html to work
        """
        context = super().get_context_data(**kwargs)
        context['create'] = True
        return context
    
    def get_success_url(self):
        """ Returns a url to redirect to the previous page after completion
        """
        return reverse('itin:detail_trip', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Checks if the form is valid, and adds the user and route
        to the fields of the form
        """
        form.instance.user = self.request.user
        form.instance.route = Itineraire.objects.get(
            id=self.request.GET.get("route_id"))
        return super().form_valid(form)

class TripUpdateView(generic.UpdateView):
    """View to edit a trip
    """
    model = Sortie
    fields = ['date','actual_duration','number_people','group_xp','weather','difficulty_felt']

    def get_context_data(self, **kwargs):
        """Adds the context variables needed for the html to work
        """
        context = super().get_context_data(**kwargs)
        context['create'] = False
        return context
    
    def get_success_url(self):
        """ Returns a url to redirect to the previous page after completion
        """
        return reverse('itin:detail_trip', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Checks if the form is valid, and adds the user and route
        to the fields of the form
        """
        if form.instance.user == self.request.user :
            return super().form_valid(form)
        else :
            return HttpResponseForbidden("Vous n'avez pas créé cette sortie, vous ne pouvez donc pas la modifier.")