# MIT License
#
# Copyright (c) 2022 Ivan Radeljak, Bernhard Rippich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import getopt
import math
import sys

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from darts import TimeSeries
from darts.models import Prophet, ExponentialSmoothing

import utils


def calculate_prediction_darts(data: pd.DataFrame, y_columns: list[str], method: str, predict_count: int) -> pd.DataFrame:
    """
    Predicts the given data for the next n numbers.
    :param data:
    :param y_columns:
    :param method:
    :param predict_count:
    :return:
    """

    # Contains a dict of supported models.
    models = {
        'prophet': lambda: Prophet(changepoint_prior_scale=0.001, seasonality_prior_scale=0.8),
        'exponential': lambda: ExponentialSmoothing()
    }

    # Get the last unpredicted date from the list
    last_real_date = data.loc[len(data) - 1]['Date']

    # Calculate time values based on the last real date
    prediction_x_values = [last_real_date + relativedelta(months=x+1) for x in range(0, predict_count)]

    result_df = pd.DataFrame()
    result_df['Date'] = prediction_x_values

    for y_column in y_columns:
        # Predict for each column
        model = models[method]()

        series = TimeSeries.from_dataframe(data, 'Date', y_column)
        model.fit(series)
        prediction = model.predict(predict_count).values()
        result_df[y_column] = prediction
        result_df[y_column] = result_df.apply(lambda row: max(0, row[y_column]), axis=1)

    return result_df


def process_data(input_file: str, count: int, method: str, output_file: str):
    # Make prediction reproducible by using always the same random seed
    np.random.seed(0)

    input_dataframe = utils.read_history_sales_data_csv(input_file)

    prediction_results = None

    if method in ['exponential', 'prophet']:
        prediction_results = calculate_prediction_darts(input_dataframe, ['Fish', 'Ducks'], method, count)
    else:
        print("Prediction method is not supported.")
        sys.exit(-1)
        return

    rows: list[dict] = []

    for i in range(0, count):
        rows.append({
            'Fish': math.ceil(prediction_results.iloc[i]['Fish']),
            'Ducks': math.ceil(prediction_results.iloc[i]['Ducks']),
            'Year': prediction_results.iloc[i]['Date'].year,
            'Month': prediction_results.iloc[i]['Date'].strftime('%B')[0:1],
            'Date': prediction_results.iloc[i]['Date'],
            'Predicted': True
        })

    output_data_frame = pd.concat([input_dataframe, pd.DataFrame(rows)])
    output_data_frame['Total'] = output_data_frame.apply(lambda row: row['Fish'] + row['Ducks'], axis=1)

    output_data_frame.to_csv(output_file, index=None, header=True)


def main(argv):
    input_file = None
    output_file = None
    prediction_count = 3
    method = 'linear'

    try:
        opts, args = getopt.getopt(argv, "hi:o:c:m:", ["ifile=", "ofile=", "count=", "method="])
    except getopt.GetoptError:
        print('-i <inputfile> -o <outputfile> -c <count> -m <linear>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-i <inputfile> -o <outputfile> -c <count> -m <linear>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-c", "--count"):
            prediction_count = int(arg)
        elif opt in ("-m", "--method"):
            method = arg

    process_data(input_file, prediction_count, method, output_file)


if __name__ == '__main__':
    main(sys.argv[1:])
