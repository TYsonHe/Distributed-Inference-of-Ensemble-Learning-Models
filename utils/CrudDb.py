import pymysql
import yaml


class CrudDb:
    def __init__(self, configPath: str) -> None:
        """
        :param conn: 数据库连接
        :param cur: 数据库游标(dict类型)
        """
        self.conn = None
        self.cur = None
        self.configPath = configPath
        self.loadConfig()

    def loadConfig(self) -> None:
        with open(self.configPath, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.host = config['host']
        self.user = config['user']
        self.password = config['password']
        self.dbname = config['dbname']
        self.port = config['port']
        self.charset = config['charset']

    def BuildConnection(self):
        """
        :param host: 数据库地址
        :param user: 用户名
        :param password: 密码
        :param dbname: 数据库名
        :param port: 端口号
        :param charset: 字符集
        :return: None
        """
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                    db=self.dbname, port=self.port, charset=self.charset)
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def CloseConnection(self):
        """
        释放数据库连接
        :return: None
        """
        self.cur.close()
        self.conn.close()

    def RetrieveData(self, query):
        """
        :param query: 查询语句
        :return: 查询结果
        """
        try:
            self.cur.execute(query)
            result = self.cur.fetchall()
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
            self.cur.execute(query)
            # 这里要注意，插入数据后要commit才能生效
            self.conn.commit()
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
            self.cur.execute(query)
            # 这里要注意，更新数据后要commit才能生效
            self.conn.commit()
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
            self.cur.execute(query)
            # 这里要注意，删除数据后要commit才能生效
            self.conn.commit()
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
            self.cur.execute(query, values)
            self.conn.commit()  # 根据操作类型，需要commit才能生效
            return 'ExecuteSuccess'
        except Exception as e:
            print(f'ExecuteFailed, CatchError:{e}')
            return 'ExecuteFailed'


# test
if __name__ == '__main__':
    crudDb = CrudDb('configs\db.yml')
    crudDb.BuildConnection()
    result = crudDb.RetrieveData('desc models')
    crudDb.CloseConnection()
    print(result)
