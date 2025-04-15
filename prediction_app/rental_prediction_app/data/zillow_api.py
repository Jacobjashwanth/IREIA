# data/zillow_api.py

import requests
import json
import time
import random
import os
from datetime import datetime

def fetch_rental_listings(latitude, longitude, radius=10, max_results=50):
    """
    Fetch rental listings from Zillow API based on location.
    
    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius: Search radius in miles
        max_results: Maximum number of results to return
        
    Returns:
        list: Rental property listings
    """
    from flask import current_app
    
    # Try to use the Zillow API if key is provided
    api_key = current_app.config.get('ZILLOW_API_KEY')
    
    if api_key and api_key != 'YOUR_ZILLOW_API_KEY':
        try:
            # Define the API endpoint
            url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
            
            # Define the query parameters
            querystring = {
                "location": f"{latitude},{longitude}",
                "status": "forRent",
                "radius": str(radius),
                "sort": "days",
                "home_type": "Houses,Apartments,Condos"
            }
            
            # Define the headers
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": current_app.config.get('ZILLOW_API_HOST')
            }
            
            # Make the request
            response = requests.get(url, headers=headers, params=querystring)
            
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Check if 'props' is in the response
                if 'props' in data and data['props']:
                    # Process the properties
                    listings = []
                    
                    for prop in data['props'][:max_results]:
                        # Extract required information
                        listing = {
                            'zpid': prop.get('zpid'),
                            'address': prop.get('address'),
                            'price': prop.get('price'),
                            'rentZestimate': prop.get('rentZestimate'),
                            'bedrooms': prop.get('bedrooms'),
                            'bathrooms': prop.get('bathrooms'),
                            'livingArea': prop.get('livingArea'),
                            'latitude': prop.get('latitude'),
                            'longitude': prop.get('longitude'),
                            'propertyType': prop.get('propertyType', 'UNKNOWN'),
                            'imgSrc': prop.get('imgSrc')
                        }
                        
                        listings.append(listing)
                    
                    return listings
                else:
                    print("No properties found in the API response")
            else:
                print(f"API request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
        
        except Exception as e:
            print(f"Error fetching data from Zillow API: {e}")
    
    # If we reach here, either the API key is not provided, or the API call failed
    # Generate sample data for demonstration
    print("Generating sample rental listings data")
    return generate_sample_listings(latitude, longitude, max_results)

def generate_sample_listings(latitude, longitude, count=15):
    """Generate sample rental listings when API is unavailable"""
    # Property types with their probabilities
    property_types = [
        ('SINGLE_FAMILY', 0.4),
        ('CONDO', 0.35),
        ('MULTI_FAMILY', 0.1),
        ('TOWNHOUSE', 0.1),
        ('MANUFACTURED', 0.05)
    ]
    
    # Boston neighborhoods with their approximate coordinates
    neighborhoods = [
        ('Downtown Boston', 42.3601, -71.0589),
        ('Back Bay', 42.3503, -71.0810),
        ('South End', 42.3388, -71.0765),
        ('North End', 42.3647, -71.0542),
        ('Beacon Hill', 42.3588, -71.0707),
        ('Fenway', 42.3429, -71.1003),
        ('Cambridge', 42.3736, -71.1097),
        ('Somerville', 42.3876, -71.0995),
        ('Brookline', 42.3318, -71.1212),
        ('Jamaica Plain', 42.3097, -71.1151),
        ('Allston', 42.3539, -71.1337),
        ('Brighton', 42.3464, -71.1627),
        ('Charlestown', 42.3782, -71.0602)
    ]
    
    # Calculate distance from input coordinates to each neighborhood
    neighborhoods_with_distance = []
    for name, lat, lng in neighborhoods:
        dist = ((latitude - lat) ** 2 + (longitude - lng) ** 2) ** 0.5
        neighborhoods_with_distance.append((name, lat, lng, dist))
    
    # Sort by distance
    neighborhoods_with_distance.sort(key=lambda x: x[3])
    
    # Select closest neighborhoods
    closest_neighborhoods = neighborhoods_with_distance[:5]
    
    # Generate random listings
    listings = []
    
    for i in range(count):
        # Select a random neighborhood with emphasis on closer ones
        weights = [1.0/(idx+1) for idx in range(len(closest_neighborhoods))]
        total_weight = sum(weights)
        normalized_weights = [w/total_weight for w in weights]
        neighborhood_idx = random.choices(range(len(closest_neighborhoods)), weights=normalized_weights)[0]
        neighborhood, n_lat, n_lng, _ = closest_neighborhoods[neighborhood_idx]
        
        # Add some randomness to the coordinates
        lat = n_lat + random.uniform(-0.01, 0.01)
        lng = n_lng + random.uniform(-0.01, 0.01)
        
        # Select property type
        prop_type = random.choices([pt[0] for pt in property_types], weights=[pt[1] for pt in property_types])[0]
        
        # Determine bedrooms based on property type
        if prop_type == 'CONDO':
            bedrooms = random.choices([0, 1, 2, 3], weights=[0.1, 0.4, 0.4, 0.1])[0]
        elif prop_type == 'SINGLE_FAMILY':
            bedrooms = random.choices([2, 3, 4, 5], weights=[0.2, 0.4, 0.3, 0.1])[0]
        else:
            bedrooms = random.choices([1, 2, 3, 4], weights=[0.2, 0.4, 0.3, 0.1])[0]
            
        # Determine bathrooms based on bedrooms
        if bedrooms == 0:  # Studio
            bathrooms = 1.0
        elif bedrooms == 1:
            bathrooms = random.choices([1.0, 1.5], weights=[0.8, 0.2])[0]
        elif bedrooms == 2:
            bathrooms = random.choices([1.0, 1.5, 2.0], weights=[0.3, 0.5, 0.2])[0]
        elif bedrooms == 3:
            bathrooms = random.choices([1.5, 2.0, 2.5], weights=[0.2, 0.5, 0.3])[0]
        else:
            bathrooms = random.choices([2.0, 2.5, 3.0, 3.5], weights=[0.2, 0.3, 0.3, 0.2])[0]
            
        # Determine living area based on bedrooms and property type
        if bedrooms == 0:  # Studio
            living_area = random.randint(400, 600)
        else:
            base_area = 400 + (bedrooms * 250)
            if prop_type == 'CONDO':
                living_area = int(base_area * random.uniform(0.8, 1.2))
            elif prop_type == 'SINGLE_FAMILY':
                living_area = int(base_area * random.uniform(1.2, 1.6))
            else:
                living_area = int(base_area * random.uniform(1.0, 1.4))
        
        # Determine price based on property features and neighborhood
        # Start with base price
        base_price = 1500
        
        # Adjust for bedrooms
        base_price += bedrooms * 500
        
        # Adjust for bathrooms
        base_price += (bathrooms - 1) * 300
        
        # Adjust for living area
        base_price += living_area * 0.5
        
        # Adjust for property type
        type_factors = {
            'CONDO': 1.1,
            'SINGLE_FAMILY': 1.3,
            'MULTI_FAMILY': 0.95,
            'TOWNHOUSE': 1.2,
            'MANUFACTURED': 0.85
        }
        base_price *= type_factors.get(prop_type, 1.0)
        
        # Adjust for neighborhood
        if 'Downtown' in neighborhood or 'Back Bay' in neighborhood or 'Beacon Hill' in neighborhood:
            neighborhood_factor = random.uniform(1.3, 1.5)
        elif 'Cambridge' in neighborhood or 'Somerville' in neighborhood or 'South End' in neighborhood:
            neighborhood_factor = random.uniform(1.1, 1.3)
        else:
            neighborhood_factor = random.uniform(0.9, 1.1)
            
        base_price *= neighborhood_factor
        
        # Add some randomness
        price = int(base_price * random.uniform(0.9, 1.1))
        
        # Round to nearest $50
        price = round(price / 50) * 50
        
        # Create the listing
        listing = {
            'zpid': 10000000 + i,
            'address': f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Washington', 'Beacon', 'Commonwealth', 'Tremont'])} {random.choice(['St', 'Ave', 'Rd', 'Blvd'])}, {neighborhood}",
            'price': price,
            'rentZestimate': int(price * random.uniform(0.9, 1.1)),
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'livingArea': living_area,
            'latitude': lat,
            'longitude': lng,
            'propertyType': prop_type,
            'imgSrc': f"https://via.placeholder.com/350x250.png?text=Sample+{prop_type}+{bedrooms}BR"
        }
        
        listings.append(listing)
    
    return listings