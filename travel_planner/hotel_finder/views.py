from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import HotelSearchForm
from django.conf import settings
import requests
from datetime import datetime

@login_required
def search_hotels(request):
    current_date = datetime.now().date()
    hotels = None
    error_message = None
    search_params = {}

    if request.method == 'POST':
        form = HotelSearchForm(request.POST)

        if form.is_valid():
            search_params = form.cleaned_data

            if search_params['arrival_date'] == search_params['departure_date']:
                error_message = "Check-in and Check-out dates cannot be the same."
            elif search_params['arrival_date'] < current_date or search_params['departure_date'] < current_date:
                error_message = "Dates cannot be in the past."
            else:
                try:
                    headers = {
                        'x-rapidapi-key': settings.RAPID_API_KEY,
                        'x-rapidapi-host': "booking-com15.p.rapidapi.com"
                    }

                    dest_response = requests.get(
                        f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query={search_params['destination']}",
                        headers=headers
                    )
                    dest_data = dest_response.json()

                    if not dest_data.get('data'):
                        error_message = "Destination not found. Please try another location."
                    else:
                        dest_id = dest_data['data'][0]['dest_id']

                        all_hotels = []
                        page = 1
                        max_pages = 7

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
                                checkin_date = search_params['arrival_date']
                                checkout_date = search_params['departure_date']
                                adults = search_params['adults']
                                rooms = search_params['room_qty']

                                hotel['bookingUrl'] = (
                                    f"https://www.booking.com/searchresults.html"
                                    f"?dest_id={dest_id}"
                                    f"&dest_type=city"
                                    f"&checkin={checkin_date}"
                                    f"&checkout={checkout_date}"
                                    f"&group_adults={adults}"
                                    f"&no_rooms={rooms}"
                                    f"&selected_currency=USD"
                                )
                            all_hotels.extend(page_hotels)
                            page += 1

                        if all_hotels:
                            paginator = Paginator(all_hotels, 20)
                            page_number = request.POST.get('page', 1)
                            hotels = paginator.get_page(page_number)
                        else:
                            error_message = "No hotels found for the given search. Please try again."

                except requests.exceptions.RequestException as e:
                    error_message = f"An error occurred: {e}"

        else:
            error_message = "There was an error with your form submission."

    else:
        form = HotelSearchForm()

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