# coding=utf-8
import MsgBase

# 注册协议
class MsgRegister(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgRegister",
            # 客户端发
            "id": "",
            "pw": "",
            # 服务端回(0:成功，1：失败)
            "result": 0
        }

# 登陆协议
class MsgLogin(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgLogin",
            # 客户端发
            "id": "",
            "pw": "",
            # 服务端回(0:成功，1：失败)
            "result": 0
        }

# 踢下线协议（服务端推送）
class MsgKick(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgKick",
            # 服务端回原因(0:其他人登陆同一账号)
            "reason": 0
        }

# 获取记事本内容协议
class MsgGetText(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgGetText",
            # 服务端回
            "text": ""
        }

# 保存记事本内容协议
class MsgSaveText(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgSaveText",
            # 客户端发
            "text": "",
            # 服务端回(0:成功，1：太长)
            "result": 0
        }

# 心跳机制中的PING协议
class MsgPing(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgPing",
        }

# 心跳机制中的PONG协议
class MsgPong(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgPong",
        }