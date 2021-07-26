from nkmodel import NKModel
from household import Household
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import pandas as pd

MEAN_INCOME = 33523
HOURS_WORKED_PER_WEEK = 40
HOURS_WORKED_PER_DAY = HOURS_WORKED_PER_WEEK / 7


def do_many_sims():
    prices = []

    for i in range(20):
        print(f"Iteration {i + 1}")
        model = NKModel(
            households=10,
            firms=5,
            household_wealth=1000,
            initial_price=10,
            initial_supply=1,
            firm_wealth=50000,
            max_wage=MEAN_INCOME / 365 / HOURS_WORKED_PER_DAY,
            sigma=0.6,
            phi=0.7,
            nu=0.2,
            seed=None
        )
        initial_price = None

        df = model.start(periods=100)
        for k, price in enumerate(df["price"]):
            if k == 0:
                initial_price = price
            if len(prices) <= k:
                prices.append([price / initial_price * 100])
            else:
                prices[k].append(price / initial_price * 100)

        del model

    final_prices = []
    u = []
    l = []
    for price in prices:
        mean = np.mean(price)
        std = np.std(price)

        final_prices.append(mean)
        u.append(mean + std)
        l.append(mean - std)

    plt.plot(final_prices, 'b', label="Price level indexed from t=0")
    plt.xlabel("Time")
    plt.ylabel("Price level")
    # plt.plot(price)
    plt.fill_between(range(len(final_prices)), l, u)
    plt.legend()
    plt.grid()
    plt.show()


def main():
    model = NKModel(
        households=10,
        firms=3,
        household_wealth=0,
        initial_price=1,
        initial_supply=100,
        firm_wealth=50000,
        max_wage=MEAN_INCOME / 365 / HOURS_WORKED_PER_DAY / 10,
        sigma=0.6,
        phi=0.1,
        nu=0.2,
        productivity=0.5,
        h_eta=0.2,
        h_rho=0.2,
        seed=0,

    )

    df = model.start(periods=500)
    print(df)
    rgdp = df["GDP"] / df["price"]
    price = df["price"]
    # plt.plot((rgdp / rgdp[0]).rolling(10).mean(), 'b', label="Real GDP")
    plt.plot(((1 + price.pct_change().dropna()).rolling(10).apply(scipy.stats.gmean) - 1) * 100, 'b',
             label="10 period rolling average inflation")

    money_supply = df["money_stock"]
    velocity = df["GDP"] / money_supply

    # plt.plot(((((1 + money_supply.pct_change()) + (1 + velocity.pct_change()) - (1 + rgdp.pct_change())).dropna().rolling(10).apply(scipy.stats.gmean) - 1) * 100), 'r', label='Inflation as implied by the Equation of Exchange')
    # plt.plot(((((1 + money_supply.pct_change()) + 1 - (1 + rgdp.pct_change())).dropna().rolling(10).apply(scipy.stats.gmean) - 1) * 100), 'purple', label='Inflation as implied by the QTM')
    # plt.plot(df["price"], 'b', label="Price level")
    # plt.plot(df["price"], 'r', label="Price Level")
    plt.xlabel("Time")
    plt.ylabel("Inflation (%)")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    pd.set_option("display.max_columns", None)
main()
