import os
import sys
from buildhat import Motor
import time
import termios
import tty
import sys

def check_permissions():
    """检查串口权限"""
    # 检查串口权限
    if not os.access('/dev/ttyAMA0', os.R_OK | os.W_OK):
        print("错误：没有串口访问权限")
        print("请运行以下命令添加权限：")
        print("sudo usermod -a -G dialout $USER")
        print("然后注销并重新登录使权限生效")
        sys.exit(1)

def get_key():
    """读取按键"""
    try:
        # 保存终端设置
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # 设置终端为原始模式
            tty.setraw(sys.stdin.fileno())
            # 读取一个字符
            ch = sys.stdin.read(1)
            return ch
        finally:
            # 恢复终端设置
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    except:
        return None

# 初始化电机
motor_left_front = Motor('A')  # 左轮电机
motor_right_front = Motor('B')  # 右轮电机
motor_left_back = Motor('C')  # 左轮电机
motor_right_back = Motor('D')  # 右轮电机


# 设置默认速度
DEFAULT_SPEED = 50  # 默认速度10%
TURN_SPEED = 50    # 转弯时的速度

def stop_motors():
    """停止所有电机"""
    motor_left_front.stop()
    motor_right_front.stop()
    motor_left_back.stop()
    motor_right_back.stop()

def move_forward():
    """向前移动"""
    motor_left_front.start(-DEFAULT_SPEED)  # 左轮逆时针
    motor_right_front.start(DEFAULT_SPEED)  # 右轮顺时针
    motor_left_back.start(-DEFAULT_SPEED)  # 左轮逆时针
    motor_right_back.start(DEFAULT_SPEED)  # 右轮顺时针

def move_backward():
    """向后移动"""
    motor_left_front.start(DEFAULT_SPEED)   # 左轮顺时针
    motor_right_front.start(-DEFAULT_SPEED) # 右轮逆时针
    motor_left_back.start(DEFAULT_SPEED)   # 左轮顺时针
    motor_right_back.start(-DEFAULT_SPEED) # 右轮逆时针

def go_left():
    """左平移"""
    motor_left_front.start(TURN_SPEED)     # 左轮顺时针
    motor_right_front.start(TURN_SPEED)    # 右轮顺时针
    motor_left_back.start(-TURN_SPEED)     # 左轮顺时针
    motor_right_back.start(-TURN_SPEED)    # 右轮顺时针

def go_right():
    """右平移"""
    motor_left_front.start(-TURN_SPEED)    # 左轮逆时针
    motor_right_front.start(-TURN_SPEED)   # 右轮逆时针
    motor_left_back.start(TURN_SPEED)     # 左轮顺时针
    motor_right_back.start(TURN_SPEED)    # 右轮顺时针

def turn_left():
    """左转"""
    motor_left_front.start(TURN_SPEED)     # 左轮顺时针
    motor_right_front.start(TURN_SPEED)   # 右轮逆时针
    motor_left_back.start(TURN_SPEED)      # 左轮顺时针
    motor_right_back.start(TURN_SPEED)    # 右轮逆时针

def turn_right():
    """右转"""
    motor_left_front.start(-TURN_SPEED)    # 左轮逆时针
    motor_right_front.start(-TURN_SPEED)   # 右轮顺时针
    motor_left_back.start(-TURN_SPEED)     # 左轮逆时针
    motor_right_back.start(-TURN_SPEED)    # 右轮顺时针
    

print("小车控制程序已启动！")
print("使用以下按键控制小车：")
print("按住 w : 向前")
print("按住 s : 向后")
print("按住 a : 左平移")
print("按住 d : 右平移")
print("按住 q : 左转")
print("按住 e : 右转")
print("p : 退出程序")
print("松开按键后小车会自动停止")

try:
    while True:
        current_time = time.time()
        
        key = get_key()
        
        if key == 'w':
            move_forward()
        elif key == 's':
            move_backward()
        elif key == 'a':
            go_left()
        elif key == 'd':
            go_right()
        elif key == 'p':
            print("程序已退出！")
            stop_motors()
            break
        elif key == 'q':
            turn_left()
        elif key == 'e':
            turn_right()
        else:
            stop_motors()

        next_time = time.time()
        if next_time - current_time < 0.1:
            time.sleep(0.1 - (next_time - current_time))
            continue
            
except KeyboardInterrupt:
    print("程序已被用户中断！")
    stop_motors()
finally:
    stop_motors() 