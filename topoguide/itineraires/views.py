from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin

from .models import Itineraire, Photo, Sortie, Comment
from .forms import CommentForm, ImageForm

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
        return Itineraire.objects.order_by('title')

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