from utils.EnsembleModel import EnsembleModel
from utils.CrudDb import CrudDb


class DynamicSelect:
    def __init__(self, ensemble_model: EnsembleModel, db: CrudDb) -> None:
        self.ensemble_model = ensemble_model
        self.db = db
