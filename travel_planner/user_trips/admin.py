from django.contrib import admin
from .models import MyTrip

@admin.register(MyTrip)
class MyTripAdmin(admin.ModelAdmin):
    list_display = ('destination', 'start_date', 'end_date', 'user')
    search_fields = ('destination', 'user__username')