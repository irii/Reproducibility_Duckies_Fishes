#!/bin/bash
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

set -e

# Arguments

while getopts u:a:f: flag
do
    case "${flag}" in
        m) PREDICTION_METHOD=${OPTARG};;
        c) PREDICTION_COUNT=${OPTARG};;
    esac
done

# Each step is separated into files for independent development.

# Prepare files - Convert to csv and calculate a machine readable date, starting always with January.
python3.9 ./src/convert_xls_to_csv_and_normalize.py \
        -i "${DATA_FOLDER}/historical_sales_data.xls" \
        -o "${TEMPLATE_FOLDER}/historical_sales_data.input.csv" \

# Execute prediction
python3.9 ./src/calculate_prediction.py \
        -i "${TEMPLATE_FOLDER}/historical_sales_data.input.csv" \
        -o "${TEMPLATE_FOLDER}/historical_sales_data.predicted.csv" \
        -c "${PREDICTION_COUNT}"\
        -m "${PREDICTION_METHOD}"

# Execute sales calculation
python3.9 ./src/calculate_sales.py \
        -i "${TEMPLATE_FOLDER}/historical_sales_data.predicted.csv" \
        -o "${TEMPLATE_FOLDER}/historical_sales_data.optimized.csv"

# Execute knitr and tex generation
cd "${TEMPLATE_FOLDER}"
Rscript -e "library(knitr); library(scales); library(ggplot2); library(tidyverse); knit2pdf('document.Rnw')"

# Export results to output folder
cp "historical_sales_data.optimized.csv" "${OUTPUT_FOLDER}/historical_sales_data.optimized.csv"
cp "document.pdf" "${OUTPUT_FOLDER}/document.pdf"
