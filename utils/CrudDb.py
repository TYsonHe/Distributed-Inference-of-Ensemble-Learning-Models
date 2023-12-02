import pymysql
import yaml
from pymysqlpool import ConnectionPool


class CrudDb:
    def __init__(self, configPath: str) -> None:
        """
        :param conn: 数据库连接
        :param cur: 数据库游标(dict类型)
        """
        self.configPath = configPath
        self.loadConfig()
        self.pool = ConnectionPool(host=self.host, user=self.user, password=self.password, db=self.dbname,
                                   port=self.port, charset=self.charset, cursorclass=pymysql.cursors.DictCursor)

    def loadConfig(self) -> None:
        with open(self.configPath, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.host = config['host']
        self.user = config['user']
        self.password = config['password']
        self.dbname = config['dbname']
        self.port = config['port']
        self.charset = config['charset']

    def RetrieveData(self, query):
        """
        :param query: 查询语句
        :return: 查询结果
        """
        try:
            conn = self.pool.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
            conn.close()
            return result
        except Exception as e:
            print(f'RetrieveFailed, CatchError:{e}')
            return 'RetrieveFailed'

    def CreateData(self, query):
        """
        :param query: 插入语句
        :return: 插入结果
        """
        try:
            conn = self.pool.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
            conn.close()
            return 'CreateSuccess'
        except Exception as e:
            print(f'CreateFailed, CatchError:{e}')
            return 'CreateFailed'

    def UpdateData(self, query):
        """ 
        :param query: 更新语句
        :return: 更新结果
        """
        try:
            conn = self.pool.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
            conn.close()
            return 'UpdateSuccess'
        except Exception as e:
            print(f'UpdateFailed, CatchError:{e}')
            return 'UpdateFailed'

    def DeleteData(self, query):
        """
        :param query: 删除语句
        :return: 删除结果
        """
        try:
            conn = self.pool.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
            conn.close()
            return 'DeleteSuccess'
        except Exception as e:
            print(f'DeleteFailed, CatchError:{e}')
            return 'DeleteFailed'

    def Execute(self, query, *values):
        """
        :param query: SQL语句
        :param values: SQL语句中的参数值
        :return: 执行结果
        """
        try:
            conn = self.pool.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
            conn.close()
            return 'ExecuteSuccess'
        except Exception as e:
            print(f'ExecuteFailed, CatchError:{e}')
            return 'ExecuteFailed'


# test
if __name__ == '__main__':
    crudDb = CrudDb('configs\db.yml')
    result = crudDb.RetrieveData('desc models')
    print(result)
