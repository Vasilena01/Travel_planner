import http.client
import json
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests

def get_destination_id(query, headers):
    """Helper function to get destination ID from the API"""
    if not query:
        print("Empty query received")
        return None
        
    try:
        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com", timeout=30)
        
        # URL encode the query parameter
        query = str(query).strip().replace(' ', '%20')
        
        # print(f"Searching for destination: {query}")
        
        conn.request("GET", f"/api/v1/flights/searchDestination?query={query}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        # print(f"API Response for {query}:", data)

        # Make sure to close the connection
        conn.close()

        # Check if data is a list and has items
        if isinstance(data.get('data'), list) and len(data['data']) > 0:
            for item in data['data']:
                # Return the first matching ID
                if item.get('id'):
                    return item['id']
                
        # If no direct ID found, try to construct it from code
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
            # API headers
            headers = {
                'x-rapidapi-key': settings.RAPID_API_KEY,
                'x-rapidapi-host': "booking-com15.p.rapidapi.com"
            }

            # Get form data with validation
            from_location = request.POST.get('from_location', '').strip()
            to_location = request.POST.get('to_location', '').strip()
            departure_date = request.POST.get('departure_date', '').strip()
            return_date = request.POST.get('return_date', '').strip()
            
            if not all([from_location, to_location, departure_date]):
                error_message = "Please fill in all required fields."
                raise ValueError(error_message)
            
            # Validate date format
            date_format = '%Y-%m-%d'
            try:
                # Validate departure date
                datetime.strptime(departure_date, date_format)
                # Validate return date if provided
                if return_date:
                    datetime.strptime(return_date, date_format)
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD format.")

            # Debug print to see exact format being sent to API
            print(f"Departure date being sent: {departure_date}")
            print(f"Return date being sent: {return_date}")

            # Get destination IDs
            from_id = get_destination_id(from_location, headers)
            to_id = get_destination_id(to_location, headers)

            if not from_id or not to_id:
                error_message = "Could not find valid airport codes."
                raise ValueError(error_message)

            # Create a new connection for flight search
            conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com", timeout=30)
            
            # Construct search URL with parameters
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
            
            # Build the query string
            query_string = '&'.join(f"{k}={v}" for k, v in search_params.items() if v)
            search_url = f"/api/v1/flights/searchFlights?{query_string}"

            print(f"Searching with URL: {search_url}")  # Debug print

            # Make the request
            conn.request("GET", search_url, headers=headers)
            res = conn.getresponse()
            print("Response: ", res)
            data = json.loads(res.read().decode("utf-8"))
            print("Flight Offers: ", data)

            # Close the connection
            conn.close()


            if data.get('status') and data.get('data', {}).get('flightOffers'):
                flights = data['data']['flightOffers']
            else:
                error_message = "No flights found for the given search criteria."

        except ValueError as ve:
            error_message = str(ve)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
        finally:
            # Make sure connection is closed if it exists
            if 'conn' in locals():
                conn.close()

    # Render the template with results
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