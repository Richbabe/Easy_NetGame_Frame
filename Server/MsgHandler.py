# coding=utf-8
import MsgBase
import BattleMsg
import SysMsg
import Player

"""
逻辑消息处理模块
声明逻辑消息处理函数
"""
def MsgMove(managers, c, msg_base):
    net_manager = managers["net_manager"]
    print(msg_base.content["x"])
    msg_base.content["x"] += 1
    net_manager.send(c, msg_base)


"""
系统消息处理模块
声明系统消息处理函数
"""
def MsgRegister(managers, c, msg_base):
    db_manager = managers["db_manager"]
    net_manager = managers["net_manager"]
    # 注册
    if db_manager.register(msg_base.content["id"], msg_base.content["pw"]):
        db_manager.create_player(msg_base.content["id"])
        msg_base.content["result"] = 0
    else:
        msg_base.content["result"] = 1
    net_manager.send(c, msg_base)

def MsgLogin(managers, c, msg_base):
    db_manager = managers["db_manager"]
    net_manager = managers["net_manager"]
    player_manager = managers["player_manager"]
    # 密码校验
    if not db_manager.check_password(msg_base.content["id"],msg_base.content["pw"]):
        msg_base.content["result"] = 1
        net_manager.send(c, msg_base)
        return

    # 不允许再次登陆
    if c.player is not None:
        msg_base.content["result"] = 1
        net_manager.send(c, msg_base)
        return

    # 如果已经登陆，踢下线
    if player_manager.is_online(msg_base.content["id"]):
        # print(msg_base.content["id"])
        # 发送踢下线协议
        other = player_manager.get_player(msg_base.content["id"])
        msgKick = SysMsg.MsgKick()
        msgKick.content["reason"] = 0

        net_manager.send(other.state, msgKick)

        # 断开连接
        net_manager.close(other.state.client_socket)

    # 获取玩家数据
    player_data = db_manager.get_player_data(msg_base.content["id"])
    if player_data is None:
        msg_base.content["result"] = 1
        net_manager.send(c, msg_base)
        return

    # 构建Player
    player = Player.Player(c)
    player.id = msg_base.content["id"]
    player.data = player_data
    player_manager.add_player(msg_base.content["id"], player)
    c.player = player

    # 返回协议
    msg_base.content["result"] = 0
    net_manager.send(player.state, msg_base)

def MsgGetText(managers, c, msg_base):
    net_manager = managers["net_manager"]
    player = c.player
    if player is None:
        return
    # 获取text
    msg_base.content["text"] = player.data.text
    net_manager.send(player.state, msg_base)

def MsgSaveText(managers, c, msg_base):
    net_manager = managers["net_manager"]
    player = c.player
    if player is None:
        return
    # 获取text
    player.data.text = msg_base.content["text"]
    net_manager.send(player.state, msg_base)

def MsgPing(managers, c, msg_base):
    net_manager = managers["net_manager"]
    print("MsgPing")
    c.last_ping_time = net_manager.get_time_stamp()
    msg_pong = SysMsg.MsgPong()
    net_manager.send(c, msg_pong)


"""
事件处理模块EventHandlerHandler
声明事件处理函数
"""
def disconnect(managers, cs):
    db_manager = managers["db_manager"]
    player_manager = managers["player_manager"]
    desc = cs.addr
    print("Close")
    # sendStr = "Leave|" + desc + ","
    # player下线
    if cs.player is not None:
        # 保存数据
        db_manager.update_player_data(cs.player.id, cs.player.data)
        # 移除
        player_manager.remove_player(cs.player.id)

#  Ping检查
def check_ping(managers, clients):
    net_manager = managers["net_manager"]
    time_now = net_manager.get_time_stamp()

    # 遍历，删除
    for cs in clients.values():
        if time_now - cs.last_ping_time > net_manager.ping_interval * 4:
            print("Ping Close : " + cs.addr)
            net_manager.close(cs.client_socket)
            return


def timer(managers, clients):
    check_ping(managers, clients)
