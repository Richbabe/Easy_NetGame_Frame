using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System;
using System.Linq;

public class NetManager : MonoBehaviour {

    // 定义套接字
    static Socket socket;

    // 接收缓冲区
    static ByteArray readBuff;

    // 写入队列
    static Queue<ByteArray> writeQueue;

    // 消息列表
    static List<MsgBase> msgList = new List<MsgBase>();

    // 消息列表长度
    static int msgCount = 0;

    // 每一次Update处理的消息量
    readonly static int MAX_MESSAGE_FIRE = 10;

    // 是否正在连接
    static bool isConnecting = false;

    // 是否正在关闭
    static bool isClosing = false;

    // 是否启用心跳
    public static bool isUsePing = true;

    // 心跳间隔时间
    public static int pingInterval = 30;

    // 上一次发送Ping的时间
    static float lastPingTime = 0;

    // 上一次收到Pong的时间
    static float lastPongTime = 0;

    // 事件
    public enum NetEvent
    {
        ConnectSucc = 1,
        ConnectFail = 2,
        Close = 3,
    }

    // 事件委托类型
    public delegate void EventListener(String err);

    // 事件监听列表
    private static Dictionary<NetEvent, EventListener> eventListeners = new Dictionary<NetEvent, EventListener>();

    // 消息委托类型
    public delegate void MsgListener(MsgBase msgBase);

    // 消息监听列表
    private static Dictionary<string, MsgListener> msgListeners = new Dictionary<string, MsgListener>();

    // 添加事件监听
    public static void AddEventListener(NetEvent netEvent, EventListener listener)
    {
        // 添加事件
        if (eventListeners.ContainsKey(netEvent))
        {
            eventListeners[netEvent] += listener;
        }
        // 新增事件
        else
        {
            eventListeners[netEvent] = listener;
        }
    }

    // 删除事件监听
    public static void RemoveEventListener(NetEvent netEvent, EventListener listener)
    {
        if (eventListeners.ContainsKey(netEvent))
        {
            eventListeners[netEvent] -= listener;
            // 如果当前事件无监听，删除该事件
            if(eventListeners[netEvent] == null)
            {
                eventListeners.Remove(netEvent);
            }
        }
    }

    // 添加消息监听
    public static void AddMsgListener(string msgName, MsgListener listener)
    {
        // 添加
        if (msgListeners.ContainsKey(msgName))
        {
            msgListeners[msgName] += listener;
        }
        // 新增
        else
        {
            msgListeners[msgName] = listener;
        }
    }

    // 删除消息监听
    public static void RemoveMsgListener(string msgName, MsgListener listener)
    {
        if (msgListeners.ContainsKey(msgName))
        {
            msgListeners[msgName] -= listener;
            // 删除
            if(msgListeners[msgName] == null)
            {
                msgListeners.Remove(msgName);
            }
        }
    }

    // 分发事件
    private static void FireEvent(NetEvent netEvent, string err)
    {
        if (eventListeners.ContainsKey(netEvent))
        {
            eventListeners[netEvent](err);
        }
    }

    // 分发消息
    private static void FireMsg(string msgName, MsgBase msgBase)
    {
        if (msgListeners.ContainsKey(msgName)){
            msgListeners[msgName](msgBase);
        }
    }

    // 连接
    public static void Connect(string ip, int port)
    {
        // 状态判断
        if(socket != null && socket.Connected)
        {
            Debug.Log("Connect fail, already connected!");
            return;
        }
        if (isConnecting)
        {
            Debug.Log("Connect fail, is connecting!");
            return;
        }

        // 初始化成员
        InitState();
        // 参数设置
        socket.NoDelay = true;  // 不使用Nagle算法，保证实时性
        // Connect
        isConnecting = true;
        socket.BeginConnect(ip, port, ConnectCallback, socket);
    }

    // Connect回调函数
    private static void ConnectCallback(IAsyncResult ar)
    {
        try
        {
            Socket socket = (Socket)ar.AsyncState;
            socket.EndConnect(ar);
            FireEvent(NetEvent.ConnectSucc, "");
            isConnecting = false;

            // 开始接收数据
            socket.BeginReceive(readBuff.bytes, readBuff.writeIdx, readBuff.remain, 0, ReceiveCallback, socket);
        }
        catch(SocketException ex)
        {
            FireEvent(NetEvent.ConnectFail, ex.ToString());
            isConnecting = false;
        }
    }

    // Receive回调函数
    public static void ReceiveCallback(IAsyncResult ar)
    {
        try
        {
            Socket socket = (Socket)ar.AsyncState;
            // 获取接收数据长度
            int count = socket.EndReceive(ar);

            // 如果收到FIN信号（count == 0），断开连接
            if(count == 0)
            {
                Close();
                return;
            }

            readBuff.writeIdx += count;

            // 处理二进制消息
            OnReceiveData();

            // 继续接收数据
            if(readBuff.remain < 8)
            {
                readBuff.MoveBytes();
                readBuff.Resize(readBuff.length * 2);
            }
            socket.BeginReceive(readBuff.bytes, readBuff.writeIdx, readBuff.remain, 0, ReceiveCallback, socket);
        }
        catch (SocketException ex){
            Debug.Log("Socket Receive fail " + ex.ToString());
        }
    }

    // 数据处理
    public static void OnReceiveData()
    {
        // 消息长度
        if(readBuff.length < 2)
        {
            return;
        }

        // 获取消息体长度
        int readIdx = readBuff.readIdx;
        byte[] bytes = readBuff.bytes;
        // Debug.Log(System.Text.Encoding.ASCII.GetString(bytes));
        Int16 bodyLength = (Int16)((bytes[readIdx + 1] << 8) | bytes[readIdx]);
        if (readBuff.length < bodyLength + 2)
        {
            return;
        }
        readBuff.readIdx += 2;

        // 解析协议名
        int nameCount = 0;
        string protoName = MsgBase.DecodeName(readBuff.bytes, readBuff.readIdx, out nameCount);
        if(protoName == "")
        {
            Debug.Log("OnReceiveData MsgBase.DecodeName fail!");
            return;
        }
        readBuff.readIdx += nameCount;

        // 解析协议体
        int bodyCount = bodyLength - nameCount;
        MsgBase msgBase = MsgBase.Decode(protoName, readBuff.bytes, readBuff.readIdx, bodyCount);
        readBuff.readIdx += bodyCount;

        // 将已读数据移除
        readBuff.CheckAndMoveBytes();

        // 将协议添加到消息队列
        lock (msgList)
        {
            msgList.Add(msgBase);
        }
        msgCount++;  // 避免操作msgList（不用msgList.Length()）,防止发生线程冲突

        // 继续读取消息
        if(readBuff.length > 2)
        {
            OnReceiveData();
        }
    }

    // 初始化状态
    private static void InitState()
    {
        // Socket
        socket = new Socket(AddressFamily.InterNetwork,
            SocketType.Stream, ProtocolType.Tcp);

        // 接收缓冲区
        readBuff = new ByteArray();

        // 写入队列
        writeQueue = new Queue<ByteArray>();

        // 消息列表
        msgList = new List<MsgBase>();

        // 消息列表长度
        msgCount = 0;

        // 是否正在连接
        isConnecting = false;

        // 是否正在关闭
        isClosing = false;

        // 上一次发送Ping的时间
        lastPingTime = Time.time;

        // 上一次收到Pong的时间
        lastPongTime = Time.time;

        // 监听PONG协议
        if (!msgListeners.ContainsKey("MsgPong"))
        {
            AddMsgListener("MsgPong", OnMsgPong);
        }
    }

    // 监听PONG协议
    private static void OnMsgPong(MsgBase msgBase)
    {
        lastPongTime = Time.time;
    }

    // 关闭连接
    public static void Close()
    {
        // 状态判断
        if (socket == null || !socket.Connected)
        {
            return;
        }
        if (isConnecting)
        {
            return;
        }

        // 还有数据在发送
        if(writeQueue.Count > 0)
        {
            isClosing = true;
        }
        // 没有数据在发送
        else
        {
            socket.Close();
            FireEvent(NetEvent.Close, "");
        }
    }

    // 发送数据
    public static void Send(MsgBase msg)
    {
        // 状态判断
        if(socket == null || !socket.Connected)
        {
            return;
        }
        if (isConnecting)
        {
            return;
        }
        if (isClosing)
        {
            return;
        }

        // 数据编码
        byte[] nameBytes = MsgBase.EncodeName(msg);  // 协议名长度+协议名
        byte[] bodyBytes = MsgBase.Encode(msg);      // 协议体
        int len = nameBytes.Length + bodyBytes.Length;  // 总长度
        byte[] sendBytes = new byte[2 + len];

        // 组装总长度
        sendBytes[0] = (byte)(len % 256);
        sendBytes[1] = (byte)(len / 256);
        // 组装协议名
        Array.Copy(nameBytes, 0, sendBytes, 2, nameBytes.Length);
        // 组装协议体
        Array.Copy(bodyBytes, 0, sendBytes, 2 + nameBytes.Length, bodyBytes.Length);

        // 写入队列
        ByteArray ba = new ByteArray(sendBytes);
        int count = 0;  // writeQueue的长度
        lock (writeQueue)
        {
            writeQueue.Enqueue(ba);
            count = writeQueue.Count;
        }

        // Send
        if(count == 1)
        {
            socket.BeginSend(sendBytes, 0, sendBytes.Length, 0, SendCallback, socket);
        }
    }

    // Send回调函数
    public static void SendCallback(IAsyncResult ar)
    {
        // 获取state、Endstate
        Socket socket = (Socket)ar.AsyncState;
        // 状态判断
        if(socket == null || !socket.Connected)
        {
            return;
        }
        // EndSend
        int count = socket.EndSend(ar);

        // 获取写入队列第一条数据
        ByteArray ba;
        lock (writeQueue)
        {
            ba = writeQueue.First();
        }

        // 如果当前消息完整发送
        ba.readIdx += count;
        if(ba.length == 0)
        {
            lock (writeQueue)
            {
                writeQueue.Dequeue();
                ba = writeQueue.First();
            }
        }

        // 继续发送(当前消息还有残留或者写入队列还有别的消息)
        if(ba != null)
        {
            socket.BeginSend(ba.bytes, ba.readIdx, ba.length, 0, SendCallback, socket);
        }
        // 正在关闭
        else if (isClosing)
        {
            socket.Close();
        }
    }

    // 更新消息
    public static void MsgUpdate()
    {
        // 初步判断，提升效率
        if(msgCount == 0)
        {
            return;
        }

        // 重复处理消息
        for(int i = 0;i < MAX_MESSAGE_FIRE; ++i)
        {
            // 获取第一条
            MsgBase msgBase = null;
            lock (msgList)
            {
                if(msgList.Count > 0)
                {
                    msgBase = msgList[0];
                    msgList.RemoveAt(0);
                    msgCount--;
                }
            }

            // 分发消息
            if(msgBase != null)
            {
                FireMsg(msgBase.protoName, msgBase);
            }
            // 没有消息了
            else
            {
                break;
            }
        }
    }

    // 发送PING协议
    private static void PingUpdate()
    {
        // 是否启用心跳机制
        if (!isUsePing)
        {
            return;
        }

        // 发送PING
        if(Time.time - lastPingTime > pingInterval)
        {
            MsgPing msgPing = new MsgPing();
            Send(msgPing);
            lastPingTime = Time.time;
        }

        // 检测PONG时间
        if(Time.time - lastPongTime > pingInterval * 4)
        {
            Close();
        }
    }

    // Use this for initialization
    void Start () {
		
	}
	
	// Update is called once per frame
	public static void Update () {
        MsgUpdate();
        PingUpdate();
    }
}
