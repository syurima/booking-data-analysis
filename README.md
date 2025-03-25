# Data Analysis Project

This project involves data analysis and visualization using various machine learning models. The data is gathered from CSV files and analyzed using Python libraries such as pandas, numpy, matplotlib, seaborn, and scikit-learn.


## Requirements

- Python 3.x
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn

## Installation

1. Clone the repository

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the `gather_data.py` script to gather data:
    ```sh
    python gather_data.py
    ```
    The script will generate random requests to booking and save listing data as csv files to the `data/` directory.
    By default, the script generates 20 requests for Amsterdam.
    The city for which requests are generated and the default number of requests can be changed in the `gather_data.py` script or passed as command line arguments.

    ```sh
    python gather_data.py --city "New York" --requests 100
    ```
    or
    ```sh
    python gather_data.py -c "New York" -r 100
    ```
    

2. Open the `data_analysis.ipynb` notebook to perform data analysis and visualization.

## Data Analysis

The `data_analysis.ipynb` notebook includes the following steps:

1. Loading and preprocessing data.
2. Visualizing data using matplotlib and seaborn.
3. Splitting data into training and testing sets.
4. Applying various machine learning models:
    - Linear Regression
    - Polynomial Regression
    - Random Forest Regressor
    - K-Nearest Neighbors Regressor
5. Evaluating model performance using metrics such as mean absolute error, mean squared error, and r2 score.

## Results

The results of the data analysis and model performance are saved in the `graphs/` directory.
Additionaly, the results are further analysed in the `raport.pdf` file (written in Polish).