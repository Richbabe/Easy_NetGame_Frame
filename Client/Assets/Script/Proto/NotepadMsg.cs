//获取记事本内容
public class MsgGetText : MsgBase
{
    public MsgGetText() { protoName = "MsgGetText"; }
    //服务端回
    public string text = "";
}

//保存记事本内容
public class MsgSaveText : MsgBase
{
    public MsgSaveText() { protoName = "MsgSaveText"; }
    //客户端发
    public string text = "";
    //服务端回（0-成功 1-文字太长）
    public int result = 0;
}
