# coding=utf-8
import json

class MessageBase:
    # 构造函数
    def __init__(self):
        self.content = {"protoName": ""}

    # 编码（将协议转化为Json类型）
    def encode(self, msg_base):
        s = json.dumps(msg_base.content)
        return bytearray(s.encode())

    # 解码（将Json类型的协议转化为协议实例）
    def decode(self, proto_name, byte, offset, count):
        string = byte.decode()
        s = string[offset:offset + count]
        msg_base = MessageBase()
        msg_base.content = json.loads(s)
        return msg_base

    # 编码协议名(2字节长度+协议名字符串)
    def encode_name(self, msg_base):
        # 名字bytes和长度
        name_bytes = msg_base.content["protoName"]
        name_bytes = bytearray(name_bytes.encode())
        length = len(name_bytes)

        # 申请bytes数组
        byte = bytearray(2 + length)

        # 组装2字节的长度信息(按小端方式存储，比如70表示0 * 256 + 7)
        name_length = bytearray([length % 256, length // 256])
        byte[0:2] = name_length

        # 组装协议名
        byte[2:2 + length] = name_bytes[0:length]

        return byte

    # 解码协议名，返回[name,count]
    def decode_name(self, byte, offset):
        count = 0

        # 必须大于2字节
        if offset + 2 > len(byte):
            return ["", count]

        # 读取长度
        length = int(byte[offset + 1]) << 8 | int(byte[offset])

        # 长度必须足够
        if offset + 2 + length > len(byte):
            return ["", count]

        # 解析
        count = 2 + length  # 返回协议名总长度（2字节长度+协议名长度）
        string = byte.decode()
        name = string[offset + 2:offset + 2 + length]
        return [name, count]




