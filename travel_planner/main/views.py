from django.shortcuts import render
from django.utils import timezone
from datetime import date
from user_trips.models import MyTrip
from django.db import models
from destinations.views import get_destinations_by_category

def homepage(request):
    if request.user.is_authenticated:
        today = date.today()
        
        # Get both owned and shared current/future trips
        current_future_trips = MyTrip.objects.filter(
            models.Q(user=request.user) | models.Q(shared_with=request.user),
            end_date__gte=today
        ).order_by('start_date')
        
        selected_category = request.GET.get('category', 'all')
        destinations = get_destinations_by_category(selected_category)

        context = {
            'current_future_trips': current_future_trips,
            'destinations': destinations,
            'selected_category': selected_category,
        }
        return render(request, 'main/homepage.html', context)
    return render(request, 'main/homepage.html')
