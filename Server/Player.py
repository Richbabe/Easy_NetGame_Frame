# coding=utf-8
import json

class PlayerData:
    # 构造函数
    def __init__(self):
        self.coin = 0  # 金币
        self.text = "new text"  # 记事本

    # 将PlayerData转成Json规范函数
    def obj_2_json(self):
        return {
            "coin": self.coin,
            "text": self.text
        }

    # 将PlayerData转成Json字符串
    def to_json(self):
        return json.dumps(self.obj_2_json())

    # 将Json字符串转换成PlayerData
    def to_player_data(self, string):
        d = json.loads(string)
        player_data = PlayerData()
        player_data.coin = d["coin"]
        player_data.text = d["text"]
        return player_data

class Player:
    # 构造函数
    def __init__(self, state):
        self.id = ""  # id
        self.state = state
        # 临时数据
        self.x = 0
        self.y = 0
        self.z = 0
        # 数据库数据
        self.data = PlayerData()

class PlayerManager:
    # 构造函数
    def __init__(self):
        self.players = {}  # 玩家列表

    # 玩家是否在线
    def is_online(self, player_id):
        return self.players.__contains__(player_id)

    # 获取玩家
    def get_player(self, player_id):
        if self.players.__contains__(player_id):
            return self.players[player_id]
        return None

    # 添加玩家
    def add_player(self, player_id, player):
        self.players[player_id] = player

    # 删除玩家
    def remove_player(self, player_id):
        if self.players.__contains__(player_id):
            del self.players[player_id]


