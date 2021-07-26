import mesa


class Government(mesa.Agent):
    def __init__(self, unique_id: int, model, bank):
        """

        :param unique_id:
        :param model: nkmodel.NKModel
        :param bank: central_bank.CentralBank
        """
        super().__init__(unique_id, model)

    def tax(self, household):
        household.bank.make_transfer(household, self, household.wealth / 2)
