# # models/model.py

# import numpy as np
# import pandas as pd
# import joblib
# import os

# def predict_rent(model, latitude, longitude, property_type, bedrooms, 
#                  bathrooms, living_area, lot_area=0.25, days_on_market=0):
#     """
#     Predicts the rental price using the trained model.
    
#     Args:
#         model: The trained ML model
#         latitude: Property latitude
#         longitude: Property longitude
#         property_type: Type of property (SINGLE_FAMILY, CONDO, etc.)
#         bedrooms: Number of bedrooms
#         bathrooms: Number of bathrooms
#         living_area: Square footage of the property
#         lot_area: Size of the lot in acres (default: 0.25)
#         days_on_market: Days the property has been on market (default: 0)
        
#     Returns:
#         float: Predicted monthly rent
#     """
#     try:
#         # Create feature dictionary
#         features = {
#             'bedrooms': bedrooms,
#             'bathrooms': bathrooms,
#             'livingArea': living_area,
#             'latitude': latitude,
#             'longitude': longitude,
#             'propertyType': property_type,
#             'lotAreaValue': lot_area,
#             'daysOnZillow': days_on_market
#         }
        
#         # Add engineered features
#         features['bedrooms_squared'] = bedrooms ** 2
#         features['bathrooms_squared'] = bathrooms ** 2
#         features['living_area_sqrt'] = np.sqrt(living_area)
#         features['bed_bath_ratio'] = bedrooms / max(1, bathrooms)  # Avoid division by zero
#         features['bed_area_ratio'] = bedrooms / (living_area + 1)  # Add 1 to avoid division by zero
        
#         # Create DataFrame with the property features
#         property_data = pd.DataFrame([features])
        
#         # Make prediction - handle both log-transformed and regular models
#         prediction = model.predict(property_data)
        
#         # If the model outputs log-transformed predictions, convert back
#         if prediction[0] < 20:  # Heuristic: if prediction is very small, it's likely log-transformed
#             predicted_rent = np.expm1(prediction)[0]
#         else:
#             predicted_rent = prediction[0]
            
#         return predicted_rent
        
#     except Exception as e:
#         print(f"Error in predict_rent: {e}")
#         # Fallback to a simple estimation
#         base_rent = 1500 + (bedrooms * 500) + (bathrooms * 300) + (living_area * 0.5)
#         return base_rent







# models/model.py
import pandas as pd
import numpy as np
import os

def predict_rent(model, bedrooms, bathrooms, zipcode=None, latitude=None, longitude=None, 
                property_type=None, living_area=None, lot_area=None, days_on_market=0):
    """
    Predicts the rental price using the trained model.
    
    Required parameters:
    - bedrooms: Number of bedrooms
    - bathrooms: Number of bathrooms
    - zipcode: Property zipcode
    
    Optional parameters:
    - latitude: Property latitude
    - longitude: Property longitude
    - property_type: Type of property (SINGLE_FAMILY, CONDO, etc.)
    - living_area: Square footage
    - lot_area: Lot size in acres
    - days_on_market: Days the property has been on market
    """
    try:
        # Create feature dictionary with required fields
        features = {
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'zipcode': str(zipcode) if zipcode else '02108'  # Boston zipcode as default
        }
        
        # Add optional fields if provided
        if living_area is not None:
            features['livingArea'] = living_area
        else:
            features['livingArea'] = 1000  # Default square footage
            
        if property_type is not None:
            features['propertyType'] = property_type
        else:
            features['propertyType'] = 'SINGLE_FAMILY'
            
        if latitude is not None:
            features['latitude'] = latitude
        else:
            features['latitude'] = 42.3601  # Boston coordinates
            
        if longitude is not None:
            features['longitude'] = longitude
        else:
            features['longitude'] = -71.0589  # Boston coordinates
            
        if lot_area is not None:
            features['lotAreaValue'] = lot_area
        else:
            features['lotAreaValue'] = 0.25  # Default lot size
            
        features['daysOnZillow'] = days_on_market
        
        # Add engineered features
        features['bedrooms_squared'] = features['bedrooms'] ** 2
        features['bathrooms_squared'] = features['bathrooms'] ** 2
        features['living_area_sqrt'] = np.sqrt(features['livingArea'])
        features['bed_bath_ratio'] = features['bedrooms'] / max(1, features['bathrooms'])
        features['bed_area_ratio'] = features['bedrooms'] / (features['livingArea'] + 1)
        
        # Add location-based features
        boston_lat, boston_lng = 42.3601, -71.0589
        features['boston_distance'] = np.sqrt(
            (features['latitude'] - boston_lat) ** 2 + 
            (features['longitude'] - boston_lng) ** 2
        )
        
        cambridge_lat, cambridge_lng = 42.3736, -71.1097
        features['cambridge_distance'] = np.sqrt(
            (features['latitude'] - cambridge_lat) ** 2 + 
            (features['longitude'] - cambridge_lng) ** 2
        )
        
        # Create DataFrame with the property features
        property_data = pd.DataFrame([features])
        
        # Make prediction
        prediction = model.predict(property_data)
        
        # If the model outputs log-transformed predictions, convert back
        if prediction[0] < 20:  # Heuristic: if prediction is very small, it's likely log-transformed
            predicted_rent = np.expm1(prediction)[0]
        else:
            predicted_rent = prediction[0]
            
        return predicted_rent
        
    except Exception as e:
        print(f"Error in predict_rent: {e}")
        # Fallback to a simple estimation
        base_rent = 1500 + (bedrooms * 500) + (bathrooms * 300)
        if living_area is not None:
            base_rent += living_area * 0.5
        return base_rent