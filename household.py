import random

import mesa
import numpy as np
import scipy.optimize

from commercial_bank import CommercialBank


class Household(mesa.Agent):
    def __init__(self, unique_id: int, model, wage, productivity: float, bank: CommercialBank, seed):
        """

        :type model: nkmodel.NKModel
        """
        super().__init__(unique_id, model)
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.wage = wage
        self.model = model
        self.productivity = productivity
        self.bank = bank
        self.firm = None
        self.data = None

    @property
    def wealth(self):
        return self.bank.account_total(self)

    def perform_optimisation(self):
        x = self.consumption_money_labour()
        consumption, money_stock, labour = x[0]

        self.data = [consumption, money_stock, labour]
        return self.data

    @property
    def is_employed(self):
        return bool(self.firm)

    def step(self):
        prev_wealth = self.wealth
        if not self.is_employed:
            actual_wage = self.wage
            self.wage = 0
            consumption, money, labour = self.perform_optimisation()
            self.wage = actual_wage
            if labour != 0:
                # raise Exception(f"labour = {labour} is not 0 for an unemployed worker")
                # labour = 0
                pass
        else:
            consumption, money, labour = self.data
            self.bank.make_transfer(self.firm, self, labour * self.wage)

        chosen_firm = random.choice(self.model.firms)

        supply_constrained_consumption = min(consumption, chosen_firm.inventory)
        price_constrained_consumption = min(supply_constrained_consumption,
                                            (consumption * self.model.price) / chosen_firm.price)
        self.bank.make_transfer(self, chosen_firm, price_constrained_consumption * chosen_firm.price)
        chosen_firm.inventory -= price_constrained_consumption

        self.data = [price_constrained_consumption,
                     prev_wealth + labour * self.wage - price_constrained_consumption * chosen_firm.price, labour]

        return self.data

    def consumption_money_labour(self, beta=0.1, periods=1):
        # TODO: Bounds
        # noinspection PyTypeChecker
        result = scipy.optimize.minimize(
            fun=self.intertemporal_utility_helper,
            x0=np.repeat([0, self.wealth, 0], periods),  # Initially, no consumption, save everything, don't work
            args=[beta, periods],
            constraints=self.generate_intertemporal_constraints(periods),
            bounds=[
                       (0, 10**6),
                       (0, 10**6),
                       (0, 24)
                   ] * periods
        )

        # for constraint in self.generate_intertemporal_constraints(periods):
        #     print(constraint["fun"](result.x, True))
        # print(result.x.reshape(periods, 3))
        # exit()

        return result.x.reshape(periods, 3)

    def generate_intertemporal_constraints(self, periods):
        constraints = []
        for period in range(periods):
            if period == 0:
                def constraint_helper(args, debug=False):
                    args = args.reshape(periods, 3)[period]
                    return self.budget_constraint_helper(args, self.wealth, debug)
            else:
                def constraint_helper(args, debug=False):
                    x = args.reshape(periods, 3)
                    args = x[period]
                    return self.budget_constraint_helper(args, x[period - 1][1], debug)

            constraints.append(constraint_helper)
        return [
            {
                "type": "eq",
                "fun": constraint,
            } for constraint in constraints
        ]

    def budget_constraint_helper(self, args, wealth, debug):
        return self.budget_constraint(*args, wealth, debug)

    def intertemporal_utility_helper(self, args, params):
        beta, periods = params
        return -self.intertemporal_utility(args.reshape(periods, 3), beta=beta, periods=periods)

    def budget_constraint(self, consumption, money_stock, labour, wealth, debug):
        if debug:
            print("dbg", wealth, money_stock, consumption, labour)
        return (self.wage * labour + wealth) - (consumption * self.model.price + money_stock)

    def consumption(self):
        pass

    def labour(self):
        pass

    def intertemporal_utility(self, x, beta, periods):
        consumption, money_stock, labour = x[0]
        if periods == 1:
            return self.static_utility(consumption, money_stock, labour)
        else:
            return self.static_utility(
                consumption, money_stock, labour
            ) + beta * self.intertemporal_utility(x[1:], beta, periods - 1)

    def static_utility(self, consumption: float, money_stock: float, labour: float):
        return (
                (consumption ** (1 - self.model.sigma)) / (1 - self.model.sigma)
                - (labour ** (1 + self.model.phi)) / (1 + self.model.phi)
                + ((money_stock / self.model.price) ** (1 - self.model.nu)) / (1 - self.model.nu)
        )

    @staticmethod
    def utility(consumption: float, labour: float, beta=1, time=0):
        pass
