import requests

from src.python.utils.utils import get_ip_info
from src.python.classes.weather_forecast_info import WeatherForecastInfo


def clean_up_weather_data(data: dict) -> WeatherForecastInfo | None:
    try:
        data = data['list']
        weather_forecast_info = WeatherForecastInfo(data[0]['dt_txt'].split()[0])
    except (ValueError, IndexError):
        return None

    for forecast in data:
        forecast_dt = forecast['dt_txt']
        if forecast_dt.split()[0] != weather_forecast_info.from_date:
            break

        weather = forecast['weather'][0]['main']
        humidity = forecast['main']['humidity']

        temp = {
            "time": forecast_dt.split()[1],
            "weather": weather,
            "humidity": humidity
        }

        weather_forecast_info.forecast.append(temp)

    return weather_forecast_info


def get_climate_info(ip: str, open_weather_api_key: str, ip_info_api_key: str) -> WeatherForecastInfo | None:
    city = get_ip_info(ip, ip_info_api_key)['city']
    url = f"https://api.openweathermap.org/data/2.5/forecast?id=524901&appid={open_weather_api_key}&units" \
          f"=metric&lang=pt_br&exclude=daily&q={city}"
    response = requests.get(url)
    if response.status_code in range(200, 299):
        return clean_up_weather_data(response.json())
    else:
        return None
