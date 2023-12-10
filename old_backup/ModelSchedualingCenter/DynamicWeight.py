from utils.EnsembleModel import EnsembleModel
from utils.CrudDb import CrudDb


class DynamicWeight:
    def __init__(self, ensemble_model: EnsembleModel, db: CrudDb) -> None:
        self.ensemble_model = ensemble_model
        self.db = db

    def get_weight(self, model_name: str) -> float:
        return self.ensemble_model.get_weight(model_name)

    def modify_weight(self, model_name: str, new_weight: float) -> None:
        self.ensemble_model.modify_weight(model_name, new_weight)

    def algo(self, TEXT_ID: int, window_id: int) -> None:
        """
        计算所有model的前一段历史时间error
        """
        model_num = self.ensemble_model.getModelsNum()
        models_error = []
        for i in range(model_num):
            model_name = self.ensemble_model.getModelName(i)
            model_id = self.ensemble_model.get_model_id(model_name)
            # 从数据库中获取前一段历史时间的error
            sql = f"SELECT \
                        model_id,AVG( metric_value ) AS metric_avg \
                    FROM \
                        performance_metrics \
                    WHERE \
                        window_id={window_id} AND model_id = {model_id} AND text_id = {TEXT_ID-1};"
            res = self.db.RetrieveData(sql)
            print(res)
            model_error = dict()
            model_error['model_name'] = model_name
            model_error['model_id'] = model_id
            model_error['error'] = res[0]['metric_avg']
            models_error.append(model_error)
        print(models_error)
        # 找到最大和最小的error以及对应的model_id
        for model_error in models_error:
            if model_error['error'] == max([model_error['error'] for model_error in models_error]):
                max_error_model_id = model_error['model_id']
            if model_error['error'] == min([model_error['error'] for model_error in models_error]):
                min_error_model_id = model_error['model_id']

        # 更新weight，最大的error的weight减小，最小的error的weight增大
        max_error_model_weight = self.ensemble_model.get_weight(
            max_error_model_id)
        min_error_model_weight = self.ensemble_model.get_weight(
            min_error_model_id)
        print(f"更新前max_error_model_weight: {max_error_model_weight}")
        print(f"更新前min_error_model_weight: {min_error_model_weight}")
        # 更新weight,保持总和为1,额度为max_error_weight的25%
        temp = max_error_model_weight*0.25
        self.ensemble_model.modify_weight(
            max_error_model_id, max_error_model_weight-temp)
        self.ensemble_model.modify_weight(
            min_error_model_id, min_error_model_weight+temp)
        print(
            f"更新后max_error_model_weight: {self.ensemble_model.get_weight(max_error_model_id)}")
        print(
            f"更新后min_error_model_weight: {self.ensemble_model.get_weight(min_error_model_id)}")
