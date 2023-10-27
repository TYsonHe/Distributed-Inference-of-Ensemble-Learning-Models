from utils.PrecisionSensor.ClassificationMetrics import ClassificationMetrics
from utils.PrecisionSensor.RegressionMetrics import RegressionMetrics


class PrecisionSensor:
    def __init__(self) -> None:
        self.metricsModel = None

    def getData(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def setMetricsModel(self, model: str):
        if model == 'Classification':
            self.metricsModel = ClassificationMetrics(self.y_true, self.y_pred)
        elif model == 'Regression':
            self.metricsModel = RegressionMetrics(self.y_true, self.y_pred)
        print(f'PrecisionSensor: {model} metricsModel is set.')

    def calcPrecision(self):
        if self.metricsModel is None:
            print('PrecisionSensor: metricsModel is not set.')
            return
        elif isinstance(self.metricsModel, ClassificationMetrics):
            return self.metricsModel.calcAll()
        elif isinstance(self.metricsModel, RegressionMetrics):
            return self.metricsModel.calcAll()
