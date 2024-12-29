import requests
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from travel_planner.settings import RAPID_API_KEY

@login_required
def search_hotels(request):
    hotels = None
    error_message = None
    current_date = datetime.now().strftime('%Y-%m-%d')
    search_params = {}  # Store search parameters for pagination

    if request.method == 'POST':
        search_params = {
            'destination': request.POST.get('destination'),
            'arrival_date': request.POST.get('arrival_date'),
            'departure_date': request.POST.get('departure_date'),
            'adults': request.POST.get('adults', 1),
            'children': request.POST.get('children_age', ''),
            'rooms': request.POST.get('room_qty', 1),
        }

        if search_params['arrival_date'] == search_params['departure_date']:
            error_message = "Check-in and Check-out dates cannot be the same."
            return render(request, 'hotel_finder/search_destination.html', 
                        {'error_message': error_message, 'current_date': current_date})

        if search_params['arrival_date'] < current_date or search_params['departure_date'] < current_date:
            error_message = "Dates cannot be in the past."
            return render(request, 'hotel_finder/search_destination.html', {'error_message': error_message, 'current_date': current_date})

        try:
            headers = {
                'x-rapidapi-key': RAPID_API_KEY,
                'x-rapidapi-host': "booking-com15.p.rapidapi.com"
            }

            # Fetch destination ID
            dest_response = requests.get(
                f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query={search_params['destination']}",
                headers=headers
            )
            dest_data = dest_response.json()
            
            if not dest_data.get('data'):
                error_message = "Destination not found. Please try another location."
            else:
                dest_id = dest_data['data'][0]['dest_id']

                # Get all hotels (or as many as reasonable)
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
                            'children_age': search_params['children'],
                            'room_qty': search_params['rooms'],
                            'page_number': page
                        }
                    )
                    hotels_data = hotel_response.json()
                    page_hotels = hotels_data.get('data', {}).get('hotels', [])
                    
                    if not page_hotels:
                        break
                        
                    all_hotels.extend(page_hotels)
                    page += 1

                if all_hotels:
                    # Implement pagination
                    paginator = Paginator(all_hotels, 20)
                    page_number = request.POST.get('page', 1)
                    hotels = paginator.get_page(page_number)
                else:
                    error_message = "No hotels found for the given search. Please try again."

        except requests.exceptions.RequestException as e:
            error_message = f"An error occurred: {e}"

    return render(
        request, 
        'hotel_finder/search_destination.html', 
        {
            'hotels': hotels,
            'error_message': error_message,
            'current_date': current_date,
            'search_params': search_params
        }
    )