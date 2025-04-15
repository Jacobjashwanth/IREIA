import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def clean_property_data(df):
    """
    Clean and preprocess property data.
    
    Args:
        df: Pandas DataFrame with property data
        
    Returns:
        DataFrame: Cleaned data
    """
    # Make a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Convert columns to appropriate types
    if 'bedrooms' in df_clean.columns:
        df_clean['bedrooms'] = pd.to_numeric(df_clean['bedrooms'], errors='coerce')
    
    if 'bathrooms' in df_clean.columns:
        df_clean['bathrooms'] = pd.to_numeric(df_clean['bathrooms'], errors='coerce')
    
    if 'livingArea' in df_clean.columns:
        df_clean['livingArea'] = pd.to_numeric(df_clean['livingArea'], errors='coerce')
    
    if 'latitude' in df_clean.columns:
        df_clean['latitude'] = pd.to_numeric(df_clean['latitude'], errors='coerce')
    
    if 'longitude' in df_clean.columns:
        df_clean['longitude'] = pd.to_numeric(df_clean['longitude'], errors='coerce')
    
    # Handle missing values
    numeric_cols = ['bedrooms', 'bathrooms', 'livingArea', 'latitude', 'longitude']
    for col in numeric_cols:
        if col in df_clean.columns:
            # Fill missing values with median
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    
    # Ensure propertyType is standardized
    if 'propertyType' in df_clean.columns:
        # Convert to uppercase and replace spaces with underscores
        df_clean['propertyType'] = df_clean['propertyType'].str.upper().str.replace(' ', '_')
        
        # Map similar values to standard categories
        type_mapping = {
            'HOUSE': 'SINGLE_FAMILY',
            'APARTMENT': 'MULTI_FAMILY',
            'COOP': 'CONDO',
            'DUPLEX': 'MULTI_FAMILY',
            'TRIPLEX': 'MULTI_FAMILY'
        }
        
        df_clean['propertyType'] = df_clean['propertyType'].replace(type_mapping)
        
        # Fill missing with most common
        df_clean['propertyType'] = df_clean['propertyType'].fillna('SINGLE_FAMILY')
    
    return df_clean

def add_engineered_features(df):
    """
    Add engineered features to the dataframe.
    
    Args:
        df: Pandas DataFrame with property data
        
    Returns:
        DataFrame: Data with additional features
    """
    # Create a copy to avoid modifying the original
    df_features = df.copy()
    
    # Add squared terms for non-linear relationships
    if 'bedrooms' in df_features.columns:
        df_features['bedrooms_squared'] = df_features['bedrooms'] ** 2
    
    if 'bathrooms' in df_features.columns:
        df_features['bathrooms_squared'] = df_features['bathrooms'] ** 2
    
    # Add square root for living area (diminishing returns)
    if 'livingArea' in df_features.columns:
        df_features['living_area_sqrt'] = np.sqrt(df_features['livingArea'])
    
    # Add ratios between features
    if 'bedrooms' in df_features.columns and 'bathrooms' in df_features.columns:
        # Avoid division by zero
        df_features['bed_bath_ratio'] = df_features['bedrooms'] / df_features['bathrooms'].replace(0, 1)
    
    if 'bedrooms' in df_features.columns and 'livingArea' in df_features.columns:
        # Add 1 to avoid division by zero
        df_features['bed_area_ratio'] = df_features['bedrooms'] / (df_features['livingArea'] + 1)
    
    # Add location-based features if latitude and longitude are available
    if 'latitude' in df_features.columns and 'longitude' in df_features.columns:
        # Distance from Boston city center
        boston_lat, boston_lng = 42.3601, -71.0589
        df_features['boston_distance'] = np.sqrt(
            (df_features['latitude'] - boston_lat) ** 2 + 
            (df_features['longitude'] - boston_lng) ** 2
        )
        
        # Distance from Cambridge
        cambridge_lat, cambridge_lng = 42.3736, -71.1097
        df_features['cambridge_distance'] = np.sqrt(
            (df_features['latitude'] - cambridge_lat) ** 2 + 
            (df_features['longitude'] - cambridge_lng) ** 2
        )
    
    return df_features

def prepare_features_for_prediction(df, categorical_columns=None):
    """
    Prepare features for prediction by encoding categorical variables.
    
    Args:
        df: Pandas DataFrame with property data
        categorical_columns: List of categorical column names
        
    Returns:
        DataFrame: Data ready for prediction
    """
    # If categorical columns not specified, use default
    if categorical_columns is None:
        categorical_columns = ['propertyType']
    
    # Create a copy to avoid modifying the original
    df_prepared = df.copy()
    
    # One-hot encode categorical variables
    for col in categorical_columns:
        if col in df_prepared.columns:
            # Create dummy variables
            dummies = pd.get_dummies(df_prepared[col], prefix=col, dummy_na=False)
            # Add to dataframe
            df_prepared = pd.concat([df_prepared, dummies], axis=1)
            # Remove original column
            df_prepared = df_prepared.drop(col, axis=1)
    
    return df_prepared







