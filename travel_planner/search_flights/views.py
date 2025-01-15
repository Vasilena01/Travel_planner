import http.client
import json
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests
from django.core.paginator import Paginator

def get_destination_id(query, headers):
    """Helper function to get destination ID from the API"""
    if not query:
        print("Empty query received")
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

@login_required
def search_flights(request):
    flights = None
    error_message = None
    current_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            headers = {
                'x-rapidapi-key': settings.RAPID_API_KEY,
                'x-rapidapi-host': "booking-com15.p.rapidapi.com"
            }

            from_location = request.POST.get('from_location', '').strip()
            to_location = request.POST.get('to_location', '').strip()
            departure_date = request.POST.get('departure_date', '').strip()
            return_date = request.POST.get('return_date', '').strip()
            
            if not all([from_location, to_location, departure_date]):
                error_message = "Please fill in all required fields."
                raise ValueError(error_message)
            
            date_format = '%Y-%m-%d'
            try:
                datetime.strptime(departure_date, date_format)
                if return_date:
                    datetime.strptime(return_date, date_format)
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD format.")

            # Get destination IDs
            from_id = get_destination_id(from_location, headers)
            to_id = get_destination_id(to_location, headers)

            if not from_id or not to_id:
                error_message = "Could not find valid airport codes."
                raise ValueError(error_message)

            conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com", timeout=30)
            
            search_params = {
                'fromId': from_id,
                'toId': to_id,
                'departDate': departure_date,
                'returnDate': return_date,
                'adults': request.POST.get('adults', '1'),
                'children': request.POST.get('children', '0'),
                'cabinClass': request.POST.get('cabin_class', 'ECONOMY'),
                'sort': 'BEST'
            }
            
            query_string = '&'.join(f"{k}={v}" for k, v in search_params.items() if v)
            search_url = f"/api/v1/flights/searchFlights?{query_string}"
            conn.request("GET", search_url, headers=headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))

            conn.close()

            if data.get('status') and data.get('data', {}).get('flightOffers'):
                flights = []
                for offer in data['data']['flightOffers']:
                    # Create outbound flight info
                    outbound_flight = {
                        'airline': {
                            'name': offer['segments'][0]['legs'][0]['carriersData'][0]['name'],
                            'logo': offer['segments'][0]['legs'][0]['carriersData'][0]['logo']
                        },
                        'price': {
                            'amount': offer['priceBreakdown']['total']['units'] + 
                                    offer['priceBreakdown']['total']['nanos'] / 1000000000,
                            'currency': offer['priceBreakdown']['total']['currencyCode']
                        },
                        'departure': {
                            'airport': {
                                'code': offer['segments'][0]['departureAirport']['code'],
                                'name': offer['segments'][0]['departureAirport']['name']
                            },
                            'time': datetime.strptime(offer['segments'][0]['departureTime'], "%Y-%m-%dT%H:%M:%S")
                        },
                        'arrival': {
                            'airport': {
                                'code': offer['segments'][0]['arrivalAirport']['code'],
                                'name': offer['segments'][0]['arrivalAirport']['name']
                            },
                            'time': datetime.strptime(offer['segments'][0]['arrivalTime'], "%Y-%m-%dT%H:%M:%S")
                        },
                        'duration': f"{offer['segments'][0]['totalTime'] // 3600}h {(offer['segments'][0]['totalTime'] % 3600) // 60}m",
                        'stops': len(offer['segments'][0]['legs']) - 1,
                        'cabinClass': offer['segments'][0]['legs'][0]['cabinClass'].title(),
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
                        'direction': 'outbound'
                    }
                    flights.append(outbound_flight)

                    # Get return flight data
                    if return_date and len(offer['segments']) > 1:
                        return_flight = {
                            'airline': {
                                'name': offer['segments'][1]['legs'][0]['carriersData'][0]['name'],
                                'logo': offer['segments'][1]['legs'][0]['carriersData'][0]['logo']
                            },
                            'price': {
                                'amount': offer['priceBreakdown']['total']['units'] + 
                                        offer['priceBreakdown']['total']['nanos'] / 1000000000,
                                'currency': offer['priceBreakdown']['total']['currencyCode']
                            },
                            'departure': {
                                'airport': {
                                    'code': offer['segments'][1]['departureAirport']['code'],
                                    'name': offer['segments'][1]['departureAirport']['name']
                                },
                                'time': datetime.strptime(offer['segments'][1]['departureTime'], "%Y-%m-%dT%H:%M:%S")
                            },
                            'arrival': {
                                'airport': {
                                    'code': offer['segments'][1]['arrivalAirport']['code'],
                                    'name': offer['segments'][1]['arrivalAirport']['name']
                                },
                                'time': datetime.strptime(offer['segments'][1]['arrivalTime'], "%Y-%m-%dT%H:%M:%S")
                            },
                            'duration': f"{offer['segments'][1]['totalTime'] // 3600}h {(offer['segments'][1]['totalTime'] % 3600) // 60}m",
                            'stops': len(offer['segments'][1]['legs']) - 1,
                            'cabinClass': offer['segments'][1]['legs'][0]['cabinClass'].title(),
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
                            'direction': 'return'
                        }
                        flights.append(return_flight)

                if flights:
                    flight_pairs = []
                    outbound_flights = []
                    return_flights = []
                    
                    for flight in flights:
                        if flight['direction'] == 'outbound':
                            outbound_flights.append(flight)
                        else:
                            return_flights.append(flight)
                    
                    # Sort flights by price
                    outbound_flights.sort(key=lambda x: x['price']['amount'])
                    return_flights.sort(key=lambda x: x['price']['amount'])

                    flights = outbound_flights + return_flights

                    if outbound_flights:
                        prices = [f['price']['amount'] for f in outbound_flights]
                        durations = [int(''.join(filter(str.isdigit, f['duration']))) for f in outbound_flights]
                        min_price = min(prices)
                        min_duration = min(durations)
                        avg_price = sum(prices) / len(prices)

                        for flight in outbound_flights:
                            flight['tags'] = []
                            current_duration = int(''.join(filter(str.isdigit, flight['duration'])))
                            
                            if flight['price']['amount'] == min_price:
                                flight['tags'].append({'type': 'cheapest', 'text': 'Cheapest'})
                            
                            if current_duration == min_duration:
                                flight['tags'].append({'type': 'fastest', 'text': 'Fastest'})
                            
                            price_ratio = flight['price']['amount'] / avg_price
                            duration_ratio = current_duration / min_duration
                            if price_ratio + duration_ratio <= 2.2:
                                flight['tags'].append({'type': 'best', 'text': 'Best'})
                            
                            if flight['stops'] == 0:
                                flight['tags'].append({'type': 'direct', 'text': 'Direct'})

                    # Add tags to return flights
                    if return_flights:
                        prices = [f['price']['amount'] for f in return_flights]
                        durations = [int(''.join(filter(str.isdigit, f['duration']))) for f in return_flights]
                        min_price = min(prices)
                        min_duration = min(durations)
                        avg_price = sum(prices) / len(prices)

                        for flight in return_flights:
                            flight['tags'] = []
                            current_duration = int(''.join(filter(str.isdigit, flight['duration'])))
                            
                            if flight['price']['amount'] == min_price:
                                flight['tags'].append({'type': 'cheapest', 'text': 'Cheapest'})
                            
                            if current_duration == min_duration:
                                flight['tags'].append({'type': 'fastest', 'text': 'Fastest'})
                            
                            price_ratio = flight['price']['amount'] / avg_price
                            duration_ratio = current_duration / min_duration
                            if price_ratio + duration_ratio <= 2.2:
                                flight['tags'].append({'type': 'best', 'text': 'Best'})
                            
                            if flight['stops'] == 0:
                                flight['tags'].append({'type': 'direct', 'text': 'Direct'})

                    for outbound in outbound_flights:
                        matching_return = next((rf for rf in return_flights 
                                             if rf['departure']['airport']['code'] == outbound['arrival']['airport']['code']), 
                                            None)
                        if matching_return:
                            flight_pairs.append({
                                'outbound': outbound,
                                'return': matching_return
                            })

                    flights = flight_pairs

                context = {
                    'flights': flights,
                    'form': request.POST
                }
            else:
                error_message = "No flights found for the given search criteria."

        except ValueError as ve:
            error_message = str(ve)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

    return render(
        request,
        'search_flights/search_flights.html',
        {
            'flights': flights,
            'error_message': error_message,
            'current_date': current_date,
            'search_params': request.POST if request.method == 'POST' else {}
        }
    )