import os

class Config:
    """Configuration settings for the application"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    DEBUG = True
    PORT = 5001
    
    # API keys (hardcoded - not recommended for production)
    GOOGLE_MAPS_API_KEY = "AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk"
    ZILLOW_API_KEY = '30c130cfe6mshb5b1c7bdb9d6832p10fad8jsnb59fe5804bc3'  # Replace with your actual Zillow API key
    ZILLOW_API_HOST = 'zillow-com1.p.rapidapi.com'
    
    # Model paths
    RENTAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'rental_model.pkl')
    SALES_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'price-prediction-model', 'xgboost', 'xgboost_final_model.pkl')
    
    # API settings
    REALTOR_API_KEY = "6b504def46msha6bf4ff53605f98p1c0c1djsn3fcd43362b33"
    REALTOR_HOST = "realty-in-us.p.rapidapi.com"
    
    # Server settings
    HOST = '0.0.0.0'


