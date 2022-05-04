from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

# The app name to be refered to in urls in the templates
app_name = 'itin'

# The login_required function that contains the view method
# is the authentification control that works for both
# generic and non-genetic views

urlpatterns = [
    
    #The main page
    path(
        '', 
        name = 'homepage',
        view = login_required(
            views.HomagepageView
        )
    ),
    
    #The main page
    path(
        'itineraires/', 
        name = 'index',
        view = login_required(
            views.IndexView.as_view()
        )
    ),
    
    # Details of an itineraire
    path(
        'sorties/<int:pk>',
        name="detail_route",
        view = login_required(
            views.RouteDetailView.as_view()
        )
    ),
    
    # Details of a sortie
    path(
        'sortie/<int:pk>',
        name="detail_trip",
        view = login_required(
            views.TripDetailView.as_view()
        )
    ),
    
    # Sortie creation form
    path(
        'nouvelle_sortie/',
        name = "new_trip",
        view = login_required(
            views.TripCreateView.as_view()
        )
    ),
    
    # Sortie edit form
    path(
        'modif_sortie/<int:pk>',
        name = "edit_trip",
        view = login_required(
            views.TripUpdateView.as_view()
        )
    ),
    
    # Image form
    path(
        'nouvelle_image/<int:trip_id>',
        name = "new_image",
        view = login_required(
            views.imagesCreateView
        )
    )
]