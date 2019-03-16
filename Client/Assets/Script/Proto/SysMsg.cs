// 心跳机制中的PING协议
public class MsgPing : MsgBase
{
    public MsgPing() { protoName = "MsgPing"; }
}

// 心跳机制中的PONG协议
public class MsgPong : MsgBase
{
    public MsgPong() { protoName = "MsgPong"; }
}
