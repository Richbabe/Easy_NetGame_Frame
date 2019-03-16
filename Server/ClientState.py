# coding=utf-8
import socket
import ByteArrayFile
import time
import Player

class ClientState:
    # 构造函数
    def __init__(self, client_socket, addr, t):
        self.client_socket = client_socket
        self.addr = addr
        self.read_buff = ByteArrayFile.ByteArray()
        self.player = None

        # 最后一次收到MsgPing协议的时间
        self.last_ping_time = t