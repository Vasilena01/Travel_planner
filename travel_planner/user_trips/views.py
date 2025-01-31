import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MyTrip, TripDay
from geopy.geocoders import Nominatim
from django.http import JsonResponse
from urllib.parse import unquote
from django.conf import settings
from datetime import date, timedelta
import math
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models

@login_required
def list_trips(request):
    today = date.today()
    
    # Get both owned and shared current/future trips
    current_future_trips = MyTrip.objects.filter(
        models.Q(user=request.user) | models.Q(shared_with=request.user),
        end_date__gte=today
    ).order_by('start_date')
    
    # Get both owned and shared past trips
    past_trips = MyTrip.objects.filter(
        models.Q(user=request.user) | models.Q(shared_with=request.user),
        end_date__lt=today
    ).order_by('-end_date')

    shared_current_future = MyTrip.objects.filter(
        shared_with=request.user,
        end_date__gte=today
    ).order_by('start_date')
    
    context = {
        'current_future_trips': current_future_trips,
        'past_trips': past_trips,
        'shared_current_future': shared_current_future,
    }
    
    return render(request, 'user_trips/list_trips.html', context)


@login_required
def trip_detail(request, trip_id):
    # Check if user is either the owner or a collaborator of the trip
    trip = get_object_or_404(
        MyTrip, 
        models.Q(id=trip_id) & (
            models.Q(user=request.user) | 
            models.Q(shared_with=request.user)
        )
    )
    
    trip.generate_trip_days()
    
    # Get all days for this trip
    trip_days = trip.days.all()

    # Get all users except current user and existing collaborators
    available_users = User.objects.exclude(
        models.Q(id=request.user.id) | 
        models.Q(id__in=trip.collaborators.all())
    )
    
    context = {
        'trip': trip,
        'trip_days': trip_days,
        'available_users': available_users,
    }
    
    return render(request, 'user_trips/trip_detail.html', context)


@login_required
def create_trip(request):
    if request.method == "POST":
        destination = request.POST['destination']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        if (start_date >= end_date):
            return redirect('list_trips')

        # Pexels API configuration
        headers = {'Authorization': settings.PEXELS_API_KEY}
        
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
    client_id = settings.FOURSQUARE_API_KEY
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
            "limit": 50,
            "radius": 3000,
            "sort": "RATING",
            "fields": "name,rating,stats,location,photos,description,tel,website"
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
            
            rating = place.get('rating', 0)
            vote_count = place.get('stats', {}).get('ratings', 0)
            
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
                'rating': f"{rating}/10" if rating else 'No rating',
                'raw_rating': rating or 0,  # Store raw rating for sorting
                'vote_count': vote_count,
                'photo_url': photo_url,
                'description': place.get('description', 'No description available'),
                'website': place.get('website', ''),
                'tel': place.get('tel', '')
            }
            formatted_places.append(formatted_place)
        
        # Sort places by rating * vote_count to prioritize highly-rated places with more votes
        def get_weighted_rating(place):
            try:
                rating = place['raw_rating']
                votes = place['vote_count'] or 0
                return rating * (votes + 1)
            except (ValueError, KeyError):
                return 0
        
        formatted_places.sort(key=get_weighted_rating, reverse=True)
        
        for i, place in enumerate(formatted_places):
            place['display_rating'] = f"{place['rating']} ({place['vote_count']} votes)"
        
        # Page Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(formatted_places, 10)
        page_obj = paginator.get_page(page_number)
        
        max_pages = 5
        current_page = page_obj.number
        total_pages = paginator.num_pages

        if total_pages <= max_pages:
            page_range = range(1, total_pages + 1)
        else:
            start_page = max(1, current_page - 2)
            end_page = min(total_pages, start_page + max_pages - 1)
            
            if end_page - start_page < max_pages - 1:
                start_page = max(1, end_page - max_pages + 1)
            
            page_range = range(start_page, end_page + 1)

        context = {
            'places': page_obj,
            'trip': trip,
            'place_type': place_type,
            'page_range': page_range,
            'total_pages': total_pages,
            'current_page': current_page
        }
        
        return render(request, 'user_trips/list_places.html', context)
        
    except Exception as e:
        print(f"Error in list_places: {str(e)}")
        return render(request, 'user_trips/list_places.html',
                     {'error': f'An error occurred: {str(e)}',
                      'trip': trip,
                      'place_type': place_type})
    

@login_required
def add_place_to_trip(request, trip_id):
    trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
    place_name = request.GET.get('name')
    place_address = request.GET.get('address')
    place_type = request.GET.get('type')

    place_data = {
        'name': place_name,
        'address': place_address
    }

    if place_type == 'attractions':
        if not any(place['name'] == place_name for place in trip.attractions):
            trip.attractions.append(place_data)
    else:
        if not any(place['name'] == place_name for place in trip.restaurants):
            trip.restaurants.append(place_data)
    
    trip.save()
    return redirect('trip_detail', trip_id=trip.id)

@login_required
def delete_place_from_trip(request, trip_id, place_type, place_name):
    try:
        decoded_name = unquote(place_name)
        trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
        
        if place_type == 'attractions':
            trip.attractions = [place for place in trip.attractions 
                              if place.get('name') != decoded_name]
        else:
            trip.restaurants = [place for place in trip.restaurants 
                              if place.get('name') != decoded_name]
        
        trip.save()
        
        return redirect('trip_detail', trip_id=trip_id)
    except Exception as e:
        print(f"Error deleting place: {e}")
        return redirect('trip_detail', trip_id=trip_id)

@login_required
def add_place_to_day(request, trip_id, day_id):
    if request.method == 'POST':
        trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
        trip_day = get_object_or_404(TripDay, id=day_id, trip=trip)
        
        place_name = request.POST.get('place_name')
        place_type = request.POST.get('place_type')
        
        # Get the correct list based on place_type
        place_list = trip.attractions if place_type == 'attractions' else trip.restaurants
        
        # Find the place in the corresponding list
        place_details = next((place for place in place_list if place['name'] == place_name), None)
        
        if place_details:
            if not trip_day.places:
                trip_day.places = []
            else:
                for place in trip_day.places:
                    if place['name'] == place_name:
                        return redirect('trip_detail', trip_id=trip_id)
                
            trip_day.places.append({
                'name': place_details['name'],
                'address': place_details['address'],
                'type': place_type
            })
            trip_day.save()
            
    return redirect('trip_detail', trip_id=trip_id)

@login_required
def delete_place_from_day(request, trip_id, day_id, place_index):
    trip = get_object_or_404(MyTrip, id=trip_id, user=request.user)
    trip_day = get_object_or_404(TripDay, id=day_id, trip=trip)
    
    if 0 <= place_index < len(trip_day.places):
        trip_day.places.pop(place_index)
        trip_day.save()
    
    return redirect('trip_detail', trip_id=trip_id)

@login_required
def add_collaborator(request, trip_id):
    if request.method == 'POST':
        trip = get_object_or_404(MyTrip, id=trip_id)
        collaborator_id = request.POST.get('collaborator')
        
        if collaborator_id:
            collaborator = get_object_or_404(User, id=collaborator_id)
            if collaborator not in trip.collaborators.all():
                # Add as collaborator
                trip.collaborators.add(collaborator)
                # Add trip to collaborator's trips list
                trip.shared_with.add(collaborator)
                messages.success(request, f'{collaborator.username} has been added as a collaborator.')
            else:
                messages.warning(request, 'This user is already a collaborator.')
        
        return redirect('trip_detail', trip_id=trip_id)

@login_required
def remove_from_shared(request, trip_id):
    if request.method == 'POST':
        trip = get_object_or_404(MyTrip, id=trip_id)
        if request.user in trip.shared_with.all():
            trip.shared_with.remove(request.user)
            trip.collaborators.remove(request.user)
            messages.success(request, 'You have been removed from the shared trip.')
        else:
            messages.error(request, 'You are not a collaborator of this trip.')
    
    next_url = request.GET.get('next', 'list_trips')
    return redirect(next_url)