from utils.CrudDb import CrudDb
from utils.DataLoader import DataLoader
from utils.EnsembleModel import EnsembleModel
from utils.FuncMonitor import FuncMonitor
from utils.ModelSchedualingCenter.DynamicSelect import DynamicSelect
from utils.ModelSchedualingCenter.DynamicWeight import DynamicWeight
from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor

#################################### load config ####################################
# monitor_center
monitor_center = MonitorCenter('configs\monitor.yml')
func_monitor = FuncMonitor(monitor_center)

# precision_sensor
precision_sensor = PrecisionSensor()

# crud_db
db = CrudDb('configs\db.yml')
db.BuildConnection()

# dataloader
dataloader = DataLoader('testDataSets/X_test.csv', 'testDataSets/y_test.csv')
dataloader.loadX()
dataloader.loadY()
input_datas_str, y_labels = dataloader.shuffle()

# ensemble_model
ensembel_model = EnsembleModel('configs/models.yml')

#################################### end of loading config ##############################

#################################### start of running ###################################
USED_ALGO = False
TEXT_ID = 1  # 用于标识当前的文本,按需修改
urlDictList = ensembel_model.getUrlDictList()

# 算法构建

# 参数设置
detect_round = 7

# 中间结果
cur_round_models_results = []
cur_round_ensemble_results = []

pre_round_error = 0x3f3f3f3f  # 上一轮的平均误差,初始值为一个很大的数
is_pre_delete = False  # 上一轮是否删除了模型
delete_threshold = 0.1  # 删除模型的阈值

for i in range(0, len(input_datas_str), detect_round):
    # 读入7个数据
    cur_input_datas_str = input_datas_str[i:i + detect_round]
    cur_y_labels = y_labels[i:i + detect_round]
    # print(f'cur_input_datas_str: {cur_input_datas_str}')
    # print(f'cur_y_labels: {cur_y_labels}')
    cur_models_num = ensembel_model.getModelsNum()
    # 中间结果清空
    cur_round_models_results = []
    cur_round_ensemble_results = []

    # 预测结果
    for j in range(detect_round):
        results, ensemble_predict_value = ensembel_model.run(
            cur_input_datas_str[j])
        print(f'results: {results}')
        cur_round_models_results.append(results)
        cur_round_ensemble_results.append(ensemble_predict_value)

    # print(f'cur_round_models_results: {cur_round_models_results}')
    # print(f'cur_round_ensemble_results: {cur_round_ensemble_results}')

    # 利用precision_sensor进行监控

    # 存储当前轮的每个模型结果,根据模型的名字存储

    models_results = []
    for j in range(cur_models_num):
        model_results = dict()
        model_results['model_name'] = ensembel_model.getModelName(j)
        model_results['results'] = []
        models_results.append(model_results)

    for j in range(detect_round):
        for k in range(cur_models_num):
            for model_result in cur_round_models_results[j]:
                if model_result['modelName'] == models_results[k]['model_name']:
                    models_results[k]['results'].append(
                        float(model_result['predictValue']))

    # print(f'models_results: {models_results}')

    for j in range(cur_models_num):
        precision_sensor.getData(
            cur_y_labels, models_results[j]['results'])
        precision_sensor.setMetricsModel('regression')
        precision_model_result = precision_sensor.calcPrecision()
        # print(
        #     f'{models_results[j]["model_name"]}, precision: {precision_model_result}')
        # 存储到数据库
        # 根据名字取得id
        for urlDict in urlDictList:
            if urlDict['modelName'] == models_results[j]['model_name']:
                model_id = urlDict['model_id']
                create_time = models_results[j]['create_time']
                break
        # 一共有5个metric_type
        for type in precision_sensor.metrics_types():
            query = f'insert into performance_metrics (model_id, metric_type, metric_value, window_id,text_id,create_time) values ({model_id}, "{type}", "{precision_model_result[type]}",{i / detect_round + 1} ,{TEXT_ID},"{create_time}")'
            # print(query)
            db.CreateData(query)

    precision_sensor.getData(cur_y_labels, cur_round_ensemble_results)
    precision_sensor.setMetricsModel('regression')
    precision_ensemble_result = precision_sensor.calcPrecision()
    print(
        f'ensembleModel, precision: {precision_ensemble_result}')

    if USED_ALGO:
        dynamic_weight = DynamicWeight(ensembel_model, db)
        dynamic_select = DynamicSelect(ensembel_model, db)
        dynamic_weight.algo(TEXT_ID, i / detect_round + 1)

db.CloseConnection()
