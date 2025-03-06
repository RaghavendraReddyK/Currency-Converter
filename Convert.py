from flask import Flask, render_template, request,jsonify,json
import requests
import redis

app = Flask(__name__)

baseUrl = 'https://api.currencybeacon.com/v1/latest?api_key=xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs'

REDIS_HOST = 'redis-10810.c301.ap-south-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = 10810
REDIS_PASSWORD = 'iN2QcXeOwGBWd2igV9k3eNaNZy7q2uYq'


redis_connection = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
    decode_responses=True
)
# Test connection
redis_connection.ping()

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/convert', methods=['POST'])
def apiCall():

    filtered_rates = {}
    data = request.get_json()
    url = f"{baseUrl}&base={data["base"]}"
    response = requests.get(url)
    result = response.json()
    amt = float(data["amt"])

    if result and 'rates' in result:
            rates = result['rates']
            for currency, rate in rates.items():
                if currency in data["target"]:
                    filtered_rates[currency] = rate * amt

    result_json_data = {
         "base" : data['base'],
         "amt" : amt,
         "converted_rates" : filtered_rates
    }

    redis_connection.setex(data['base'],10, str(filtered_rates))
    print(redis_connection.ttl(data['base']))
    print(redis_connection.get(data['base']))

    return jsonify(result_json_data)

if __name__ == "__main__":
    app.run(debug=True)
