from django.shortcuts import render
import http.client
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def search_destination_page(request):
    return render(request, 'hotel_finder/search_destination.html')


@csrf_exempt
def search_destination(request):
    if request.method == 'POST':
        destination = request.POST.get('destination')
        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "25aa21455dmsh86b46541b28213bp1489a5jsn374b2d97cd64",
            'x-rapidapi-host': "booking-com15.p.rapidapi.com"
        }
        conn.request(
            "GET", f"/api/v1/hotels/searchDestination?query={destination}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        return JsonResponse({'destinations': data['data']})


@csrf_exempt
def search_hotels(request):
    if request.method == 'POST':
        dest_id = request.POST.get('dest_id')
        search_type = request.POST.get('search_type', 'city')
        arrival_date = request.POST.get('arrival_date')
        departure_date = request.POST.get('departure_date')
        adults = request.POST.get('adults', 1)
        children_age = request.POST.get('children_age', '')
        room_qty = request.POST.get('room_qty', 1)
        page_number = request.POST.get('page_number', 1)

        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "25aa21455dmsh86b46541b28213bp1489a5jsn374b2d97cd64",
            'x-rapidapi-host': "booking-com15.p.rapidapi.com"
        }
        url = (
            f"/api/v1/hotels/searchHotels?dest_id={dest_id}&search_type={search_type}"
            f"&arrival_date={arrival_date}&departure_date={departure_date}&adults={adults}"
            f"&children_age={children_age}&room_qty={room_qty}&page_number={page_number}"
        )

        try:
            conn.request("GET", url, headers=headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))

            if 'hotels' in data['data']:
                return JsonResponse({'hotels': data['data']['hotels']})
            else:
                return JsonResponse({'error': 'No hotels found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)