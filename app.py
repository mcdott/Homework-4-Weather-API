import os
from datetime import datetime, timedelta
from pprint import PrettyPrinter

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file

# from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }

    result_json = requests.get(API_URL, params=params).json()

    # Show the results of the API call
    pp.pprint(result_json)

    # Retrieve context variables from the result_json object
    context = {
        'date': datetime.now(),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    params_city1 = {
        "q": city1,
        "appid": API_KEY,
        "units": units
    }
    params_city2 = {
        "q": city2,
        "appid": API_KEY,
        "units": units
    }

    def get_weather_from_API(params):
        """Makes an API call to get the weather."""
        return requests.get(API_URL, params=params).json()

    # Get the weather for each city. 
    result_city1_json = get_weather_from_API(params_city1)
    result_city2_json = get_weather_from_API(params_city2)

    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.

    city1_info = {
        'city': result_city1_json['name'],
        'temp': round(result_city1_json['main']['temp']),
        'humidity': result_city1_json['main']['humidity'],
        'wind_speed': round(result_city1_json['wind']['speed']),
        'sunset': datetime.fromtimestamp(result_city1_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }
    city2_info = {
        'city': result_city2_json['name'],
        'temp': round(result_city2_json['main']['temp']),
        'humidity': result_city2_json['main']['humidity'],
        'wind_speed': round(result_city2_json['wind']['speed']),
        'sunset': datetime.fromtimestamp(result_city2_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    context = {
        'date': datetime.now(),
        'city1_info': city1_info,
        'city2_info': city2_info,
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
