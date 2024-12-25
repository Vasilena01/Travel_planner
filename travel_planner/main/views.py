from datetime import date, timedelta
from django.shortcuts import render
from user_trips.models import MyTrip

def homepage(request):
    today = date.today()
    in_one_month = today + timedelta(days=30)
    
    upcoming_trips = MyTrip.objects.filter(
        user=request.user,
        start_date__gte=today,
        end_date__lte=in_one_month
    ).order_by('start_date')
    
    return render(request, 'main/homepage.html', {'trips': upcoming_trips})
