import datetime 
from flask import Flask, render_template, request,jsonify
import psycopg2
import requests
import redis

app = Flask(__name__)


BASE_API_URL = "https://api.currencybeacon.com/v1"

# Generic function to make an API call
def make_api_call(endpoint, params):
    url = f"{BASE_API_URL}/{endpoint}"
    api_key = "xDJeYfJERFQj9TegI4PKmpcWGAQnIHhs"
    params["api_key"] = api_key
    
    try:
        response = requests.get(url, params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

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
    except Exception as e:
        raise Exception("Redis connection failed !!")
    

#connect to DB
def connectToDB():
    
    DB_host = "dev-common-eksom-vend-db.c3ucia680nmx.af-south-1.rds.amazonaws.com"
    DB_name = "playground"
    DB_user = "player"
    DB_password = "iAMready"

    try:
        conn = psycopg2.connect(
            host=DB_host,
            dbname=DB_name,
            user=DB_user,
            password=DB_password,
            port = 5432
        )
        return conn
    except Exception as e:
        # print(f"Error: {e}")
        raise Exception("Db connection Failed")

#function calculate the convertion rate
def getExchangeRate(baseCurrency,targetCurrency):

    redisConnection = connectToRedis()

    key = f"{baseCurrency}-{targetCurrency}"
    inversKey = f"{targetCurrency}-{baseCurrency}"
    ExchangeRate : float

    if redisConnection.exists(key) == 1:
        ExchangeRate = float(redisConnection.get(key))
        return ExchangeRate

    elif redisConnection.exists(inversKey) == 1:
        ExchangeRate = 1/float(redisConnection.get(inversKey))
        redisConnection.setex(key,600,ExchangeRate)
        return ExchangeRate
    else :

        api_params = {
        "base": baseCurrency,
        "symbols": targetCurrency,
        }

        result = make_api_call('latest',api_params)

        ExchangeRate = (result['rates'][f'{targetCurrency}'])

        redisConnection.setex(key,600,ExchangeRate)
        redisConnection.setex(inversKey,600,1/ExchangeRate)

        return ExchangeRate
    

if __name__ == "__main__":
    app.run(debug=True)
