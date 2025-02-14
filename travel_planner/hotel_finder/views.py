from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import HotelSearchForm
from django.conf import settings
import requests
from datetime import datetime

def validate_search_form(form, current_date):
    if form.is_valid():
        search_params = form.cleaned_data
        arrival, departure = search_params['arrival_date'], search_params['departure_date']

        if arrival == departure:
            return False, "Check-in and Check-out dates cannot be the same.", search_params
        if arrival < current_date or departure < current_date:
            return False, "Dates cannot be in the past.", search_params

        return True, None, search_params
    return False, "Invalid form submission.", {}


def fetch_destination_id(destination, headers):
    dest_response = requests.get(
        f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query={destination}",
        headers=headers
    )
    dest_data = dest_response.json()

    if not dest_data.get('data'):
        return None, "Destination not found. Please try another location."
    
    return dest_data['data'][0]['dest_id'], None

def generate_booking_url(dest_id, search_params):
    return (
        f"https://www.booking.com/searchresults.html"
        f"?dest_id={dest_id}"
        f"&dest_type=city"
        f"&checkin={search_params['arrival_date']}"
        f"&checkout={search_params['departure_date']}"
        f"&group_adults={search_params['adults']}"
        f"&no_rooms={search_params['room_qty']}"
        f"&selected_currency=USD"
    )
    
def fetch_hotels_for_destination(dest_id, search_params, headers):
    all_hotels = []
    page, max_pages = 1, 7

    while page <= max_pages:
        hotel_response = requests.get(
            "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels",
            headers=headers,
            params={
                'dest_id': dest_id,
                'search_type': 'city',
                'arrival_date': search_params['arrival_date'],
                'departure_date': search_params['departure_date'],
                'adults': search_params['adults'],
                'children_age': search_params['children_age'],
                'room_qty': search_params['room_qty'],
                'page_number': page
            }
        )
        hotels_data = hotel_response.json()
        page_hotels = hotels_data.get('data', {}).get('hotels', [])

        if not page_hotels:
            break

        for hotel in page_hotels:
            hotel['bookingUrl'] = generate_booking_url(dest_id, search_params)
        all_hotels.extend(page_hotels)
        page += 1

    return all_hotels

def render_error(request, error_message, form, search_params, current_date, hotels=None):
    return render(
        request,
        'hotel_finder/search_destination.html',
        {
            'hotels': hotels,
            'error_message': error_message,
            'current_date': current_date,
            'search_params': search_params,
            'form': form
        }
    )
    
@login_required
def search_hotels(request):
    current_date = datetime.now().date()
    hotels, error_message, search_params = None, None, {}

    if request.method == 'POST':
        form = HotelSearchForm(request.POST)
        is_valid, error_message, search_params = validate_search_form(form, current_date)

        if is_valid:
            try:
                headers = {
                    'x-rapidapi-key': settings.RAPID_API_KEY,
                    'x-rapidapi-host': "booking-com15.p.rapidapi.com"
                }
                
                dest_id, error_message = fetch_destination_id(search_params['destination'], headers)
                if not dest_id:
                    return render_error(request, error_message, form, search_params, current_date)

                all_hotels = fetch_hotels_for_destination(dest_id, search_params, headers)

                if all_hotels:
                    paginator = Paginator(all_hotels, 20)
                    page_number = request.POST.get('page', 1)
                    hotels = paginator.get_page(page_number)
                else:
                    error_message = "No hotels found for the given search. Please try again."

            except requests.exceptions.RequestException as e:
                error_message = f"An error occurred: {e}"
        else:
            return render_error(request, error_message, form, search_params, current_date, hotels)    
    else:
        form = HotelSearchForm()

    return render_error(request, error_message, form, search_params, current_date, hotels)