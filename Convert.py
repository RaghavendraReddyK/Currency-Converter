from flask import Flask, render_template, request
import requests

app = Flask(__name__)

countryList = ['INR', 'USD', 'EUR', 'JPY', 'GBP', 'ZAR']
baseUrl = 'https://api.currencybeacon.com/v1/latest?api_key=xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def apiCall():
    data = None
    filtered_rates = {}

    if request.method == 'POST':
        country = request.form['country']
        amount = float(request.form['amt'])
        url = f"{baseUrl}&base={country}"

        response = requests.get(url)
        print(response)
        data = response.json()
        print(data)

        if data and 'rates' in data:
            rates = data['rates']
            for currency, rate in rates.items():
                if currency in countryList:
                    filtered_rates[currency] = rate * amount

        return render_template('result.html', rates=filtered_rates, country=country,amount=amount)

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
