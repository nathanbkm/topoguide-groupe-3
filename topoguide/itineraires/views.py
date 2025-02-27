from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.forms.widgets import SelectDateWidget
from .models import Itineraire, Sortie, Comment, Photo
from .forms import CommentForm, ImageForm
from django.db.models import Q, Avg, Count

def HomagepageView(request):
    return render(request, 'itineraires/homepage.html', )

class IndexView(ListView):
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
        
        list_count = []
        
        if query:
            route = route.filter(Q(description__icontains = query) | Q(title__icontains = query))
            return route
        # Gets the difficulty chose in the range   
        difficulty = self.request.GET.get('difficulty')
        # Filter the trips which difficulties are lower than the one inserted
        if difficulty:
            route = route.filter(Q(estim_difficulty__lte = difficulty))
        # Gets the avg difficulty chose in the range
        difficulty_avg = self.request.GET.get('difficulty_avg')
        # Filter the routes which avg dificulties of all the trips are lower than the one inserted
        if difficulty_avg:
            route = route.annotate(avg_difficulty=Avg('sortie__difficulty_felt')).filter(avg_difficulty__lte= difficulty_avg)
        # Gets the two duration between which we search the real duration   
        duration_inf = self.request.GET.get('duration_inf')
        duration_sup = self.request.GET.get('duration_sup')
        # Filter the trips which the real durations are included between the two inserted time if inserted
        if duration_inf and duration_sup:
            route = route.filter(Q(estim_duration__range = (duration_inf, duration_sup)))
        # Gets the avg duration chose in the range
        duration_avg = self.request.GET.get('duration_avg')
        # Filter the routes which avg duration of all the trips are lower than the one inserted
        if duration_avg:
            route = route.annotate(avg_duration=Avg('sortie__actual_duration')).filter(avg_duration__lte = duration_avg)
        # Gets the avg duration chose in the range
        popularity = self.request.GET.get('popularity')
        # Filter the routes which popularity of a route is greater than the one inserted
        # Popularity is the ratio of the sum of trips and comments for one route with the sum of all the trips and comments
        # This ratio is multiplied by 100 which is the values of the range
        if popularity:
            route = route.annotate(popularity = 100*(Count('sortie') + Count('sortie__comment'))
                                   /(Sortie.objects.all().count() + Comment.objects.all().count())
                                   ).filter(popularity__gte = popularity)

        return route
        

class RouteDetailView(DetailView) :
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
        # and the words in the comments for one trip
        if search_term:
            context['trip_list'] = context['trip_list'].filter(Q(user__username__icontains = search_term)
                                                               | Q(comment__description__icontains = search_term))
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
        # Return the context for all boxes checkered
        if debutant and mixte and expert:
            context['trip_list'] = context['trip_list'].filter((Q(group_xp = 'B') | Q(group_xp = 'M')) | Q(group_xp = 'E'))
            return context
        # Return the context for beginner and mixte boxes checkered
        if debutant and mixte:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'B') | Q(group_xp = 'M'))
            return context
        # Return the context for expert and mixte boxes checkered
        if debutant and expert:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'B') | Q(group_xp = 'E'))
            return context
        # Return the context for expert and beginner boxes checkered
        if mixte and expert:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'M') | Q(group_xp = 'E'))
            return context
        # Return the context for beginner box checkered
        if debutant:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'B'))
            return context
        # Return the context for mixte box checkered
        if mixte:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'M'))
            return context
        # Return the context for exprrt box checkered
        if expert:
            context['trip_list'] = context['trip_list'].filter(Q(group_xp = 'E'))
            return context
        
        return context

class TripDetailView(FormMixin, DetailView) :
    """View for a trip showing every information, with a comments section such as a blog
    """
    model = Sortie
    form_class = CommentForm
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
        # Gets the comments related to this trip
        context['comments'] = Comment.objects.filter(trip_id=trip.id).order_by('-pub_date')
        # Gets the images related to this trip
        context['photos'] = Photo.objects.filter(trip_id=trip.id).order_by('-pub_date')
        return context
    
    def get_success_url(self):
        """ Returns a url to update this page after posting a comment
        """
        return reverse('itin:detail_trip', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        """ Constructs a form, checks the validity of the form and processes it accordingly
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Checks if the form is valid, and adds the author and trip
        attributes to the comment
        """
        form.instance.author = self.request.user
        form.instance.trip = Sortie.objects.get(id=self.get_object().id)
        form.save()
        return super().form_valid(form)
    
class TripCreateView(CreateView):
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
    
    def get_form(self):
        '''add date picker in forms'''
        form = super(TripCreateView, self).get_form()
        form.fields['date'].widget = SelectDateWidget()
        return form

class TripUpdateView(UpdateView):
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
        
    def get_form(self):
        '''add date picker in forms'''
        form = super(TripUpdateView, self).get_form()
        form.fields['date'].widget = SelectDateWidget()
        return form
        

def imagesCreateView(request, trip_id):
    """
    Create new images related to a specified trip based
    on user field input in form
    Args:
        request: the incoming request, GET or POST
        trip_id: The trip's ID 
    Returns:
        - a page with an empty form if it was a GET request,
        - a page with an empty form if it was a POST request
          with invalid data,
        - or the page of the related trip if it was a POST with valid data
    """
    trip = get_object_or_404(Sortie, pk=trip_id)
    
    if trip.user != request.user:
        return HttpResponse("Vous ne pouvez ajouter une image que pour les sorties que vous avez créé.")
    elif request.method == 'GET':
        form = ImageForm()
    elif request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')
        if form.is_valid():
            for f in files:
                Photo.objects.create(
                    image = f,
                    trip = trip
                )
            return redirect('itin:detail_trip', pk=trip_id)
    return render(request, 'itineraires/image_form.html', {'form': form})