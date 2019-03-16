# coding=utf-8

DEFAULT_SIZE = 1024


class ByteArray:
    # 构造函数
    def __init__(self, *args):
        if len(args) == 0:
            self.byte = bytearray(DEFAULT_SIZE)
            self.capacity = DEFAULT_SIZE
            self.initSize = DEFAULT_SIZE
            self.readIdx = 0
            self.writeIdx = 0
        elif isinstance(args[0], int):
            self.byte = bytearray(args[0])
            self.capacity = args[0]
            self.initSize = args[0]
            self.readIdx = 0
            self.writeIdx = 0
        elif isinstance(args[0], bytearray):
            self.byte = args[0]
            self.capacity = len(args[0])
            self.initSize = len(args[0])
            self.readIdx = 0
            self.writeIdx = len(args[0])

    # 获取信息流长度
    def length(self):
        return self.writeIdx - self.readIdx

    # 获取可用容量
    def remain(self):
        return self.capacity - self.writeIdx

    # 重设尺寸
    def resize(self, size):
        if size < self.length() or size < self.initSize:
            return

        n = 1
        while n < size:
            n *= 2

        self.capacity = n
        new_bytes = bytearray(self.capacity)
        new_bytes[0:self.length()] = self.byte[self.readIdx:self.writeIdx]
        self.byte = new_bytes
        self.readIdx = 0
        self.writeIdx = self.length()

    # 检查并移动数据
    def check_move(self):
        if self.length() < 8:
            self.move_bytes()

    # 移动数据，将已读数据清掉
    def move_bytes(self):
        if self.length() > 0:
            self.byte[0:self.length()] = self.byte[self.readIdx:self.writeIdx]

        self.writeIdx = self.length()
        self.readIdx = 0

    # 写入数据
    def write(self, byte, offset, count):
        # 判断缓冲区容量是否够大
        if self.remain() < count:
            self.resize(self.length() + count)

        self.byte[self.writeIdx:self.writeIdx + count] = byte[offset:offset + count]
        self.writeIdx += count
        return count

    # 读取数据
    def read(self, byte, offset, count):
        count = min(count, self.length())  # 规定最多只能读取length个字节

        byte[offset:offset + count] = self.byte[0:count]

        self.readIdx += count
        self.check_move()

        return count

    # 读取Int16
    def read_int_16(self):
        if self.length() < 2:
            return

        # print(self.byte[self.readIdx],self.byte[self.readIdx + 1])
        ret = self.byte[self.readIdx + 1] << 8 | self.byte[self.readIdx]
        self.readIdx += 2

        self.check_move()
        return ret

    # 打印缓冲区（调试用）
    def to_string(self):
        return self.byte[self.readIdx:self.writeIdx]

    # 打印调试信息（调试用）
    def debug(self):
        return "readIdx({0}) writeIdx({1}) bytes({2})".format(self.readIdx, self.writeIdx, self.byte)

'''
# 测试
# [1 创建]
buff = ByteArray(8)
print("[1 debug] -> {0}".format(buff.debug()))
print("[1 string] -> {0}".format(buff.to_string()))

# [2 write]
wb = bytearray([1, 2, 3, 4, 5])
buff.write(wb, 0, 5)
print("[2 debug] -> {0}".format(buff.debug()))
print("[2 string] -> {0}".format(buff.to_string()))

# [3 read]
rb = bytearray(4)
buff.read(rb, 0, 2)
print("[3 debug] -> {0}".format(buff.debug()))
print("[3 string] -> {0}".format(buff.to_string()))
print("[3 rb ] -> {0}".format(rb))

# [4 write, resize]
wb = bytearray([6,7,8,7,1,2])
buff.write(wb, 0, 6)
print("[4 debug] -> {0}".format(buff.debug()))
print("[4 string] -> {0}".format(buff.to_string()))

s = "Test"
a = bytearray(s.encode())
print(a.decode())


s = "80Test0000"
t = ByteArray()
a = bytearray(s.encode())
t.byte = a
t.readIdx = 0
t.writeIdx = 8
print(t.read_int_16())
print(t.length())
'''




