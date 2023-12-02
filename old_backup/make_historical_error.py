from utils.EnsembleModel import EnsembleModel
from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor
import os

if __name__ == '__main__':
    print(os.getcwd())
    ensemble_model = EnsembleModel('./configs/models.yml')
    precision_sensor = PrecisionSensor()
    # 读取X_test.csv的每一行，只需要字符串
    with open('../testDataSets/X_test.csv', 'r') as f:
        lines = f.readlines()
    # 去掉第一行
    lines = lines[1:]
    # 去掉换行符
    X = [line.strip() for line in lines]
    with open('../testDataSets/y_test.csv', 'r') as f:
        y_labels = f.readlines()
    zip_data = zip(X, y_labels)
    for i, (X, y) in enumerate(zip_data):
        print(f'X: {X}, y: {y}')
        ensemble_model.async_run(X)
