from django.contrib import admin

from .models import Itineraire, Localisation, Sortie, Comment, Photo

# Access to the models for the admin users to modify or create them
admin.site.register(Itineraire)
admin.site.register(Sortie)
admin.site.register(Comment)
admin.site.register(Photo)
admin.site.register(Localisation)