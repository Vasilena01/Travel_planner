import json
import os
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

COUNTRIES_JSON_PATH = os.path.join(settings.BASE_DIR, 'countries_data.json')

def fetch_and_store_countries():
    try:
        countries_url = "https://restcountries.com/v3.1/all"
        response = requests.get(countries_url)
        response.raise_for_status()
        countries = response.json()

        with open(COUNTRIES_JSON_PATH, 'w') as f:
            json.dump(countries, f, indent=4)
        return countries
    except Exception as e:
        return []

def load_countries_data():
    if os.path.exists(COUNTRIES_JSON_PATH):
        try:
            with open(COUNTRIES_JSON_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            return []
    else:
        return fetch_and_store_countries()

def get_destinations_by_category(category):
    countries = load_countries_data()
    
    category_filters = {
        'all': lambda country: True,
        'europe': lambda country: country.get('region') == 'Europe',
        'asia': lambda country: country.get('region') == 'Asia',
        'americas': lambda country: country.get('region') == 'Americas',
        'africa': lambda ccountry: country.get('region') == 'Africa',
        'oceania': lambda country: country.get('region') == 'Oceania'
    }
    
    filter_func = category_filters.get(category, lambda country: True)
    filtered_countries = [country for country in countries if filter_func(country)][:27]

    destinations = []
    for country in filtered_countries:
        try:
            headers = {'Authorization': settings.PEXELS_API_KEY}
            pexels_response = requests.get(
                'https://api.pexels.com/v1/search',
                headers=headers,
                params={
                    'query': f"{country['name']['common']} landmark",
                    'per_page': 1
                },
                timeout=5
            )
            
            # Default image URL in case Pexels fails
            image_url = 'https://images.pexels.com/photos/1271619/pexels-photo-1271619.jpeg'
            
            if pexels_response.status_code == 200:
                photo_data = pexels_response.json()
                if photo_data.get('photos') and len(photo_data['photos']) > 0:
                    image_url = photo_data['photos'][0]['src']['large']
            
            destinations.append({
                'name': country['name']['common'],
                'capital': country['capital'][0] if 'capital' in country else 'N/A',
                'region': country['region'],
                'subregion': country.get('subregion', ''),
                'population': country['population'],
                'languages': list(country.get('languages', {}).values()),
                'currencies': list(country.get('currencies', {}).keys()),
                'image_url': image_url,
                'maps_url': country.get('maps', {}).get('googleMaps', ''),
                'flag': country['flags']['png']
            })
        except Exception as e:
            continue
    return destinations

def category_destinations(request, category):
    destinations = get_destinations_by_category(category)
    return JsonResponse({'destinations': destinations}, safe=False)

def get_major_cities(country_name, country_code):
    try:
        response = requests.get(
            'http://api.geonames.org/searchJSON',
            params={
                'q': country_name,
                'country': country_code,
                'featureClass': 'P',  # P stands for populated places
                'orderby': 'population',
                'maxRows': 12,
                'cities': 'cities1000',
                'username': settings.GEONAMES_USERNAME
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return [city['name'] for city in data.get('geonames', [])]
        return []
    except Exception as e:
        return []

def destination_detail(request, destination_name):
    countries = load_countries_data()
    try:
        country_data = next(
            (c for c in countries if c['name']['common'].lower() == destination_name.lower()),
            None
        )
        
        if not country_data:
            return render(request, 'destinations/destination_detail.html', {
                'error_message': f"Sorry, we couldn't find additional information about {destination_name}."
            })
        
        headers = {'Authorization': settings.PEXELS_API_KEY}
        photos_response = requests.get(
            'https://api.pexels.com/v1/search',
            headers=headers,
            params={
                'query': f"{destination_name} travel",
                'per_page': 15
            }
        )
        photos = photos_response.json()['photos']
        
        # Get major cities using GeoNames
        major_city_names = get_major_cities(
            country_data['name']['common'],
            country_data['cca2']
        )
        
        cities = []
        for city in major_city_names:
            try:
                city_response = requests.get(
                    'https://api.pexels.com/v1/search',
                    headers=headers,
                    params={
                        'query': f"{city} {country_data['name']['common']} city",
                        'per_page': 1
                    }
                )
                city_photo = city_response.json()['photos'][0]['src']['large'] if city_response.json()['photos'] else None
                
                cities.append({
                    'name': city,
                    'image_url': city_photo
                })
            except Exception as e:
                continue
        
        context = {
            'destination': {
                'name': country_data['name']['common'],
                'capital': country_data['capital'][0] if 'capital' in country_data else 'N/A',
                'region': country_data['region'],
                'subregion': country_data.get('subregion', ''),
                'population': country_data['population'],
                'languages': list(country_data.get('languages', {}).values()),
                'currencies': list(country_data.get('currencies', {}).keys()),
                'maps_url': country_data.get('maps', {}).get('googleMaps', ''),
                'flag': country_data['flags']['png'],
                'photos': [photo['src']['large'] for photo in photos],
                'major_cities': cities
            }
        }
        
        return render(request, 'destinations/destination_detail.html', context)
    except Exception as e:
        return render(request, 'destinations/destination_detail.html', {
            'error_message': f"Sorry, we couldn't find additional information about {destination_name}."
        })