from flask import Flask, render_template, request,jsonify
import requests

app = Flask(__name__)

countryList = ['INR', 'USD', 'EUR', 'JPY', 'GBP', 'ZAR']
baseUrl = 'https://api.currencybeacon.com/v1/latest?api_key=xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def apiCall():
    filtered_rates = {}
    data = request.get_json()
    url = f"{baseUrl}&base={data["base"]}"
    response = requests.get(url)
    result = response.json()

    if result and 'rates' in result:
            rates = result['rates']
            for currency, rate in rates.items():
                if currency in data["target"]:
                    filtered_rates[currency] = rate * data["amt"]

    result_json_data = {
         "base" : data['base'],
         "amt" : data['amt'],
         "converted_rates" : filtered_rates
    }

    return jsonify(result_json_data)

if __name__ == "__main__":
    app.run(debug=True)
