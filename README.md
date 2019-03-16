# Easy_NetGame_Frame
Client:Unity &amp; Server:Python3.6 + mysql

该框架为单进程单线程架构，使用Select多路复用处理网络连接，用MySQL数据库保存玩家数据，具有粘包半包、心跳机制、消息分发等处理。拥有用户注册登陆、客户端服务端通信、数据保存等功能。

在运行前，请自行修改Server文件夹下的NetManager.py第205行中的mysql用户名和密码，并自己先建立一个GAME数据库，在GAME数据库中建立ACCOUNT表和PLAYER表，表中元素请参考Server文件夹下的DBManager.py中的init_database函数。
