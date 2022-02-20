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

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV LANG="C.UTF-8"
ENV LC_ALL="C.UTF-8"

LABEL maintainer="Ivan Radeljak <ivan.radeljak@st.oth-regensburg.de>; Bernhard Rippich <bernhard.rippich@st.oth-regensburg.de>"

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        nano \
        sudo \
        curl \
        zlib1g-dev \
        liblapack-dev \
        libblas-dev \
        libssl-dev \
        libcurl4-openssl-dev \
        libxml2-dev \
        r-base \
        r-base-dev \
        r-cran-ggplot2 \
        r-cran-reshape2 \
        r-cran-knitr \
        r-cran-tinytex \
        r-cran-tidyverse \
        texlive-base \
        texlive-bibtex-extra \
        texlive-fonts-recommended \
        texlive-latex-extra \
        texlive-publishers

# Use Anaconda as package manager. pip causes issues when compiling pystan with python 3.9
RUN curl -LO "http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# Install Python and all required packages
RUN conda config --add channels conda-forge
RUN conda config --set channel_priority strict
RUN conda install -c conda-forge -y \
        python=3.9.10 \
        pandas=1.4.1 \
        xlrd=2.0.1 \
        scikit-learn=1.0.2 \
        pulp=2.6.0 \
        pystan=2.19.1.1 \
        prophet=1.0.1 \
        u8darts=0.17.1

# Don't run container as root user
RUN useradd -m -G sudo -s /bin/bash repro && echo "repro:repro" | chpasswd
RUN usermod -a -G staff repro
USER repro

WORKDIR /home/repro

# Copy source code into image
ADD --chown=repro:repro src ./src
ADD --chown=repro:repro data ./data
ADD --chown=repro:repro template ./template

# Allow executing dispatch.sh
RUN chmod +x ./src/dispatch.sh

# Expose env variables for dispatch.sh
ENV BASE_FOLDER="/home/repro"
ENV CODE_FOLDER="/home/repro/src"
ENV TEMPLATE_FOLDER="/home/repro/template"
ENV DATA_FOLDER="/home/repro/data"

# Number of predicted data tuples
ENV PREDICTION_COUNT=3

# Determines which prediction should be used.
# Available methods: exponential, prophet
ENV PREDICTION_METHOD=prophet

# Output folder. Can be changed by running a container
# Example usage: Docker Desktop local file system mount for immediate results
ENV OUTPUT_FOLDER="/home/repro/output"

RUN mkdir output

ENTRYPOINT ["/home/repro/src/dispatch.sh"]