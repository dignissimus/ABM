from typing import Dict

import mesa


class DepositAccountEntry:
    def __init__(self, amount=0):
        self.amount = amount


class Bank(mesa.Agent):
    def __init__(self, unique_id: int, model):
        """

        :type model: nkmodel.NKModel
        """
        super().__init__(unique_id, model)
        self.deposits = {}  # type: Dict[int, DepositAccountEntry]

    def open_account(self, agent: mesa.Agent, initial_deposit=0):
        self.deposits[agent.unique_id] = DepositAccountEntry(initial_deposit)

    def account_total(self, agent: mesa.Agent):
        return self.deposits[agent.unique_id].amount

    def relegate_cash(self, agent: mesa.Agent, amount):
        self.deposits[agent.unique_id].amount -= amount

    def make_transfer(self, source: mesa.Agent, destination: mesa.Agent, amount):
        if destination.unique_id not in self.deposits:
            self.open_account(destination)
        self.deposits[source.unique_id].amount -= amount
        self.deposits[destination.unique_id].amount += amount
