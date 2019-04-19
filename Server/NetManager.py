# coding=utf-8
import socket
import select
import ClientState
import MsgBase
import MsgHandler
import time
import datetime
import DBManager
import Player

class NetManager:
    # 构造函数
    def __init__(self):
        # 监听socket
        self.listenfd = None
        # 客户端socket及状态信息
        self.clients = {}
        # select的检查列表
        self.check_read = []

        # ping间隔
        self.ping_interval = 30

    def start_loop(self, listenPort):
        listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 开启socket
        CONN_ADDR = ('127.0.0.1', listenPort)
        listenfd.bind(CONN_ADDR)  # 绑定IP和端口到套接字
        listenfd.listen(5)  # 监听，5表示客户端最大连接数

        print('[服务器]启动成功！')

        while True:
            # 填充check_list列表
            check_list = []
            check_list.append(listenfd)
            for s in self.clients.values():
                check_list.append(s.client_socket)

            # select
            r, w, e = select.select(check_list, [], [], 1000)

            # 检查可读对象
            for s in r:
                if s == listenfd:
                    self.read_listenfd(s)
                else:
                    self.read_clientfd(s)

            # 超时
            self.timer()

    # 读取Listenfd
    def read_listenfd(self, listenfd):
        try:
            cilentfd, addr = listenfd.accept()  # 被动接受TCP客户的连接，等待连接的到来，收不到时会报异常
            print('connect by ', addr)
            socketAddr = str(addr[0]) + ":" + str(addr[1])
            client_state = ClientState.ClientState(cilentfd, socketAddr, self.get_time_stamp())
            self.clients[cilentfd] = client_state
        except socket.error as ex:
            print("Accept fail: " + str(ex))

    # 读取Clientfd
    def read_clientfd(self, clientfd):
        state = self.clients[clientfd]
        read_buff = state.read_buff

        # 接收字节数
        count = 0

        # 缓冲区不够，清除，若依旧不够，只能返回
        # 缓冲区长度只有1024，单条协议超过缓冲区长度时会发生错误，根据需要调整长度
        if read_buff.remain() <= 0:
            self.on_receive_data(state)
            read_buff.move_bytes()
        if read_buff.remain() <= 0:
            print("Receive fail, maybe msg length > buff capacity!")
            self.close(clientfd)
            return

        try:
            data = bytearray(clientfd.recv(1024))  # 接收数据1024字节
            count = len(data)
            state.read_buff.byte[state.read_buff.writeIdx:state.read_buff.capacity] = data[0:state.read_buff.remain()]

        except socket.error as ex:
            print("Receive fail: " + str(ex))
            self.close(clientfd)
            return

        # 客户端关闭
        if count <= 0:
            print('Socket Close ' + state.addr)
            self.close(clientfd)
            return

        # 消息处理
        read_buff.writeIdx += count

        # 处理二进制消息
        self.on_receive_data(state)

        # 移动缓冲区
        read_buff.check_move()

    # 关闭连接
    def close(self, clientfd):
        state = self.clients[clientfd]
        MsgHandler.disconnect(managers, state)

        state.client_socket.close()
        del self.clients[clientfd]

    # 消息处理
    def on_receive_data(self, state):
        read_buff = state.read_buff

        # 消息长度
        if read_buff.length() <= 2:
            return

        body_length = read_buff.read_int_16()

        # 消息体
        if read_buff.length() < body_length:
            return

        # 解析协议名
        msg_base = MsgBase.MessageBase()
        res = msg_base.decode_name(read_buff.byte, read_buff.readIdx)
        proto_name = res[0]
        name_count = res[1]

        if proto_name == "":
            print("OnReceiveData MsgBase.DecodeName fail！")
            self.close(state.client_socket)

        read_buff.readIdx += name_count

        # 解析协议体
        body_count = body_length - name_count
        msg_base = msg_base.decode(proto_name, read_buff.byte, read_buff.readIdx, body_count)
        read_buff.readIdx += body_count
        read_buff.check_move()

        # 分发消息00
        funName = "MsgHandler." + proto_name
        eval(funName)(managers, state, msg_base)  # 调用对应的消息处理函数

        # 继续读取消息
        if read_buff.length() > 2:
            self.on_receive_data(state)

    # 发送
    def send(self, cs, msg):
        # 状态判断
        if cs is None:
            return

        # 数据编码
        msg_base = MsgBase.MessageBase()
        name_bytes = msg_base.encode_name(msg)
        body_bytes = msg_base.encode(msg)

        length = len(name_bytes) + len(body_bytes)

        send_bytes = bytearray(2 + length)

        # 组装2字节的长度信息(按小端方式存储，比如70表示0 * 256 + 7)
        length_bytes = bytearray([length % 256, length // 256])
        send_bytes[0:2] = length_bytes

        # 组装名字
        send_bytes[2:2 + len(name_bytes)] = name_bytes

        # 组装消息体
        send_bytes[2 + len(name_bytes):2 + len(name_bytes) + len(body_bytes)] = body_bytes

        # 发送消息
        try:
            cs.client_socket.send(send_bytes)
        except socket.error as ex:
            print("Send fail: " + str(ex))

    # 获取时间戳
    def get_time_stamp(self):
        return time.time()

    # 定时器
    def timer(self):
        MsgHandler.timer(managers, self.clients)


net_manager = NetManager()
db_manager = DBManager.DbManager()
player_manager = Player.PlayerManager()

managers = {"net_manager": net_manager, "db_manager": db_manager, "player_manager": player_manager}

def run_server():
    global db_manager
    if not db_manager.connect("localhost","root","123","game", 3306):
        return
    '''
    # 测试
    if db_manager.register('hpz', '123456'):
        print("注册成功")

    # 测试
    if db_manager.create_player('hpz'):
        print("创建成功")
    
    # 测试
    if db_manager.check_password('hpz', '123456'):
        print("校验成功")
    
    
    # 测试
    player_data = db_manager.get_player_data('hpz')
    player_data.coin = 256
    db_manager.update_player_data('hpz', player_data)
    '''


    net_manager.start_loop(8888)

if __name__ == '__main__':
    run_server()

