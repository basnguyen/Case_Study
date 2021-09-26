# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 18:24:22 2021

@author: Nguye
"""


import warnings
import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
plt.style.use("fivethirtyeight")
import pandas as pd
import matplotlib
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

import sys

orig_stdout = sys.stdout
f = open("PROPHET_LOG.txt", "w")
sys.stdout = f


matplotlib.rcParams["axes.labelsize"] = 14
matplotlib.rcParams["xtick.labelsize"] = 12
matplotlib.rcParams["ytick.labelsize"] = 12
matplotlib.rcParams["text.color"] = "k"

embi_data = pd.read_csv("./Data/EMBI_cleaned.csv", index_col=[0, 1])
pictet_data = pd.read_csv("./Data/Pictet_Spread_data.csv", index_col=[0, 1])

# List of countries
list_of_countries = pd.Series(
    pictet_data.index.get_level_values(0),
).drop_duplicates(keep="first")
list_of_countries = ["ARE", "ARE"]

# Output Cross-validation
output_cv = pd.DataFrame(
    columns=[
        "country",
        "rmse_avg",
        "rmse_std",
        "mae_avg",
        "mae_std",
        "mape_avg",
        "mape_std",
    ]
)

for country_i in list_of_countries:
    print(f"Fitting country {country_i}")
    country_data = pictet_data.loc[country_i, :]
    country_data = country_data.reset_index()
    country_data["date"] = pd.to_datetime(country_data["date"], format="%d/%m/%Y")

    from pylab import rcParams

    rcParams["figure.figsize"] = 18, 8
    country_data = country_data.rename(columns={"date": "ds", "value": "y"})
    country_model = Prophet(interval_width=0.95)
    country_model.fit(country_data)

    country_forecast = country_model.make_future_dataframe(periods=36, freq="MS")
    country_forecast = country_model.predict(country_forecast)

    se = np.square(
        country_forecast.loc[1 : len(country_data), "yhat"] - country_data["y"]
    )
    mse = np.mean(se)
    rmse = np.sqrt(mse)
    print(f"RMSE : {rmse}")

    # plt.figure(figsize=(18, 6))
    # ax = country_model.plot(country_forecast, xlabel = 'Date', ylabel = 'Bond spreads (bips)')
    # plt.savefig(f'./Plots/Prophet/{country_i}_prediction.pdf')

    # Train on two third of set, cross-validation on 1 year of data
    initial_days = int(len(country_data["ds"]) * 31 * 0.6)
    cv_results = cross_validation(
        model=country_model,
        initial=f"{initial_days} days",
        period=f"31 days",
        horizon="365 days",
    )
    sys.stdout = f
    output_cv_i = performance_metrics(cv_results)

    output_cv_i.to_csv(f"./Plots/Prophet/{country_i}_cv_results.csv")

    output_cv_i = pd.DataFrame(
        [
            [
                country_i,
                output_cv_i["rmse"].mean(),
                output_cv_i["rmse"].std(),
                output_cv_i["mae"].mean(),
                output_cv_i["mae"].std(),
                output_cv_i["mape"].mean(),
                output_cv_i["mape"].std(),
            ]
        ],
        columns=[
            "country",
            "rmse_avg",
            "rmse_std",
            "mae_avg",
            "mae_std",
            "mape_avg",
            "mape_std",
        ],
    )
    output_cv = output_cv.append(output_cv_i)

output_cv.to_csv(f"./cv_aggregated_results.csv")
sys.stdout = orig_stdout
f.close()
