from datetime import datetime
from flask import Flask, render_template, request,jsonify
from Convert import getExchangeRate, connectToDB, make_api_call

app = Flask(__name__)

#Api End point to get Convertion rate
@app.route('/convert', methods=['POST'])
def apiCall(): 
    data = request.get_json()
    try :    
        amt = float(data['amt'])
        targetCurrency = data['target']
        baseCurrency = data['base']
    except :
        return jsonify("Provide both 'base' and 'target' values "),400

    exchangeRate = getExchangeRate(baseCurrency,targetCurrency)

    # formating my response to Json
    result_json_data = {
         "base" : baseCurrency,
         "amt" : amt,
         "converted_rates" : exchangeRate * amt
    }

    return jsonify(result_json_data)

    
@app.route('/addRates', methods = ['GET'])
def add():
    # try:
    base = request.args.get('base')
    symbol = request.args.get('symbols')

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

# except:
    # return jsonify("Enter all the parameters !!"), 400

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()


    if start_date > end_date or end_date > datetime.utcnow().date():
        raise Exception("enter the valid dates")

    else:
        try:
            conn = connectToDB()
            cursor = conn.cursor()
            print ("connected to db")

            api_params = {
            "base": base,
            "start_date": start_date,
            "end_date": end_date,
            "symbols": symbol
            }

            result = make_api_call('timeseries',api_params)
            data = result['response']

            
            insert_query = """
                    INSERT INTO exchange_rates (base_currency, target_currency, currency_exchange_rate, rate_date) VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (base_currency, target_currency, rate_date) DO NOTHING;
                """
            
            # Iterate through the nested dictionary
            for date, rates in data.items():
                
                cursor.execute(insert_query, (base, symbol, rates[symbol], date))

            conn.commit()
            return jsonify("data added to db"),200

        finally:
            cursor.close()
            conn.close()


@app.route('/GetRates', methods = ['GET'])
def getRates():

    # try:
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    # except:
    #     return jsonify("Enter all the parameters !!"), 400

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    try:
        conn = connectToDB()
        cursor = conn.cursor()

        # SQL query to fetch exchange rates within the date range
        getQuery = "SELECT * FROM exchange_rates WHERE rate_date >= %s AND rate_date <= %s"
        cursor.execute(getQuery, (start_date, end_date))

        
        # Fetch all results
        results = cursor.fetchall()
        # print(results)

        # Convert results to JSON
        rate_list = []
        for row in results:
            rate_list.append({
                "id": row[0], 
                "base_currency": row[1],
                "target_currency": row[2],
                "exchange_rate": row[3],
                "rate_date": row[4].strftime("%Y-%m-%d") 
            })

        return jsonify(rate_list), 200
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
