import numpy as np


class ClassificationMetrics:
    '''
    types:numpy.ndarray
    y_true: Ground truth (correct) target values.
    y_pred: Estimated target values.
    '''

    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred
        self.tp = np.sum((self.y_true == 1) & (self.y_pred == 1))
        self.tn = np.sum((self.y_true == 0) & (self.y_pred == 0))
        self.fp = np.sum((self.y_true == 0) & (self.y_pred == 1))
        self.fn = np.sum((self.y_true == 1) & (self.y_pred == 0))

    def accuracy(self):
        return (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn)

    def precision(self):
        return self.tp / (self.tp + self.fp)

    def recall(self):
        return self.tp / (self.tp + self.fn)

    def f1_score(self):
        p = self.precision()
        r = self.recall()
        return 2 * p * r / (p + r)

    def confusionMatrix(self):
        return np.array([[self.tp, self.fp], [self.fn, self.tn]])

    def calcAll(self):
        result = {}
        result['accuracy'] = self.accuracy()
        result['precision'] = self.precision()
        result['recall'] = self.recall()
        result['f1_score'] = self.f1_score()
        result['confusionMatrix'] = self.confusionMatrix()
        return result


# test
if __name__ == "__main__":
    y_true = np.array([1, 0, 1, 1, 0, 1])
    y_pred = np.array([1, 0, 1, 0, 0, 1])
    classificationMetrics = ClassificationMetrics(y_true, y_pred)
    print(classificationMetrics.accuracy())
    print(classificationMetrics.precision())
    print(classificationMetrics.recall())
    print(classificationMetrics.f1_score())
    print(classificationMetrics.confusionMatrix())
