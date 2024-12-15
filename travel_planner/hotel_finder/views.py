from datetime import datetime
from django.shortcuts import render
import http.client
import json

def search_hotels(request):
    hotels = None
    error_message = None
    current_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        destination = request.POST.get('destination')
        arrival_date = request.POST.get('arrival_date')
        departure_date = request.POST.get('departure_date')
        adults = request.POST.get('adults', 1)
        children = request.POST.get('children_age', '') 
        rooms = request.POST.get('room_qty', 1)
        page_number = request.POST.get('page_number', 1)

        if arrival_date == departure_date:
            error_message = "Check-in and Check-out dates cannot be the same."
            return render(request, 'hotel_finder/search_destination.html', {'error_message': error_message, 'current_date': current_date})

        if arrival_date < current_date or departure_date < current_date:
            error_message = "Dates cannot be in the past."
            return render(request, 'hotel_finder/search_destination.html', {'error_message': error_message, 'current_date': current_date})

        # Fetch destination ID
        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "25aa21455dmsh86b46541b28213bp1489a5jsn374b2d97cd64",
            'x-rapidapi-host': "booking-com15.p.rapidapi.com"
        }
        conn.request("GET", f"/api/v1/hotels/searchDestination?query={destination}", headers=headers)
        res = conn.getresponse()
        dest_data = json.loads(res.read().decode("utf-8"))
        
        if not dest_data['data']:
            error_message = "Destination not found. Please try another location."
        else:
            dest_id = dest_data['data'][0]['dest_id']

            # Fetch hotels for the destination
            url = (
                f"/api/v1/hotels/searchHotels?dest_id={dest_id}&search_type=city"
                f"&arrival_date={arrival_date}&departure_date={departure_date}"
            )
            conn.request("GET", url, headers=headers)
            res = conn.getresponse()
            hotels_data = json.loads(res.read().decode("utf-8"))
            hotels = hotels_data['data']['hotels'] if 'hotels' in hotels_data['data'] else None

            if not hotels:
                error_message = "No hotels found for the given search. Please try again."

    return render(
        request, 
        'hotel_finder/search_destination.html', 
        {'hotels': hotels, 'error_message': error_message, 'current_date': current_date}
    )