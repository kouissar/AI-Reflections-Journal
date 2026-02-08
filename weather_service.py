import requests
import logging
from datetime import datetime
import streamlit as st

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/current.json"
    
    def get_weather(self, location=None):
        try:
            # use provided location or fallback to secrets
            if not location:
                location = st.secrets.get("weather", {}).get("zip_code", "20871")
            
            params = {
                "key": self.api_key,
                "q": location,
                "aqi": "no"
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
            
            logger.info(f"Weather fetched successfully for {location}")
            return weather_info
            
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            # Simpler approach: return dummy data if API fails so the app doesn't break
            return {
                "temperature": 72,
                "description": "Clear (Simulated)",
                "humidity": 45,
                "timestamp": datetime.now().isoformat()
            } 