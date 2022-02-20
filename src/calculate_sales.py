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
from typing import Tuple
import pandas as pd
import pulp
import utils


def solve_amount_problem(required_ducks: int, required_fishes,
                         profit_per_duck: float = 5, profit_per_fish: float = 4,
                         pellets_per_duck: int = 100, pellets_per_fish: int = 125,
                         max_allowed_pellets: int = 50000,
                         max_count_ducks: int = 400, max_count_fish: int = 300) -> Tuple[int, int, float]:
    """
    Calculates the optimal factory values for duckies and fishes.

    Returns a dict with [
        'Optimal_Ducks',
        'Optimal_Fish',
        'Optimal_Total',
        'Total_Profit'
    ]
    """

    # set the dictionary for each feature
    prob = pulp.LpProblem('SalesAmount', pulp.LpMaximize)

    duck_var = pulp.LpVariable('Duck', lowBound=0, cat='Integer')
    fish_var = pulp.LpVariable('Fish', lowBound=0, cat='Integer')

    # Target Result
    prob += duck_var * profit_per_duck + fish_var * profit_per_fish, "Total Sales Amount"

    # Set Constraints (Like in Excel Solver)

    prob += duck_var >= required_ducks, "Min Ducks"
    prob += fish_var >= required_fishes, "Min Fishes"
    prob += duck_var <= max_count_ducks, "Max Ducks - Factory restriction"
    prob += fish_var <= max_count_fish, "Max Fishes - Factory restriction"
    prob += (duck_var * pellets_per_duck + fish_var * pellets_per_fish) <= max_allowed_pellets, "Pellets Limit - Resource restriction"

    # Solve the problem and return results
    prob.solve()

    return {
        'Optimal_Ducks': duck_var.varValue,
        'Optimal_Fish': fish_var.varValue,
        'Optimal_Total': duck_var.varValue + fish_var.varValue,
        'Optimal_Profit': pulp.value(prob.objective)
    }


def process_data(input_file: str, output_file: str):
    input_dataframe = utils.read_history_sales_data_csv(input_file)

    appiled_df = input_dataframe.apply(lambda row: solve_amount_problem(row['Ducks'], row['Fish']), axis='columns', result_type='expand')
    output_dataframe = pd.concat([input_dataframe, appiled_df], axis='columns')

    output_dataframe.to_csv(output_file, index=None, header=True)


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

