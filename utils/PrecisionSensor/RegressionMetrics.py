import numpy as np


class RegressionMetrics:
    '''
    types:numpy.ndarray
    y_true: Ground truth (correct) target values.
    y_pred: Estimated target values.
    '''

    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def mean_absolute_error(self):
        return np.mean(np.abs(self.y_true - self.y_pred))

    def mean_squared_error(self):
        return np.mean((self.y_true - self.y_pred) ** 2)

    def root_mean_squared_error(self):
        return np.sqrt(self.mean_squared_error())

    def mean_absolute_percentage_error(self):
        return np.mean(np.abs((self.y_true - self.y_pred) / self.y_true)) * 100

    def r_squared(self):
        ss_res = np.sum((self.y_true - self.y_pred) ** 2)
        ss_tot = np.sum((self.y_true - np.mean(self.y_true)) ** 2)
        return 1 - (ss_res / ss_tot)

    def calcAll(self):
        result = {}
        result['mae'] = self.mean_absolute_error()
        result['mse'] = self.mean_squared_error()
        result['rmse'] = self.root_mean_squared_error()
        result['mape'] = self.mean_absolute_percentage_error()
        result['r2'] = self.r_squared()
        return result


# test
if __name__ == "__main__":
    y_true = np.array([3, -0.5, 2, 7])
    y_pred = np.array([2.5, 0.0, 2, 8])
    regressionMetrics = RegressionMetrics(y_true, y_pred)
    print(regressionMetrics.mean_absolute_error())
    print(regressionMetrics.mean_squared_error())
    print(regressionMetrics.root_mean_squared_error())
    print(regressionMetrics.mean_absolute_percentage_error())
    print(regressionMetrics.r_squared())
