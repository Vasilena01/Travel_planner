from django.shortcuts import render
from user_trips.models import MyTrip

def homepage(request):
    trips = MyTrip.objects.filter(user=request.user)
    return render(request, 'main/homepage.html', {'trips': trips})
