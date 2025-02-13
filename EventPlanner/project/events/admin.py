from django.contrib import admin
from .models import Event

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location')  # Görünmesini istediğin alanlar
    search_fields = ('name', 'location')        # Arama yapılacak alanlar


    