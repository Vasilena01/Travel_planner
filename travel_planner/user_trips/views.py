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

        # Pexels API configuration
        pexels_api_key = "nkOEfBfnkELjeOzNTNQqhQn80bXrrV5yBMWtgf9y1zWfNzWkxBcaVOZ4"
        headers = {
            "Authorization": pexels_api_key
        }
        
        # Enhanced search query to focus on landmarks and tourist attractions
        search_query = f"{destination} landmarks architecture"
        api_url = f"https://api.pexels.com/v1/search?query={search_query}&per_page=1&orientation=landscape&size=large"
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                image_url = data["photos"][0]["src"]["landscape"]
            else:
                # Fallback search if no results with landmarks
                fallback_search = f"{destination} cityscape skyline"
                fallback_url = f"https://api.pexels.com/v1/search?query={fallback_search}&per_page=1&orientation=landscape&size=large"
                fallback_response = requests.get(fallback_url, headers=headers)
                
                if fallback_response.status_code == 200:
                    fallback_data = fallback_response.json()
                    if fallback_data.get("photos") and len(fallback_data["photos"]) > 0:
                        image_url = fallback_data["photos"][0]["src"]["landscape"]
                    else:
                        image_url = ""
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


@login_required
def list_places(request, trip_id, place_type):
    trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
    
    api_key = '5ae2e3f221c38a28845f05b6323b362c7d14f9c900dce73db4e93df5'
    destination = trip.destination.lower().strip()
    
    try:
        # Get coordinates for the destination
        geoname_url = "https://api.opentripmap.com/0.1/en/places/geoname"
        geoname_params = {
            "name": destination,
            "apikey": api_key
        }
                
        geoname_response = requests.get(geoname_url, params=geoname_params)
        
        if geoname_response.status_code != 200:
            return render(request, 'user_trips/list_places.html', 
                        {'error': f'API Error: {geoname_response.status_code}', 
                         'trip': trip, 
                         'place_type': place_type})
        
        location_data = geoname_response.json()
        
        if not location_data:
            return render(request, 'user_trips/list_places.html', 
                        {'error': f'Location not found: {destination}', 
                         'trip': trip, 
                         'place_type': place_type})
        
        lat = location_data.get('lat')
        lon = location_data.get('lon')
        
        if not lat or not lon:
            return render(request, 'user_trips/list_places.html', 
                        {'error': 'Invalid coordinates received', 
                         'trip': trip, 
                         'place_type': place_type})
        
        # Search for places
        radius = 3000
        kinds = 'museums,historic,architecture,cultural' if place_type == 'attractions' else 'restaurants'
        
        places_url = "https://api.opentripmap.com/0.1/en/places/radius"
        places_params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "kinds": kinds,
            "rate": "7",
            "format": "json",
            "limit": 10,
            "apikey": api_key
        }
        
        places_response = requests.get(places_url, params=places_params)
        
        if places_response.status_code != 200:
            return render(request, 'user_trips/list_places.html', 
                        {'error': f'Places API Error: {places_response.status_code}', 
                         'trip': trip, 
                         'place_type': place_type})
        
        places_data = places_response.json()
        formatted_places = []
        
        for place in places_data:
            xid = place.get('xid')
            if not xid:
                continue
                
            detail_url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
            detail_params = {"apikey": api_key}
            
            detail_response = requests.get(detail_url, params=detail_params)
            if detail_response.status_code == 200:
                place_details = detail_response.json()
                
                if place_details.get('name'):
                    formatted_place = {
                        'name': place_details.get('name', ''),
                        'address': place_details.get('address', {}).get('road', ''),
                        'rating': place.get('rate', 'No rating'),
                        'photos': [place_details.get('preview', {}).get('source', '')] if place_details.get('preview') else [],
                        'description': place_details.get('wikipedia_extracts', {}).get('text', ''),
                        'categories': place_details.get('kinds', '').split(',')
                    }
                    formatted_places.append(formatted_place)
        
        context = {
            'places': formatted_places,
            'trip': trip,
            'place_type': place_type
        }
        return render(request, 'user_trips/list_places.html', context)
        
    except requests.RequestException as e:
        return render(request, 'user_trips/list_places.html', 
                     {'error': f'Network error: {str(e)}', 
                      'trip': trip, 
                      'place_type': place_type})
    except Exception as e:
        return render(request, 'user_trips/list_places.html', 
                     {'error': f'An unexpected error occurred: {str(e)}', 
                      'trip': trip, 
                      'place_type': place_type})