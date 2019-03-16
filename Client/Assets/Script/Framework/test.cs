using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;

public class test : MonoBehaviour {
    public InputField idInput;
    public InputField pwInput;
    public InputField textInput;


	// Use this for initialization
	void Start () {
        NetManager.AddEventListener(NetManager.NetEvent.ConnectSucc, OnConnectSucc);
        NetManager.AddEventListener(NetManager.NetEvent.ConnectFail, OnConnectFail);
        NetManager.AddEventListener(NetManager.NetEvent.Close, OnConnectClose);

        NetManager.AddMsgListener("MsgMove", OnMsgMove);

        NetManager.AddMsgListener("MsgRegister", OnMsgRegister);
        
        NetManager.AddMsgListener("MsgLogin", OnMsgLogin);
        NetManager.AddMsgListener("MsgKick", OnMsgKick);
        NetManager.AddMsgListener("MsgGetText", OnMsgGetText);
        NetManager.AddMsgListener("MsgSaveText", OnMsgSaveText);
    }
	
	// Update is called once per frame
	void Update () {
        NetManager.Update();
	}

    // 玩家点击连接按钮
    public void OnConnectClick()
    {
        NetManager.Connect("127.0.0.1", 8888);
    }

    // 玩家点击断开按钮
    public void OnCloseClick()
    {
        NetManager.Close();
    }

    // 玩家点击移动按钮
    public void OnMoveClick()
    {
        MsgMove msg = new MsgMove();
        msg.x = 120;
        msg.y = 123;
        msg.z = -6;
        NetManager.Send(msg);
    }

    // 连接成功回调
    void OnConnectSucc(string err)
    {
        Debug.Log("OnConnectSucc");
    }

    // 连接失败回调
    void OnConnectFail(string err)
    {
        Debug.Log("OnConnectFail" + err);
    }

    // 连接关闭回调
    void OnConnectClose(string err)
    {
        Debug.Log("OnConnectClose");
    }

    // 收到MsgMove协议
    public void OnMsgMove(MsgBase msgBase)
    {
        MsgMove msg = (MsgMove)msgBase;
        // 消息处理
        Debug.Log("OnMsgMove msg.x = " + msg.x);
        Debug.Log("OnMsgMove msg.y = " + msg.y);
        Debug.Log("OnMsgMove msg.z = " + msg.z);
    }

    // 玩家点击注册按钮
    public void OnRegisterClick()
    {
        MsgRegister msg = new MsgRegister();
        msg.id = idInput.text;
        msg.pw = pwInput.text;
        if (msg.id != "" && msg.pw != "")
        {
            NetManager.Send(msg);
        }
        else
        {
            Debug.Log("id or pw can't be empty string");
        }
    }

    // 收到注册协议
    void OnMsgRegister(MsgBase msgBase)
    {
        MsgRegister msg = (MsgRegister)msgBase;
        if(msg.result == 0)
        {
            Debug.Log("注册成功");
        }
        else
        {
            Debug.Log("注册失败");
        }
    }

    // 玩家点击登陆按钮
    public void OnLoginClick()
    {
        MsgLogin msg = new MsgLogin();
        msg.id = idInput.text;
        msg.pw = pwInput.text;
        if(msg.id != "" && msg.pw != "")
        {
            NetManager.Send(msg);
        }
        else
        {
            Debug.Log("id or pw can't be empty string");
        }
    }

    // 收到登陆协议
    void OnMsgLogin(MsgBase msgBase)
    {
        MsgLogin msg = (MsgLogin)msgBase;
        if(msg.result == 0)
        {
            Debug.Log("登陆成功");
            // 请求记事本文本
            MsgGetText msgGetText = new MsgGetText();
            NetManager.Send(msgGetText);
        }
        else
        {
            Debug.Log("登陆失败");
        }
    }

    // 被踢下线
    void OnMsgKick(MsgBase msgBase)
    {
        Debug.Log("被踢下线");
    }

    // 收到记事本文本协议
    void OnMsgGetText(MsgBase msgBase)
    {
        MsgGetText msg = (MsgGetText)msgBase;
        textInput.text = msg.text;  // 更新文本
    }

    // 玩家点击保存按钮
    public void OnSaveClick()
    {
        MsgSaveText msg = new MsgSaveText();
        msg.text = textInput.text;
        NetManager.Send(msg);
    }

    // 收到保存协议
    void OnMsgSaveText(MsgBase msgBase)
    {
        MsgSaveText msg = (MsgSaveText)msgBase;
        if(msg.result == 0)
        {
            Debug.Log("保存成功");
        }
        else
        {
            Debug.Log("保存失败");
        }
    }
}


