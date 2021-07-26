from typing import Dict

import mesa

from bank import Bank


class CommercialBank(Bank):
    def __init__(self, unique_id: int, model):
        """

        :type model: nkmodel.NKModel
        """
        super().__init__(unique_id, model)
