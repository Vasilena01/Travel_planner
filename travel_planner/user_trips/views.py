import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MyTrip
from geopy.geocoders import Nominatim
from django.http import JsonResponse


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
    
    # Foursquare API configuration
    client_id = 'fsq3FidKW0IcrRsQ5wut/tyyuTkCREEV/ez9oR4Xx5Luajs='
    destination = trip.destination.strip()
    
    try:
        # Get coordinates using Nominatim
        geolocator = Nominatim(user_agent="my_travel_planner")
        location = geolocator.geocode(destination)
        
        if not location:
            return render(request, 'user_trips/list_places.html',
                        {'error': f'Location not found: {destination}',
                         'trip': trip,
                         'place_type': place_type})
        
        url = "https://api.foursquare.com/v3/places/search"
        
        # Define category IDs based on place_type
        if place_type == 'attractions':
            categories = "16000,10000,10027,10028,10025"  # landmarks, arts, museums
        else:
            categories = "13065"  # restaurants
        
        headers = {
            "accept": "application/json",
            "Authorization": client_id
        }
        
        params = {
            "ll": f"{location.latitude},{location.longitude}",
            "categories": categories,
            "limit": 15,
            "radius": 3000,
            "sort": "RATING",
            "fields": "name,rating,location,photos,description,tel,website"  # Specify fields we want
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return render(request, 'user_trips/list_places.html',
                        {'error': f'API Error: {response.status_code}',
                         'trip': trip,
                         'place_type': place_type})
        
        data = response.json()
        formatted_places = []
        
        for place in data.get('results', []):
            photos = place.get('photos', [])
            photo_url = None
            if photos:
                photo = photos[0]
                photo_url = f"{photo['prefix']}original{photo['suffix']}"
            
            # Format the address properly
            location_info = place.get('location', {})
            address_parts = [
                location_info.get('address'),
                location_info.get('locality'),
                location_info.get('region'),
            ]
            address = ', '.join(part for part in address_parts if part)
            
            formatted_place = {
                'name': place.get('name', ''),
                'address': address,
                'rating': f"{place.get('rating', 'No rating')}/10" if place.get('rating') else 'No rating',
                'photo_url': photo_url,
                'description': place.get('description', 'No description available'),
                'website': place.get('website', ''),
                'tel': place.get('tel', '')
            }
            formatted_places.append(formatted_place)
        
        # Sort places by rating (highest first)
        formatted_places.sort(key=lambda x: float(x['rating'].split('/')[0]) if x['rating'] != 'No rating' else 0, reverse=True)
        
        context = {
            'places': formatted_places[:15],  # Ensure that the app only shows top 15
            'trip': trip,
            'place_type': place_type
        }
        return render(request, 'user_trips/list_places.html', context)
        
    except Exception as e:
        print(f"Error in list_places: {str(e)}")  # Debug print
        return render(request, 'user_trips/list_places.html',
                     {'error': f'An error occurred: {str(e)}',
                      'trip': trip,
                      'place_type': place_type})
    

@login_required
def add_place_to_trip(request, trip_id):
    if request.method == 'POST':
        trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
        place_name = request.POST.get('name')
        place_type = request.POST.get('place_type')
        website = request.POST.get('website', '')

        if place_type == 'attractions':
            if place_name not in trip.attractions:
                trip.attractions.append({'name': place_name, 'website': website})
                trip.save()
        else:
            if place_name not in trip.restaurants:
                trip.restaurants.append({'name': place_name, 'website': website})
                trip.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)