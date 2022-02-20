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
import sys
import datetime
import pandas as pd


def __last_day_of_month(date):
    # Get last day of a month

    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)


def __calculate_date(row) -> datetime.date:
    # Calculate date column with the last day of the month

    month = int(row.name % 12) + 1

    date_start = datetime.date(year=int(row['Year']), month=month, day=1)
    date_end = __last_day_of_month(date_start)
    return datetime.date(year=date_end.year, month=date_end.month, day=date_end.day)


def process_data(input_file: str, output_file: str):
    raw_frame = pd.read_excel(input_file)
    raw_frame = raw_frame[(raw_frame['Year'].notna()) & (raw_frame['Month'].notna())]

    raw_frame['Date'] = raw_frame.apply(__calculate_date, axis=1)

    # Remove unnamed columns
    raw_frame = raw_frame.loc[:, ~raw_frame.columns.str.contains('^Unnamed')]

    raw_frame = raw_frame[['Month', 'Year', 'Date', 'Ducks', 'Fish']]
    raw_frame['Total'] = raw_frame.apply(lambda row: row['Ducks'] + row['Fish'], axis=1)
    raw_frame['Predicted'] = False

    raw_frame.to_csv(output_file, index=None, header=True)


def main(argv):
    input_file = None
    output_file = None

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('-i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    process_data(input_file, output_file)


if __name__ == '__main__':
    main(sys.argv[1:])
