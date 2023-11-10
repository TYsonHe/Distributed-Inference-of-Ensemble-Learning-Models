from utils.EnsembleModel import EnsembleModel
from utils.CrudDb import CrudDb


class DynamicWeight:
    def __init__(self, ensemble_model: EnsembleModel, db: CrudDb) -> None:
        self.ensemble_model = ensemble_model
        self.db = db

    def get_weight(self, model_name: str) -> float:
        return self.ensemble_model.get_weight(model_name)

    def modify_weight(self, model_name: str, new_weight: float) -> None:
        self.ensemble_model.modify_weight(model_name, new_weight)

    def algo():
        pass
