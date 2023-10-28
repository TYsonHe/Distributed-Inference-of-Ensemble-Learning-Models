from utils.DataLoader import DataLoader
from utils.EnsembleModel import EnsembleModel
from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor
from utils.FuncMonitor import FuncMonitor
from utils.CrudDb import CrudDb

#################################### load config ####################################
# monitor_center
monitor_center = MonitorCenter('configs\monitor.yml')
funcMonitor = FuncMonitor(monitor_center)

# precision_sensor
precision_sensor = PrecisionSensor()

# crud_db
db = CrudDb('configs\db.yml')

# dataloader
dataloader = DataLoader('testDataSets/X_test.csv', 'testDataSets/y_test.csv')
dataloader.loadX()
dataloader.loadY()
inputDatas_str, yLabels = dataloader.shuffle()

# ensemble_model
ensembel_model = EnsembleModel('configs/models.yml')

#################################### end of loading config ##############################

#################################### start of running ##################################
