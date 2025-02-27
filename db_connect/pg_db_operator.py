from config import config_
from logger import log
# import psycopg2
# from psycopg2.extras import DictCursor
from psycopg2.pool import SimpleConnectionPool
import os


class PgDbOperator:
    def __init__(self):
        self.config = config_
        self.host = os.getenv('DB_HOST', self.config.get('postgresql', 'host'))
        self.port = os.getenv('DB_PORT', self.config.get('postgresql', 'port'))
        self.user = os.getenv('DB_USER', self.config.get('postgresql', 'user'))
        self.password = os.getenv('DB_PASSWORD', self.config.get('postgresql', 'password'))
        self.database = os.getenv('DB_DATABASE', self.config.get('postgresql', 'database'))

        # 尝试连接数据库
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
            )
        except Exception as e:
            log.critical(f"连接数据库错误: {e}")
            raise
        self.conn = self.pool.getconn()
        self.cur = self.conn.cursor()

    def switch_schema(self, schema_name: str) -> None:
        """
        切换模式
        :param schema_name:模式名称
        :return:无
        """
        self.cur.execute(f"SET search_path TO {schema_name}")
        self.conn.commit()

    def insert(self, table_name: str, data_dict: dict) -> None:
        """
        插入单行数据
        :param table_name:表名称
        :param data_dict:数据字典
        :return:无
        """
        # 生成,隔开的字符串
        columns = ','.join(data_dict.keys())
        # 生成%s占位符的字符串
        placeholders = ','.join(['%s'] * len(data_dict))
        # 暂时不考虑时间格式
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            self.cur.execute(sql, tuple(data_dict.values()))
            self.conn.commit()
        except Exception as e:
            log.error(f"插入数据错误: {e}")
            self.conn.rollback()
            log.error(f"{sql}未执行成功")
            raise

    def inserts(self, table_name: str, data_list: list) -> None:
        """
        批量插入数据
        :param table_name:表名称
        :param data_list:数据列表
        :return:无
        """
        pass

    def delete(self, table_name: str, condition: str) -> None:
        """
        删除数据
        :param table_name:表名称
        :param condition:删除条件
        :return:无
        """
        sql = f"DELETE FROM {table_name} WHERE {condition}"
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(f"删除数据错误: {e}")
            self.conn.rollback()

    def update(self, table_name: str, data_dict: dict, condition: str) -> None:
        """
        更新单行数据
        :param table_name:表名称
        :param data_dict:数据字典
        :param condition:更新条件
        :return:无
        """
        set_clause = ', '.join([f"{key} = %s" for key in data_dict.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        try:
            self.cur.execute(sql, tuple(data_dict.values()))
            self.conn.commit()
        except Exception as e:
            log.error(f"更新数据错误: {e}")
            self.conn.rollback()

    def select(self, table_name: str, field_list: list[str], condition: str) -> list:
        """
        查询数据，指定了字段
        :param table_name: 表格名称
        :param field_list: 需要的字段，列表格式
        :param condition: 条件
        :return: 查询结果列表
        """
        # fields = '(' + ','.join(field_list) + ')'
        fields = ','.join(field_list)
        if condition == 'TRUE':
            sql = f"SELECT {fields} FROM {table_name}"
        else:
            sql = f"SELECT {fields} FROM {table_name} WHERE {condition}"
        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            log.error(f"查询语句错误: {e}")
            raise

    def select_star(self, table_name: str, condition: str) -> list:
        """
        查询所有数据
        :param table_name:表名称
        :param condition:查询条件
        :return:查询结果列表
        """
        if condition == 'TRUE':
            sql = f"SELECT * FROM {table_name}"
        else:
            sql = f"SELECT * FROM {table_name} WHERE {condition}"
        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            log.error(f"查询语句错误: {e}")
            raise

    def select_custom(self, sql: str) -> list:
        """
        执行自定义sql语句
        :param sql:sql语句
        :return:查询结果列表
        """
        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            log.error(f"查询语句错误: {e}")
            raise

    def upsert(self, table_name: str, data_dict: dict, key_columns: list[str]) -> None:
        """
        upsert单行数据，如果数据库中存在主键，则更新，否则插入
        :param table_name:表名称
        :param data_dict:数据字典
        :param key_columns:主键列
        :return:无
        """
        # 检查传入数据是否为空
        if not data_dict:
            return
        # 构建单条upsert语句
        columns = ','.join(data_dict.keys())
        placeholders = ','.join(['%s'] * len(data_dict))
        conflict_target = ','.join(key_columns)
        set_clause = ', '.join([f"{col}=EXCLUDED.{col}" for col in data_dict.keys()])
        upsert_template = (f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) "
                           f"ON CONFLICT ({conflict_target}) DO UPDATE SET {set_clause};")

        # 尝试执行单条upsert语句
        try:
            self.cur.execute(upsert_template, tuple(data_dict.values()))
            self.conn.commit()
            log.info(f"{table_name} upsert成功")
            return
        except Exception as e:
            log.error(f"{table_name} upsert失败: {e}")
            self.conn.rollback()
            raise

    def upserts(self, table_name: str, data_list: list[dict[str, any]], key_columns: list[str]) -> None:
        """
        批量upsert数据，如果数据库中存在主键，则更新，否则插入
        :param table_name:表名称
        :param data_list:数据列表
        :param key_columns:主键列
        :return:无
        """
        # 检查传入数据是否为空
        if not data_list:
            return
        # 构建UPSERT语句模板，都是拿第一行的数据作为模板
        placeholders = ','.join(['%s'] * len(data_list[0]))
        columns_str = ','.join(data_list[0].keys())
        conflict_target = ','.join(key_columns)
        set_clause = ', '.join([f"{col}=EXCLUDED.{col}" for col in data_list[0].keys()])
        upsert_template = (f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) "
                           f"ON CONFLICT ({conflict_target}) DO UPDATE SET {set_clause};")
        # 尝试执行语句
        try:
            batch_count = 0
            for row in data_list:
                self.cur.execute(upsert_template, tuple(row.values()))
                batch_count += 1
                # 达到500条时提交
                if batch_count >= 500:
                    self.conn.commit()
                    batch_count = 0
            # 处理剩余次数不足的数据
            if batch_count > 0:
                self.conn.commit()
            # print("batch_count", batch_count)
            log.info(f"UPSERT {table_name} 执行成功，执行{len(data_list)}条语句")
            return
        except Exception as e:
            log.error(f"UPSERT {table_name} 执行失败: {e}")
            self.conn.rollback()
            raise

    def upserts_dif_len_dict(self, table_name: str, data_list: list[dict[str, any]], key_columns: list[str]) -> None:
        """
        批量upsert数据，如果数据库中存在主键，则更新，否则插入
        :param table_name:表名称
        :param data_list:数据列表
        :param key_columns:主键列
        :return:无
        """
        # 检查传入数据是否为空
        if not data_list:
            return
        # 开始循环
        batch_count = 0
        for row in data_list:
            if all(column in row.keys() for column in key_columns):
                # 构建sql语句
                placeholders = ','.join(['%s'] * len(row))
                columns_str = ','.join(row.keys())
                conflict_target = ','.join(key_columns)
                set_clause = ', '.join([f"{col}=EXCLUDED.{col}" for col in row.keys()])
                upsert_template = (f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) '
                                   f'ON CONFLICT ({conflict_target}) DO UPDATE SET {set_clause};')
                # 开始写数据
                try:
                    self.cur.execute(upsert_template, tuple(row.values()))
                    batch_count += 1
                    # 达到500条时提交
                    if batch_count >= 500:
                        self.conn.commit()
                        batch_count = 0
                except Exception as e:
                    log.error(f"UPSERT {table_name} 执行失败: {e}")
                    self.conn.rollback()
                    raise
            else:
                log.error(f"{row} 缺失关键字段:{key_columns}")
                raise ValueError(f"{row} 缺失关键字段:{key_columns}")
        # 处理剩余次数不足的数据
        if batch_count > 0:
            self.conn.commit()

    def close(self) -> None:
        """
        关闭连接
        :return:无
        """
        self.cur.close()
        self.pool.putconn(self.conn)
