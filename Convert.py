from flask import Flask, render_template, request,jsonify,json
import requests
import redis

app = Flask(__name__)

baseUrl = 'https://api.currencybeacon.com/v1/latest?api_key=xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs'

RedisHost = 'redis-10810.c301.ap-south-1-1.ec2.redns.redis-cloud.com'
RedisPort = 10810
RedisPassword = 'iN2QcXeOwGBWd2igV9k3eNaNZy7q2uYq'


redis_connection = redis.Redis(
    host=RedisHost,
    port=RedisPort,
    password=RedisPassword,
    db=0,
)

@app.route('/convert', methods=['POST'])
def apiCall():

    data = request.get_json()
    amt = float(data['amt'])
    target = data['target']
    baseCurrency = data['base']

    convertedRates = {}
    KeysNotPresent = {}

    #Getting All the keys from Redis 
    redisKeys = redis_connection.keys()


    # if data is available in Redis chache
    for target in target:
        tempKey = data['base']+"-"+target
        if tempKey in redisKeys:
            convertedRates[target] = float(redis_connection.get(tempKey)) * amt
        else:
            KeysNotPresent[target] = tempKey

    # if data not available in Redis Chache
    if(len(KeysNotPresent) != 0):
        url = f"{baseUrl}&base={baseCurrency}"
        response = requests.get(url)
        result = response.json()
        if result and 'rates' in result:
            rates = result['rates']
            for currency, rate in rates.items():
                if currency in KeysNotPresent:
                    convertedRates[currency] = rate * amt
                    
                    #Setting new redis Key with 10 min expiry
                    redis_connection.setex(KeysNotPresent[currency], 600, rate)


    #formating my response to Json
    result_json_data = {
         "base" : baseCurrency,
         "amt" : amt,
         "converted_rates" : convertedRates
    }

    return jsonify(result_json_data)

if __name__ == "__main__":
    app.run(debug=True)
