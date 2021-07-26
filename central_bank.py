from bank import Bank
import numpy as np
import pandas as pd


class CentralBank(Bank):
    INFLATION_TARGET = 0.02

    def __init__(self, unique_id: int, model):
        """

        :type model: nkmodel.NKModel
        """
        super().__init__(unique_id, model)
        self.model = model
        self.data = None  # type: pd.DataFrame

    def output(self):
        return  # TODO

    def do_targeting(self):
        if len(self.data) < 50:
            return  # Do nothing

        prev_money_supply_growth = self.data["money_stock"].pct_change().iloc[-1]
        rgdp = self.data["GDP"] / self.data["price"]
        necessary_growth = CentralBank.INFLATION_TARGET  # - rgdp.pct_change().iloc[-1]
        increase = necessary_growth - prev_money_supply_growth
        multiplier = 1 + increase
        print(f"{np.floor(increase * 100)}%")
        total_increase = self.data["money_stock"].iloc[-1] * increase
        if not np.isnan(multiplier):
            for household in self.model.households:
                # household.bank.make_transfer(household, self, -household.wealth * increase)
                household.bank.make_transfer(household, self, -total_increase / len(
                    self.model.households))  # -household.wealth * increase)

    def feed_data(self, data):
        if self.data is not None:
            self.data = self.data.append(data, ignore_index=True)
        else:
            self.data = pd.json_normalize(data)
