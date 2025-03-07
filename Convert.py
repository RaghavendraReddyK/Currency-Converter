from flask import Flask, render_template, request,jsonify,json
from CustomException import ConnectFailed
import requests
import redis

app = Flask(__name__)

#function to connect to redis
def connectToRedis():
    RedisHost = 'redis-10810.c301.ap-south-1-1.ec2.redns.redis-cloud.com'
    RedisPort = 10810
    RedisPassword = 'iN2QcXeOwGBWd2igV9k3eNaNZy7q2uYq'

    try:
        redis_connection = redis.Redis(
            host=RedisHost,
            port=RedisPort,
            password=RedisPassword,
            db=0,
            decode_responses=True
        )

        # Test connection
        if redis_connection.ping():
            print("Connected to Redis successfully!")
            return redis_connection
    except redis.ConnectionError as e:
        raise ConnectFailed("Redis connection failed !!")


#function calculate the convertion rate
def getConvertedRate(baseCurrency,targetCurrency,amt):

    latestRatesURL = 'https://api.currencybeacon.com/v1/latest?api_key=xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs'

    redisConnection = connectToRedis()

    key = f"{baseCurrency}-{targetCurrency}"
    inversKey = f"{targetCurrency}-{baseCurrency}"
    ExchangeRate : float

    if redisConnection.exists(key) == 1:
        ExchangeRate = float(redisConnection.get(key))
        return amt * ExchangeRate

    elif redisConnection.exists(inversKey) == 1:
        ExchangeRate = 1/float(redisConnection.get(inversKey))
        redisConnection.setex(key,600,ExchangeRate)
        return amt * ExchangeRate
    else :
        url = f"{latestRatesURL}&base={baseCurrency}&symbols={targetCurrency}"

        response = requests.get(url)

        result = response.json()

        ExchangeRate = (result['rates'][f'{targetCurrency}'])

        redisConnection.setex(key,600,ExchangeRate)
        redisConnection.setex(inversKey,600,1/ExchangeRate)

        return amt * ExchangeRate

#Api End point to get Convertion rate
@app.route('/convert', methods=['POST'])
def apiCall(): 
    data = request.get_json()
    try :    
        amt = float(data['amt'])
        targetCurrency = data['target']
        baseCurrency = data['base']
    except :
        return jsonify("Provide both 'base' and 'target' values "),500

    convertedRate = getConvertedRate(baseCurrency,targetCurrency,amt)

    # formating my response to Json
    result_json_data = {
         "base" : baseCurrency,
         "amt" : amt,
         "converted_rates" : convertedRate
    }

    return jsonify(result_json_data)

    
@app.route('/rateoftheday', methods = ['GET'])
def oneRate():
    baseUrl = 'https://api.currencybeacon.com/v1/timeseries?api_key=xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs'
    base = request.args.get('base')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    symbols = request.args.get('symbols')

    url = f"{baseUrl}&base={base}&start_date={start_date}&end_date={end_date}&symbols={symbols}"

    responses = requests.get(url)
    result = responses.json()
    data = result['response']
    resValues = {}

    # Iterate through the nested dictionary
    for date, rates in data.items():
        print("date= "+ date)
        for currency, value in rates.items():
            resValues[date] = {currency: value}
            print("currency = "+currency)
            print(f"value = {value}")

    return resValues

if __name__ == "__main__":
    app.run(debug=True)
