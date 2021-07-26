import random
import statistics
from typing import Dict, Any

import mesa
import pandas as pd

from commercial_bank import CommercialBank
from government import Government
from household import Household
from firm import Firm
from central_bank import CentralBank


class NKModel(mesa.Model):
    def __init__(self,
                 households=10,
                 firms=2,
                 household_wealth=0,
                 initial_price=2,
                 initial_supply=1,
                 firm_wealth=1000,
                 max_wage=175000,
                 sigma=0.6,
                 phi=0.7,
                 nu=0.5,
                 h_eta=0.5,
                 h_rho=0.5,
                 seed=None,
                 productivity=None
                 ):
        super().__init__()
        if seed is not None:
            random.seed(seed)
        self.steps = 0
        self.sigma = sigma  # Coefficient for consumption utility
        self.phi = phi  # Coefficient for labour utility
        self.nu = nu  # Coefficient for money balance utility
        self.h_eta = h_eta  # Coefficient for price changes
        self.h_rho = h_rho  # Coefficient for supply changes

        # self.price = price
        self._price = []
        self.households = []
        self.firms = []
        self.central_bank = CentralBank(self.next_id(), self)
        self.commercial_banks = [CommercialBank(self.next_id(), self)]
        self.government = Government(self.next_id(), self, self.central_bank)
        for i in range(households):
            bank = random.choice(self.commercial_banks)
            household = Household(self.next_id(), self, wage=self.random_income(alpha=0.63, beta=0.82) * max_wage,
                                  productivity=productivity, bank=bank, seed=seed)
            self.households.append(household)
            bank.open_account(household, initial_deposit=household_wealth)

        for i in range(firms):
            bank = random.choice(self.commercial_banks)
            firm = Firm(self.next_id(), self, price=initial_price, supply=initial_supply, bank=bank, seed=seed)

            self.firms.append(firm)
            bank.open_account(firm, initial_deposit=firm_wealth)

        # for household in self.households:
        #     firm = random.choice(self.firms)
        #     firm.hire(household)

    @property
    def price(self):
        return statistics.mean([firm.price for firm in self.firms])

    def start(self, periods=10):
        df = []
        for i in range(periods):
            # if i >= 50:
            #     for household in self.households:
            #         household.bank.make_transfer(household, self.government, household.wealth)
            #         household.wage /= 5
            data = self.step()
            df.append(data)

        return pd.json_normalize(df)

    def step(self) -> Dict[str, Any]:
        for household in self.households:
            household.perform_optimisation()

        random.shuffle(self.households)

        for household in self.households:
            firm = random.choice(self.firms)
            if firm.will_hire(household):
                firm.hire(household)

        for firm in self.firms:
            firm.create_inventory()

        for household in self.households:
            household.step()

        average_price = self.price
        for firm in self.firms:
            firm.step(average_price)

        self.steps += 1
        print(self.steps)
        data = self.collect_data()
        self.central_bank.feed_data(data)
        self.central_bank.do_targeting()
        data = self.collect_data()
        self.central_bank.feed_data(data)

        return data

    def collect_data(self):
        consumption_data = []
        money_stock_data = []
        labour_data = []
        firm_wealth = []
        supply_data = []
        incomes = []

        employed = []

        total_money_supply = 0

        for household in self.households:
            consumption, money, labour = household.data
            consumption_data.append(consumption)
            money_stock_data.append(money)
            labour_data.append(labour)
            incomes.append(labour * household.wage * 365)
            employed.append(int(labour > 0))
            total_money_supply += money
        for firm in self.firms:
            total_money_supply += firm.wealth
            firm_wealth.append(firm.wealth)
            supply_data.append(firm.desired_supply)

        # total_money_supply += self.government.wealth

        return {
            "GDP": sum(consumption_data) * self.price,
            "money_stock": sum(money_stock_data),  # statistics.mean(money_stock_data),
            "labour": statistics.mean(labour_data),
            "firm_wealth": statistics.mean(firm_wealth),
            "money_supply": total_money_supply,
            "mean_income": statistics.mean(incomes),
            "price": self.price,
            "supply": statistics.mean(supply_data),
            "employment": statistics.mean(employed)
        }

    @staticmethod
    def random_income(alpha, beta):
        return NKModel.income_function(random.random(), alpha, beta)

    @staticmethod
    def income_cdf(x, alpha, beta):
        return (1 - (1 - x) ** alpha) ** (1 / beta)

    @staticmethod
    def inverse_income_cdf(x, alpha, beta):
        return 1 - (1 - x ** beta) ** (1 / alpha)

    @staticmethod
    def income_function(x, alpha, beta):
        return alpha / beta * (1 - (1 - x) ** alpha) ** (1 / beta - 1) * (1 - x) ** (-(1 - alpha))
