# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 18:24:22 2021

@author: Nguye
"""


import warnings
import itertools
import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
plt.style.use("fivethirtyeight")
import pandas as pd
import statsmodels.api as sm
import matplotlib
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf

import sys

orig_stdout = sys.stdout
f = open("SARIMA_LOG.txt", "w")
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

for country_i in list_of_countries:
    print(f"Fitting country {country_i}")
    country_data = pictet_data.loc[country_i, :]
    country_data = country_data.reset_index()
    country_data["date"] = pd.to_datetime(country_data["date"], format="%d/%m/%Y")
    country_data.set_index("date", inplace=True)
    y = country_data["value"].resample("MS").mean()

    from pylab import rcParams

    rcParams["figure.figsize"] = 18, 8

    decomposition = sm.tsa.seasonal_decompose(y, model="additive")
    fig = decomposition.plot()
    # plt.show()
    plt.savefig(f"./Plots/SARIMA/{country_i}_decomposition.pdf")
    plt.close()

    # Dicker Fuller rTest
    dftest = adfuller(y)
    print("Dicker-Fuller Test")
    dfoutput = pd.Series(
        dftest[0:4],
        index=[
            "Test Statistic",
            "p-value",
            "#Lags Used",
            "Number of Observations Used",
        ],
    )
    for key, value in dftest[4].items():
        dfoutput["Critical Value (%s)" % key] = value
    print(dfoutput)

    # Selecting D
    """
    y_diff=y.diff(periods=4).dropna()
    # Dicker Fulle rTest
    dftest = adfuller(y_diff)
    print('Dicker-Fuller Test')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value',"#Lags Used",'Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Cirtical Value (%s)' %key] = value
    print (dfoutput)
    """

    # Plot auto and partial autocorrelation
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    plot_acf(y, ax=ax1, lags=10)

    ax2 = fig.add_subplot(2, 1, 2)
    plot_pacf(y, ax=ax2, lags=10)

    plt.savefig(f"./Plots/SARIMA/{country_i}_acf_pacf.pdf")

    # Select best SARIMAX Model
    p = d = q = range(0, 3)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
    ans = []
    for comb in pdq:
        for combs in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(
                    y,
                    order=comb,
                    seasonal_oder=combs,
                    enforce_stationariy=False,
                    enforce_inveritilibty=False,
                )
                output = mod.fit()

                ans.append([comb, combs, output.aic])

                # print('ARIMA {} x {}12 : AIC Calculated ={}'.format(comb, combs, output.aic))

            except:
                continue

    ans_df = pd.DataFrame(ans, columns=["pdq", "pdqs", "aic"])
    print("Best model :")
    print(ans_df.loc[ans_df["aic"].idxmin()])

    pdq = ans_df.loc[ans_df["aic"].idxmin()][0]
    pdqs = ans_df.loc[ans_df["aic"].idxmin()][1]

    pdq = (1, 1, 1)
    pdqs = (0, 0, 0, 12)

    mod = sm.tsa.statespace.SARIMAX(
        y,
        order=pdq,
        seasonal_order=pdqs,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    results = mod.fit()

    print(results.summary().tables[1])

    results.plot_diagnostics(figsize=(16, 8))
    plt.savefig(f"./Plots/SARIMA/{country_i}_resuts.pdf")
    plt.close()

    max_plot_length = 72 if len(y) > 72 else len(y)

    pred = results.get_prediction(start=y.index[-max_plot_length], dynamic=False)
    pred_ci = pred.conf_int()

    observed_plot = y[-72:]

    fig = plt.figure()

    ax = observed_plot.plot(label="observed")
    pred.predicted_mean.plot(
        ax=ax, label="One-step ahead Forecast", alpha=0.7, figsize=(14, 7)
    )

    # pred_uc.predicted_mean.plot(ax=ax, label='Forecast')

    ax.fill_between(
        pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color="k", alpha=0.2
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Bond spreads (bips)")
    plt.legend()

    plt.savefig(f"./Plots/SARIMA/{country_i}_prediction.pdf")

    y_forecasted = pred.predicted_mean
    observed_plot

    # Compute the mean square error
    mse = ((y_forecasted - observed_plot) ** 2).mean()
    print("MSE {}".format(round(mse, 2)))
    print("RMSE {}".format(round(np.sqrt(mse), 2)))


sys.stdout = orig_stdout
f.close()
