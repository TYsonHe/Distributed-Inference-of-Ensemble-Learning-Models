from utils.CrudDb import CrudDb
from utils.DataLoader import DataLoader
from utils.EnsembleModel import EnsembleModel
from utils.FuncMonitor import FuncMonitor
from utils.ModelSchedualingCenter.DynamicSelect import DynamicSelect
from utils.ModelSchedualingCenter.DynamicWeight import DynamicWeight
from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor
from utils.RequestEmitter.RequestEmitter import RequestEmitter

#################################### load config ####################################
# monitor_center
monitor_center = MonitorCenter('configs\monitor.yml')
func_monitor = FuncMonitor(monitor_center)

# precision_sensor
precision_sensor = PrecisionSensor()

# crud_db
db = CrudDb('configs\db.yml')
db.BuildConnection()

# ensemble_model
ensembel_model = EnsembleModel('configs/models.yml')

# request_emitter
request_emitter = RequestEmitter()
