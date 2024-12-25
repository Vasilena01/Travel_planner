import requests
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

        if (start_date >= end_date):
            return redirect('list_trips')

        api_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
        headers = {
            "x-rapidapi-key": "25aa21455dmsh86b46541b28213bp1489a5jsn374b2d97cd64",
            "x-rapidapi-host": "booking-com15.p.rapidapi.com",
        }
        params = {"query": destination}
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") and data.get("data"):
                image_url = data["data"][0].get("image_url", "")
            else:
                image_url = ""
        else:
            image_url = ""
            
        MyTrip.objects.create(
            user=request.user,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            image_url=image_url
        )

        next_url = request.GET.get('next', 'list_trips')
        return redirect(next_url)
    
@login_required
def delete_trip(request, trip_id):
    trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
    trip.delete()
    
    next_url = request.GET.get('next', 'list_trips')
    return redirect(next_url)
