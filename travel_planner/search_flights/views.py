from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import FlightSearchForm
import http.client
import json
from datetime import datetime

def get_destination_id(query, headers):
    """Helper function to get destination ID from the API"""
    if not query:
        return None
        
    try:
        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com", timeout=30)
        query = str(query).strip().replace(' ', '%20')
        conn.request("GET", f"/api/v1/flights/searchDestination?query={query}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        conn.close()

        if isinstance(data.get('data'), list) and len(data['data']) > 0:
            for item in data['data']:
                if item.get('id'):
                    return item['id']
                
        if isinstance(data.get('data'), list) and len(data['data']) > 0:
            item = data['data'][0]
            if item.get('type') == 'CITY' and item.get('code'):
                return f"{item['code']}.CITY"
            elif item.get('type') == 'AIRPORT' and item.get('code'):
                return f"{item['code']}.AIRPORT"
        
        return None
    except Exception as e:
        print(f"Error in get_destination_id: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return None

def validate_dates(departure_date_str, return_date_str, current_date):
    """Validate that the dates are not in the past."""
    if departure_date_str < current_date or (return_date_str and return_date_str < current_date):
        return "Dates cannot be in the past."
    return None

def fetch_flight_offers(search_params, headers):
    """Fetch flight offers from the API."""
    conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com", timeout=30)
    query_string = '&'.join(f"{k}={v}" for k, v in search_params.items() if v)
    search_url = f"/api/v1/flights/searchFlights?{query_string}"
    conn.request("GET", search_url, headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    conn.close()
    return data

def process_flight_offer(segment, offer, from_id, to_id, direction):
    """Process a single flight offer."""
    flight = {
        'airline': {
            'name': segment['legs'][0]['carriersData'][0]['name'],
            'logo': segment['legs'][0]['carriersData'][0]['logo']
        },
        'price': {
            'amount': offer['priceBreakdown']['total']['units'] + 
                      offer['priceBreakdown']['total']['nanos'] / 1000000000,
            'currency': offer['priceBreakdown']['total']['currencyCode']
        },
        'departure': {
            'airport': {
                'code': segment['departureAirport']['code'],
                'name': segment['departureAirport']['name']
            },
            'time': datetime.strptime(segment['departureTime'], "%Y-%m-%dT%H:%M:%S")
        },
        'arrival': {
            'airport': {
                'code': segment['arrivalAirport']['code'],
                'name': segment['arrivalAirport']['name']
            },
            'time': datetime.strptime(segment['arrivalTime'], "%Y-%m-%dT%H:%M:%S")
        },
        'duration': f"{segment['totalTime'] // 3600}h {(segment['totalTime'] % 3600) // 60}m",
        'stops': len(segment['legs']) - 1,
        'cabinClass': segment['legs'][0]['cabinClass'].title(),
        'bookingLink': (
            f"https://www.booking.com/flights/details.html"
            f"?aid=304142"
            f"&label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYAQm4ARfIAQzYAQHoAQH4AQKIAgGoAgO4AqWs7a0GwAIB"
            f"&sid=null"
            f"&token={offer['token']}"
            f"&fromId={from_id}"
            f"&toId={to_id}"
            f"&source=search_form"
        ),
        'direction': direction
    }
    return flight

def add_tags_to_flights(flights):
    """Add tags for cheapest and fastest flights."""
    if flights:
        min_price = min(f['price']['amount'] for f in flights)
        min_duration = min(
            int(f['duration'].split('h')[0]) * 60 + int(f['duration'].split('h')[1].split('m')[0]) 
            for f in flights
        )

        for flight in flights:
            flight['tags'] = []
            if flight['price']['amount'] == min_price:
                flight['tags'].append({'type': 'best-deal', 'text': 'Best Deal'})
                
            flight_duration = int(flight['duration'].split('h')[0]) * 60 + int(flight['duration'].split('h')[1].split('m')[0])
            if flight_duration == min_duration:
                flight['tags'].append({'type': 'fastest', 'text': 'Fastest'})

@login_required
def search_flights(request):
    """View for searching flights."""
    current_date = datetime.now().strftime('%Y-%m-%d')
    flights = None
    error_message = None
    form = FlightSearchForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        departure_date_str = form.cleaned_data['departure_date'].strftime('%Y-%m-%d')
        return_date_str = form.cleaned_data.get('return_date').strftime('%Y-%m-%d') if form.cleaned_data.get('return_date') else None

        error_message = validate_dates(departure_date_str, return_date_str, current_date)
        if not error_message:
            try:
                from_location = form.cleaned_data['from_location']
                to_location = form.cleaned_data['to_location']
                adults = form.cleaned_data['adults']
                children = form.cleaned_data['children']
                cabin_class = form.cleaned_data['cabin_class']

                headers = {
                    'x-rapidapi-key': settings.RAPID_API_KEY,
                    'x-rapidapi-host': "booking-com15.p.rapidapi.com"
                }

                from_id = get_destination_id(from_location, headers)
                to_id = get_destination_id(to_location, headers)

                if not from_id or not to_id:
                    error_message = "Could not find valid airport codes."
                    raise ValueError(error_message)

                search_params = {
                    'fromId': from_id,
                    'toId': to_id,
                    'departDate': departure_date_str,
                    'returnDate': return_date_str,
                    'adults': adults,
                    'children': children,
                    'cabinClass': cabin_class,
                    'sort': 'BEST'
                }

                data = fetch_flight_offers(search_params, headers)

                if data.get('status') and data.get('data', {}).get('flightOffers'):
                    outbound_flights = []
                    return_flights = []

                    for offer in data['data']['flightOffers']:
                        outbound_flight = process_flight_offer(offer['segments'][0], offer, from_id, to_id, 'outbound')
                        outbound_flights.append(outbound_flight)

                        if return_date_str and len(offer['segments']) > 1:
                            return_flight = process_flight_offer(offer['segments'][1], offer, to_id, from_id, 'return')
                            return_flights.append(return_flight)

                    add_tags_to_flights(outbound_flights)
                    add_tags_to_flights(return_flights)

                    paired_flights = list(zip(outbound_flights, return_flights))
                    flights = [{'outbound': out, 'return': ret} for out, ret in paired_flights]
                else:
                    error_message = "No flights found for the given search."
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
    elif request.method == 'POST':
        error_message = "Form is invalid. Please check the inputs."

    return render(
        request,
        'search_flights/search_flights.html',
        {
            'flights': flights,
            'error_message': error_message,
            'current_date': current_date,
            'form': form
        }
    )