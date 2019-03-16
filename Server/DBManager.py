# coding=utf-8
import pymysql
import Player
import json

INVALID_CHAR = [';', ',', '\\', '/' ,'(', ')', '[', ']', '{', '}', '%', '@', '*', '!', '\'']

class DbManager:
    # 构造函数
    def __init__(self):
        self.mysql = None

    # 连接mysql数据库
    def connect(self, ip, user, pw, db, port):
        try:
            self.mysql = pymysql.connect(ip, user, pw, db, port)
            print("[数据库] connect successfully!")
            # self.init_database()  # 第一次运行，未建表时运行！！
            return True
        except pymysql.Error as ex:
            print("[数据库] connect fail: " + str(ex))
            return False

    # 初始化数据库
    def init_database(self):
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = self.mysql.cursor()

        # 使用 execute() 方法执行 SQL，如果表存在则删除
        cursor.execute("DROP TABLE IF EXISTS ACCOUNT")

        # 使用预处理语句创建表
        sql = """CREATE TABLE ACCOUNT (
                 ID  CHAR(20) NOT NULL PRIMARY KEY,
                 PASSWORD  CHAR(20) NOT NULL)"""

        cursor.execute(sql)

        # 使用 execute() 方法执行 SQL，如果表存在则删除
        cursor.execute("DROP TABLE IF EXISTS PLAYER")

        # 使用预处理语句创建表
        sql = """CREATE TABLE PLAYER (
                 ID  CHAR(20) NOT NULL PRIMARY KEY,
                 DATA  TEXT NOT NULL)"""

        cursor.execute(sql)

    # 判定安全字符串，防止SQL注入
    def is_safe_string(self, string):
        for c in INVALID_CHAR:
            if c in string:
                return False
        return True

    # 是否存在该用户
    def is_account_exist(self, player_id):
        if not self.is_safe_string(player_id):
            return True

        # sql语句
        sql = "SELECT * FROM ACCOUNT WHERE ID = '%s'" % player_id

        # 使用cursor()方法获取操作游标
        cursor = self.mysql.cursor()

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            return len(results) > 0
        except pymysql.Error as ex:
            print("[数据库] IsSafeString err, " + str(ex))
            return True

    # 注册
    def register(self, player_id, pw):
        # 防止SQL注入
        if not self.is_safe_string(player_id):
            print("[数据库] Register fail, id not safe!")
            return False
        if not self.is_safe_string(pw):
            print("[数据库] Register fail, pw not safe!")
            return False

        # 是否有重复账号
        if self.is_account_exist(player_id):
            print("[数据库] Register fail, id exist!")
            return False

        # sql语句
        sql = "INSERT INTO ACCOUNT(ID, PASSWORD) VALUES('%s', '%s')" % (player_id, pw)

        # 使用cursor()方法获取操作游标
        cursor = self.mysql.cursor()

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            self.mysql.commit()
            return True
        except pymysql.Error as ex:
            print("[数据库] Register fail: " + str(ex))
            # 发生错误时回滚
            self.mysql.rollback()
            return False

    # 创建角色
    def create_player(self, player_id):
        # 防止SQL注入
        if not self.is_safe_string(player_id):
            print("[数据库] Create player fail, id not safe!")
            return False

        # 序列化
        player_data = Player.PlayerData()
        data = player_data.to_json()

        # 写入数据库
        sql = "INSERT INTO PLAYER(ID, DATA) VALUES('%s', '%s')" % (player_id, data)

        # 使用cursor()方法获取操作游标
        cursor = self.mysql.cursor()

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            self.mysql.commit()
            return True
        except pymysql.Error as ex:
            print("[数据库] Create player fail: " + str(ex))
            # 发生错误时回滚
            self.mysql.rollback()
            return False

    # 检测用户名和密码
    def check_password(self, player_id, pw):
        # 防止SQL注入
        if not self.is_safe_string(player_id):
            print("[数据库] CheckPassword fail, id not safe!")
            return False
        if not self.is_safe_string(pw):
            print("[数据库] CheckPassword fail, pw not safe!")
            return False

        # sql语句
        sql = "SELECT * FROM ACCOUNT WHERE ID = '%s' AND PASSWORD = '%s'" % (player_id, pw)

        # 使用cursor()方法获取操作游标
        cursor = self.mysql.cursor()

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            return len(results) > 0
        except pymysql.Error as ex:
            print("[数据库] Check password err, " + str(ex))
            return True

    # 获取玩家数据
    def get_player_data(self, player_id):
        # 防止SQL注入
        if not self.is_safe_string(player_id):
            print("[数据库] Get player data fail, id not safe!")
            return None

        # sql语句
        sql = "SELECT DATA FROM PLAYER WHERE ID = '%s'" % player_id

        # 使用cursor()方法获取操作游标
        cursor = self.mysql.cursor()

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()

            if len(results) == 1:
                player_data = Player.PlayerData()
                player_data = player_data.to_player_data(results[0][0])
                return player_data
            else:
                return None
        except pymysql.Error as ex:
            print("[数据库] Get PlayerData err, " + str(ex))
            return None

    # 保存角色（更新玩家数据）
    def update_player_data(self, player_id, player_data):
        # 防止SQL注入
        if not self.is_safe_string(player_id):
            print("[数据库] Update player data fail, id not safe!")
            return False

        data = player_data.to_json()

        # sql语句
        sql = "UPDATE PLAYER SET DATA = '%s' WHERE ID = '%s'" % (data, player_id)

        # 使用cursor()方法获取操作游标
        cursor = self.mysql.cursor()

        # 更新
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 提交到数据库执行
            self.mysql.commit()
            return True
        except pymysql.Error as ex:
            print("[数据库] Update PlayerData err, " + str(ex))
            self.mysql.rollback()
            return False





