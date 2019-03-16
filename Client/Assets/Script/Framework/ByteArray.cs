using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class ByteArray{
    // 默认缓冲区大小
    const int DEFAULT_SIZE = 1024;

    // 初始大小
    int initSize = 0;
    
    // 缓冲区
    public byte[] bytes;

    // 读写位置
    public int readIdx = 0;
    public int writeIdx = 0;

    // 容量
    private int capacity = 0;

    // 剩余空间
    public int remain { get { return capacity - writeIdx; } }

    // 数据长度
    public int length { get { return writeIdx - readIdx; } }

    // 构造函数
    public ByteArray(int size = DEFAULT_SIZE)
    {
        bytes = new byte[size];
        capacity = size;
        initSize = size;
        readIdx = 0;
        writeIdx = 0;
    }

    // 构造函数
    public ByteArray(byte[] defaultBytes)
    {
        bytes = defaultBytes;
        capacity = defaultBytes.Length;
        initSize = defaultBytes.Length;
        readIdx = 0;
        writeIdx = defaultBytes.Length;
    }

    // 重设尺寸
    public void Resize(int size)
    {
        if (size < length || size < initSize)
            return;

        int n = 1;
        while (n < size)
            n *= 2;

        capacity = n;
        byte[] newBytes = new byte[capacity];
        Array.Copy(bytes, readIdx, newBytes, 0, length);
        bytes = newBytes;
        readIdx = 0;
        writeIdx = length; 
    }

    // 检查并移动数据
    public void CheckAndMoveBytes()
    {
        if(length < 8)
        {
            MoveBytes();
        }
    }

    // 移动数据, 将已读的数据清掉
    public void MoveBytes()
    {
        if(length > 0)
        {
            Array.Copy(bytes, readIdx, bytes, 0, length);
        }
        writeIdx = length;
        readIdx = 0;
    }

    // 写入数据
    public int Write(byte[] bs, int offset, int count)
    {
        // 判断缓冲区容量是否够大
        if(remain < count)
        {
            Resize(length + count);
        }

        Array.Copy(bs, offset, bytes, writeIdx, count);
        writeIdx += count;
        return count;
    }

    // 读取数据
    public int Read(byte[] bs,int offset, int count)
    {
        count = Math.Min(count, length);  // 限定最多只能读取length个字节
        Array.Copy(bytes, 0, bs, offset, count);
        readIdx += count;
        // 将已读取的字节从缓冲区中抹去
        CheckAndMoveBytes();
        return count;
    }

    // 读取Int16
    public Int16 ReadInt16()
    {
        if(length < 2)
        {
            return 0;
        }
        // Int16 ret = (Int16)((bytes[1] << 8) | bytes[0]);  // 按照小端方式读
        Int16 ret = BitConverter.ToInt16(bytes, readIdx);
        readIdx += 2;
        // 将已读取的字节从缓冲区中抹去
        CheckAndMoveBytes();
        return ret;
    }

    // 读取Int32
    public Int32 ReadInt32()
    {
        if (length < 4)
        {
            return 0;
        }
        /*
        Int32 ret = (Int32)((bytes[3] << 24) |
                            (bytes[2] << 16) |
                            (bytes[1] << 8)  |
                            bytes[0]);  // 按照小端方式读
        */
        Int32 ret = BitConverter.ToInt32(bytes, readIdx);
        readIdx += 4;
        // 将已读取的字节从缓冲区中抹去
        CheckAndMoveBytes();
        return ret;
    }

    // 打印缓冲区（调试用）
    public override string ToString()
    {
        return BitConverter.ToString(bytes, readIdx, length);
    }

    // 打印调试信息（调试用）
    public string Debug()
    {
        return string.Format("readIdx({0}) writeIdx({1}) bytes({2})", readIdx, writeIdx, BitConverter.ToString(bytes, 0, capacity));
    }

}
