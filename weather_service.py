import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/current.json"
    
    def get_weather(self, zip_code, country_code="US"):
        try:
            params = {
                "key": self.api_key,
                "q": f"{zip_code}",  # WeatherAPI accepts zip codes directly
                "aqi": "no"  # We don't need air quality data
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            weather_info = {
                "temperature": round(data["current"]["temp_f"]),
                "description": data["current"]["condition"]["text"].capitalize(),
                "humidity": data["current"]["humidity"],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Weather fetched successfully for {zip_code}")
            return weather_info
            
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return None 