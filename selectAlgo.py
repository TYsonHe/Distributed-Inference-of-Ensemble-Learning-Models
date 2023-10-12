from utils.EnsembleModel import EnsembleModel
import pandas as pd
import numpy as np

# 读入数据,并将数据转换为字符串类型
inputDatas = pd.read_csv('testDataSets/X_test.csv')
inputDatas = np.array(inputDatas)
inputDatas = inputDatas.tolist()
inputDatas_str = [','.join(map(str, row)) for row in inputDatas]


yLabels = pd.read_csv('testDataSets/y_test.csv')
yLabels = np.array(yLabels)
yLabels = yLabels.tolist()
yLabels = [float(i[0]) for i in yLabels]

# 创建集成模型
ensembleModel = EnsembleModel('configs/models.yml')
urlDictList = ensembleModel.getUrlDictList()

# 算法构建
# 全局结果
totalModelsResults = []
totalEnsembleResults = []
# 参数设置
detectRound = 7

# 中间结果
curRoundModelsResults = []
curRoundEnsembleResults = []

preRoundError = 0x3f3f3f3f  # 上一轮的平均误差,初始值为一个很大的数

isPreDelete = False  # 上一轮是否删除了模型
preDeltedUrlDict = dict()

for i in range(0, len(inputDatas_str), detectRound):
    # 读入7个数据
    curInputDatas_str = inputDatas_str[i:i+detectRound]
    curYLabels = yLabels[i:i+detectRound]
    curModelsNum = ensembleModel.getModelsNum()

    # 预测结果
    for j in range(detectRound):
        results, ensembelPredictValue = ensembleModel.run(curInputDatas_str[j])
        curRoundModelsResults.append(results)
        curRoundEnsembleResults.append(ensembelPredictValue)
        totalModelsResults.append(results)
        totalEnsembleResults.append(ensembelPredictValue)

    # 计算一轮中每个模型的平均误差
    curRoundModelError = dict()
    for j in range(curModelsNum):
        curModelError = 0
        for k in range(detectRound):
            curModelError += abs(
                float(curRoundModelsResults[k][j]['predictValue']) - curYLabels[k])
        curModelError /= detectRound
        print(curRoundModelsResults[0][j]
              ['modelName'], "的平均误差为:", curModelError)
        curRoundModelError[curRoundModelsResults[0][j]
                           ['modelName']] = curModelError

    # 计算一轮中集成模型的平均误差
    curEnsembleError = 0
    for j in range(detectRound):
        curEnsembleError += abs(
            curRoundEnsembleResults[j] - curYLabels[j])
    curEnsembleError /= detectRound
    print("集成模型的平均误差为:", curEnsembleError)

    # 如果上一轮没有删除模型,则删除表现最差的模型
    if not isPreDelete:
        for j in range(curModelsNum):
            if curRoundModelError[curRoundModelsResults[0][j]['modelName']] == max(curRoundModelError.values()):
                print("删除模型:", curRoundModelsResults[0][j]['modelName'])
                # 根据模型名字删除模型
                urlDict = [d for d in urlDictList if d['modelName']
                           == curRoundModelsResults[0][j]['modelName']][0]
                ensembleModel.deleteModel(urlDict)
                isPreDelete = True
                preDeltedUrlDict = urlDict
                break
        # 展示当前模型
        ensembleModel.showCurrentModels()
        preRoundError = curEnsembleError

    # 如果上一轮删除了模型,则看新的平均误差,若比上一次好,则保留更改,否则恢复上一次删除的模型
    else:
        if curEnsembleError < preRoundError:
            print("保留更改")
            isPreDelete = False
            preRoundError = curEnsembleError
        else:
            print("恢复更改")
            ensembleModel.addModel(preDeltedUrlDict)
            ensembleModel.showCurrentModels()
            isPreDelete = False
            preRoundError = curEnsembleError
