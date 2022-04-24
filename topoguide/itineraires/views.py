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
        route = Itineraire.objects.order_by('title')

        query = self.request.GET.get('search_term')
        
        if query:
            route = route.filter(Q(description__icontains = query) | Q(title__icontains = query))
            return route
        # Gets the difficulty choose in the range   
        difficulty = self.request.GET.get('difficulty')
        # Filter the trips which difficulties are lower than the one inserted
        if difficulty:
            route = route.filter(Q(estim_difficulty__lte = difficulty))
        # Gets the two duration between which we search the real duration   
        duration_inf = self.request.GET.get('duration_inf')
        duration_sup = self.request.GET.get('duration_sup')
        # Filter the trips which the real durations are included between the two inserted time if inserted
        if duration_inf and duration_sup:
            route = route.filter(Q(estim_duration__range = (duration_inf, duration_sup)))
        
        return route
        

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
        # Gets the charfield in the charbar        
        search_term = self.request.GET.get('search_term')
        # Filter the trips with the usernames that contains what we have in the searchbar if something is writen
        if search_term:
            context['trip_list'] = context['trip_list'].filter(Q(user__username__icontains = search_term))
            return context
        # Gets the two dates inserted in the interface    
        date_pub_inf = self.request.GET.get('date_pub_inf')
        date_pub_sup = self.request.GET.get('date_pub_sup')
        # Filter the trips which the date of publication is included between the two inserted date if inserted
        if date_pub_inf and date_pub_sup:
            context['trip_list'] = context['trip_list'].filter(Q(date__range = (date_pub_inf, date_pub_sup)))
        # Gets the difficulty choose in the range   
        difficulty = self.request.GET.get('difficulty')
        # Filter the trips which difficulties are lower than the one inserted
        if difficulty:
            context['trip_list'] = context['trip_list'].filter(Q(difficulty_felt__lte = difficulty))
        # Gets the two duration between which we search the real duration   
        duration_inf = self.request.GET.get('duration_inf')
        duration_sup = self.request.GET.get('duration_sup')
        # Filter the trips which the real durations are included between the two inserted time if inserted
        if duration_inf and duration_sup:
            context['trip_list'] = context['trip_list'].filter(Q(actual_duration__range = (duration_inf, duration_sup)))
        # Gets the information of a checkered checkbox
        debutant = self.request.GET.get('B')
        mixte = self.request.GET.get('M')
        expert = self.request.GET.get('E')
        # Filter the trips which the experience of the group are checkered by the ckeckboxes
        if debutant and mixte and expert:
            context['trip_list'] = context['trip_list'].filter((Q(group_xp = 'B') | Q(group_xp = 'M')) | Q(group_xp = 'E'))
            return context
        if debutant and mixte:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'B') | Q(group_xp = 'M'))
            return context
        if debutant and expert:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'B') | Q(group_xp = 'E'))
            return context
        if mixte and expert:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'M') | Q(group_xp = 'E'))
            return context
            return context
        if debutant:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'B'))
            return context
        if mixte:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'M'))
            return context
        if expert:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'E'))
            return context
        
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