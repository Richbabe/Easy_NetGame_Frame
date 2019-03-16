# coding=utf-8
import MsgBase


class MsgMove(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgMove",
            "x": 0,
            "y": 0,
            "z": 0
        }


class MsgAttack(MsgBase.MessageBase):
    # 构造函数
    def __init__(self):
        self.content = {
            "protoName": "MsgAttack",
            "desc": "127.0.0.1:6543"
        }

'''
msgMove = MsgMove()
print(msgMove.encode(msgMove))

string = "{\"protoName\":\"MsgMove\",\"x\":100,\"y\":-20,\"z\":0}"
byte = bytearray(string.encode())
a = msgMove.decode("MsgMove", byte, 0, len(byte))
print(a.content)

a = msgMove.encode_name(msgMove)
print(a)

res = msgMove.decode_name(a, 0)
print(res)
'''
