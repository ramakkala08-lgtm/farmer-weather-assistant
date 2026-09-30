import requests


def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": [
            "precipitation_probability",
            "precipitation",
            "rain",
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m"
        ],

        "daily": [
            "precipitation_probability_max",
            "rain_sum",
            "temperature_2m_max",
            "temperature_2m_min"
        ],

        "timezone": "auto",
        "forecast_days": 1
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        return {
            "error": f"Unable to fetch weather: {str(e)}"
        }


    # =========================
    # TODAY
    # =========================

    today = {

        "date":
            data["daily"]["time"][0],

        "rain_probability":
            data["daily"]["precipitation_probability_max"][0],

        "rain_mm":
            data["daily"]["rain_sum"][0],

        "max_temperature":
            data["daily"]["temperature_2m_max"][0],

        "min_temperature":
            data["daily"]["temperature_2m_min"][0]

    }


    # =========================
    # HOURLY
    # =========================

    hourly = []


    for i in range(
        len(data["hourly"]["time"])
    ):

        hourly.append({

            "time":
                data["hourly"]["time"][i],

            "rain_probability":
                data["hourly"]["precipitation_probability"][i],

            "rain_mm":
                data["hourly"]["rain"][i],

            "precipitation_mm":
                data["hourly"]["precipitation"][i],

            "temperature":
                data["hourly"]["temperature_2m"][i],

            "humidity":
                data["hourly"]["relative_humidity_2m"][i],

            "wind_speed":
                data["hourly"]["wind_speed_10m"][i]

        })


    return {

        "today": today,

        "hourly": hourly

    }


if __name__ == "__main__":

    result = get_weather(
        17.9784,
        79.5941
    )

    print(result["today"])

    print(result["hourly"][0])