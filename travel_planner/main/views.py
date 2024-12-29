from django.shortcuts import render
from django.utils import timezone
from datetime import date
from user_trips.models import MyTrip

def homepage(request):
    if request.user.is_authenticated:
        today = date.today()
        
        # Get only current and future trips
        current_future_trips = MyTrip.objects.filter(
            user=request.user,
            end_date__gte=today
        ).order_by('start_date')
        
        context = {
            'current_future_trips': current_future_trips,
        }
    else:
        context = {}
    
    return render(request, 'main/homepage.html', context)
