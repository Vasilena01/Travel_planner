from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MyTrip

@login_required
def list_trips(request):
    trips = MyTrip.objects.filter(user=request.user)
    return render(request, 'user_trips/list_trips.html', {'trips': trips})

@login_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
    return render(request, 'user_trips/trip_detail.html', {'trip': trip})

@login_required
def create_trip(request):
    if request.method == "POST":
        destination = request.POST['destination']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
    
        if(start_date >= end_date):
            return redirect('list_trips')
        
        MyTrip.objects.create(
            user=request.user,
            destination=destination,
            start_date=start_date,
            end_date=end_date
        )
        
        return redirect('list_trips')