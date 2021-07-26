import mesa
import statistics
import numpy as np

from commercial_bank import CommercialBank


class Firm(mesa.Agent):
    def __init__(self, unique_id: int, model, price: float, supply: float, bank: CommercialBank, seed=None):
        """

        :type model: nkmodel.NKModel
        """
        super().__init__(unique_id, model)
        if seed is not None:
            np.random.seed(seed)
        self.price = price
        self.desired_supply = supply
        self.bank = bank
        self.workers = []
        self.inventory = 0
        self.create_inventory()

    def clear_inventory(self):
        self.inventory = 0  # self.desired_supply  # PAIN, Implement labour and the labour market

    def create_inventory(self):
        # Since all workers have to be paid, even if we have to many workers for the required amount of supply, it will always be optimal to produce as much as we're able to
        # Holds true when cost of capital is 0
        # Which is all ways true in this model
        for household in self.workers:
            consumption, moneyy, labour = household.data
            self.inventory += household.wage * labour * household.productivity

    @property
    def mean_wage(self):
        return statistics.mean(list(map(lambda h: h.wage, self.workers)))

    @property
    def wealth(self):
        return self.bank.account_total(self)

    def hire(self, household):
        household.firm = self
        self.workers.append(household)

    def fire(self, household):
        household.firm = None
        self.workers.remove(household)

    def fire_all_workers(self):
        for household in self.workers:
            self.fire(household)

    @property
    def potential_inventory(self):
        # household.data = [consumption, money, labor]
        return sum(
            map(
                lambda household: household.wage * household.data[2] * household.productivity,
                self.workers
            )
        )

    def will_hire(self, household):
        if self.potential_inventory >= self.desired_supply:
            # The firm won't hire in the case it's already able to produce enough inventory
            return False
        consumption, money, labour = household.data
        added_supply = labour * household.wage * household.productivity
        if self.potential_inventory + added_supply < self.desired_supply:
            return True

        else:
            # Did some basic optimisation by hand to derive this rule
            shortage = self.desired_supply - self.potential_inventory
            excess = (self.potential_inventory + added_supply) - self.desired_supply
            return True  # self.price <= 1  # Assuming 1 £1 wage corresponds with £1 production

    def step(self, average_price):  # TODO: I currently violate the super classes type declaration
        """
        After every step, the firm will update its prices and its expectations of demand (i.e. its supply)

        """

        eta = np.random.uniform(0, self.model.h_eta)
        rho = np.random.uniform(0, self.model.h_rho)

        if self.inventory == 0 and self.price < average_price:
            self.price *= (1 + eta)

        if self.inventory > 0 and self.price >= average_price:
            self.price *= (1 - eta)

        if self.inventory == 0 and self.price >= average_price:
            self.desired_supply *= (1 + rho)

        if self.inventory > 0 and self.price < average_price:
            self.desired_supply *= (1 - rho)

        self.clear_inventory()
        self.fire_all_workers()
