from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import requests
import math
from scipy import stats

IEX_CLOUD_API_TOKEN = "sk_733d9196181c43219b61c489d0c1d417"

def portfolio_input():
    global portfolio_size
    portfolio_size = 1000000
    
    try:
        float(portfolio_size)
    except ValueError:
        print("That is not a number. n\Please try again...")
        portfolio_size = 1000000
        # portfolio_size = input("Enter size of portfolio")

df = pd.read_csv("UpdateNewcollectionSP.csv", error_bad_lines=False)
df.sort_values(by="environment_score", ascending=False, inplace=True)

the_good = df.iloc[:10]
the_bad = df.iloc[-10:]
the_good_list = the_good["Ticker"].tolist()
the_bad_list = the_bad["Ticker"].tolist()

symbol_strings = the_good_list
symbol_strings2 = the_bad_list

hqm_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    "HQM Score"
]

hqm_dataframe = pd.DataFrame(columns=hqm_columns)
convert_none = lambda x : 0 if x is None else x

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()

    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['price'],
                    'N/A',
                    convert_none(data[symbol]['stats']['year1ChangePercent']),
                    'N/A',
                    convert_none(data[symbol]['stats']['month6ChangePercent']),
                    'N/A',
                    convert_none(data[symbol]['stats']['month3ChangePercent']),
                    'N/A',
                    convert_none(data[symbol]['stats']['month1ChangePercent']),
                    'N/A',
                    "N/A"
                ],
                index = hqm_columns
            ),
            ignore_index=True
        )



hqm_dataframe2 = pd.DataFrame(columns=hqm_columns)
convert_none = lambda x : 0 if x is None else x

for symbol_string in symbol_strings2:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()

    for symbol in symbol_string.split(','):
        hqm_dataframe2 = hqm_dataframe2.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['price'],
                    'N/A',
                    convert_none(data[symbol]['stats']['year1ChangePercent']),
                    'N/A',
                    convert_none(data[symbol]['stats']['month6ChangePercent']),
                    'N/A',
                    convert_none(data[symbol]['stats']['month3ChangePercent']),
                    'N/A',
                    convert_none(data[symbol]['stats']['month1ChangePercent']),
                    'N/A',
                    "N/A"
                ],
                index = hqm_columns
            ),
            ignore_index=True
        )

time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]

for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])/100
        

for row in hqm_dataframe2.index:
    for time_period in time_periods:
        hqm_dataframe2.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe2[f'{time_period} Price Return'], hqm_dataframe2.loc[row, f'{time_period} Price Return'])/100


from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, "HQM Score"] = mean(momentum_percentiles)



for row in hqm_dataframe2.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe2.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe2.loc[row, "HQM Score"] = mean(momentum_percentiles)


hqm_dataframe.sort_values("HQM Score", ascending = False, inplace=True)
hqm_dataframe = hqm_dataframe[:5]
hqm_dataframe.reset_index(inplace = True, drop = True)
hqm_dataframe

hqm_dataframe2.sort_values("HQM Score", ascending = False, inplace=True)
hqm_dataframe2 = hqm_dataframe2[:5]
hqm_dataframe2.reset_index(inplace = True, drop = True)

portfolio_input()

position_size = float(portfolio_size)/len(hqm_dataframe.index)
for i in hqm_dataframe.index:
    hqm_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size/hqm_dataframe.loc[i, "Price"])

portfolio_input()

position_size = float(portfolio_size)/len(hqm_dataframe2.index)
for i in hqm_dataframe2.index:
    hqm_dataframe2.loc[i, "Number of Shares to Buy"] = math.floor(position_size/hqm_dataframe2.loc[i, "Price"])


the_good_mean_s = mean(hqm_dataframe["Price"]*hqm_dataframe["Number of Shares to Buy"])
the_bad_mean_s = mean(hqm_dataframe2["Price"]*hqm_dataframe2["Number of Shares to Buy"])

symbol_strings_good_u = hqm_dataframe["Ticker"]
symbol_strings_bad_u = hqm_dataframe2["Ticker"]
global dict_return
dict_return = {"The bad mean":the_bad_mean_s, "The good mean":the_good_mean_s}




app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
 

@app.route('/good', methods=['GET'])
def returnGood():

    def run_dev_func():

        hqm_columns_update = [
            'Ticker',
            'Price',
            'Names'
        ]

        hqm_dataframe_u = pd.DataFrame(columns=hqm_columns_update)
        convert_none = lambda x : 0 if x is None else x

        for symbol_string in symbol_strings_good_u:
            batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
            data = requests.get(batch_api_call_url).json()

            for symbol in symbol_string.split(','):
                hqm_dataframe_u = hqm_dataframe_u.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['price'],
                            data[symbol]["stats"]["companyName"]
                        ],
                        index = hqm_columns_update
                    ),
                    ignore_index=True
                )
        the_good_total_u = round(sum(hqm_dataframe_u["Price"]*hqm_dataframe["Number of Shares to Buy"]),2)      
        the_good_mean_u = mean(hqm_dataframe_u["Price"]*hqm_dataframe["Number of Shares to Buy"])

        hqm_dataframe_u2 = pd.DataFrame(columns=hqm_columns_update)
        convert_none = lambda x : 0 if x is None else x

        for symbol_string in symbol_strings_bad_u:
            batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
            data = requests.get(batch_api_call_url).json()

            for symbol in symbol_string.split(','):
                hqm_dataframe_u2 = hqm_dataframe_u2.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['price'],
                            data[symbol]["stats"]["companyName"]
                        ],
                        index = hqm_columns_update
                    ),
                    ignore_index=True
                )
        the_bad_total_u = round(sum(hqm_dataframe_u2["Price"]*hqm_dataframe2["Number of Shares to Buy"]),2)
        the_bad_mean_u = mean(hqm_dataframe_u2["Price"]*hqm_dataframe2["Number of Shares to Buy"])
        # dev_good = the_good_mean_u/the_good_mean_s/100
        # dev_bad = the_bad_mean_u/the_bad_mean_s/100
        dev_good = the_good_mean_u/the_good_mean_s
        dev_bad = the_bad_mean_u/the_bad_mean_s
        dev_good_per = round(dev_good-1,5)
        dev_bad_per = round(dev_bad-1,5)

        current_val_good_rounded = round(the_good_mean_u,2)
        current_val_bad_rounded = round(the_bad_mean_u,2)

        good_names = hqm_dataframe_u["Names"].tolist()
        bad_names = hqm_dataframe_u2["Names"].tolist()

        global dev_return
        dev_return = {"Good dev":dev_good_per, "Bad dev":dev_bad_per, "Current val good": the_good_total_u, "Current val bad": the_bad_total_u, "Good names": good_names,"Bad names": bad_names}
        print(f'Value the good {round(the_good_mean_s,2)} $')
        print(f'Value the bad {round(the_bad_mean_s,2)} $')

        print(f'Development the good {dev_good_per} %')
        print(f'Development the bad {dev_bad_per} %')

        print(f'Names the good {good_names}')
        print(f'Names the bad {bad_names}')


        return dev_return
    

    import time
    while True:
        return run_dev_func()
        time.sleep(60)
    

if __name__ == "__main__":
    app.run(debug=True)