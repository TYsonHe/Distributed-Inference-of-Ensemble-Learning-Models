from utils.DataLoader import DataLoader
from utils.EnsembleModel import EnsembleModel

dataloader = DataLoader('testDataSets/X_test.csv', 'testDataSets/y_test.csv')
dataloader.loadX()
dataloader.loadY()
inputDatas_str, yLabels = dataloader.shuffle()

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
preDeletedUrlDict = dict()

for i in range(0, len(inputDatas_str), detectRound):
    # 读入7个数据
    curInputDatas_str = inputDatas_str[i:i + detectRound]
    curYLabels = yLabels[i:i + detectRound]
    curModelsNum = ensembleModel.getModelsNum()
    # 中间结果清空
    curRoundModelsResults = []
    curRoundEnsembleResults = []

    # 预测结果
    for j in range(detectRound):
        results, ensemblePredictValue = ensembleModel.run(curInputDatas_str[j])
        curRoundModelsResults.append(results)
        curRoundEnsembleResults.append(ensemblePredictValue)
        totalModelsResults.append(results)
        totalEnsembleResults.append(ensemblePredictValue)

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
    # 还不能删除最后一个模型
    if not isPreDelete and curModelsNum > 1:
        for j in range(curModelsNum):
            if curRoundModelError[curRoundModelsResults[0][j]['modelName']] == max(curRoundModelError.values()):
                print("删除模型:", curRoundModelsResults[0][j]['modelName'])
                # 根据模型名字删除模型
                urlDict = [d for d in urlDictList if d['modelName']
                           == curRoundModelsResults[0][j]['modelName']][0]
                ensembleModel.deleteModel(urlDict)
                isPreDelete = True
                preDeletedUrlDict = urlDict
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
            ensembleModel.addModel(preDeletedUrlDict)
            ensembleModel.showCurrentModels()
            isPreDelete = False
            preRoundError = curEnsembleError
