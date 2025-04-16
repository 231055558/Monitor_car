

---

### **Python 控制代码全集**

#### **一、基础控制函数**
```python
from buildhat import Motor
import time

# 初始化电机（假设电机接在Port A）
wheel = Motor('A')

# 基础运动控制 --------------------------------------------------
def move_forward(speed=50, duration=None):
    """正转控制"""
    wheel.start(speed)
    if duration:  # 持续运行指定时间
        time.sleep(duration)
        wheel.stop()

def move_backward(speed=50, duration=None):
    """反转控制"""
    wheel.start(-speed)
    if duration:
        time.sleep(duration)
        wheel.stop()

def precise_control(degrees, speed=30):
    """精确位置控制（适用于主动电机）"""
    wheel.run_for_degrees(degrees, speed)

def emergency_stop():
    """紧急停止"""
    wheel.stop()
```

#### **二、实时数据读取**
```python
# 数据监控函数 --------------------------------------------------
def read_realtime_data(interval=0.5):
    """持续读取运动参数"""
    try:
        while True:
            print(f"速度: {wheel.get_speed()} deg/s | "
                  f"相对位置: {wheel.get_position()}° | "
                  f"绝对位置: {wheel.get_aposition()}°")
            time.sleep(interval)
    except KeyboardInterrupt:
        wheel.stop()

# 单次数据抓取
current_speed = wheel.get_speed()  # 当前转速（度/秒）
relative_pos = wheel.get_position()  # 相对于启动点的位置
absolute_pos = wheel.get_aposition()  # 累计绝对位置（带溢出处理）
```

#### **三、闭环控制示例**
```python
# PID位置控制（简化版）------------------------------------------
def pid_position_control(target_deg, Kp=0.8, max_speed=50):
    current_pos = wheel.get_aposition()
    while abs(current_pos - target_deg) > 2:  # 2度容差
        error = target_deg - current_pos
        speed = min(max(int(Kp * error), -max_speed), max_speed)
        wheel.start(speed)
        current_pos = wheel.get_aposition()
        time.sleep(0.1)
    wheel.stop()

# 调用示例：转动到180度位置
pid_position_control(180)
```

#### **四、完整测试流程**
```python
if __name__ == "__main__":
    # 基础测试
    move_forward(speed=30, duration=3)  # 正转3秒
    move_backward(speed=50, duration=2)  # 反转2秒
    
    # 精确运动测试
    precise_control(90, speed=20)  # 旋转90度
    
    # 启动数据监控线程
    import threading
    data_thread = threading.Thread(target=read_realtime_data)
    data_thread.start()
    
    # 执行PID控制
    pid_position_control(360)  # 旋转到360度位置
```

---

### **关键参数说明**
| 参数/方法                 | 功能说明                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| `start(speed)`           | 持续转动（速度范围-100~+100）                                            |
| `run_for_seconds(t, spd)`| 定时转动（t:秒，spd:速度）                                               |
| `run_for_degrees(d, spd)`| 转动指定角度（d:度数，需主动电机支持）                                    |
| `get_speed()`            | 返回当前转速（度/秒），负值表示反转                                       |
| `get_aposition()`        | 返回电机轴的累计绝对位置（支持多圈记录）                                  |

---

### **使用注意**
1. **电源要求**：驱动电机**必须连接8V外接电源**（USB供电只能用于读取编码器）
2. **接线验证**：LED状态检查
   - **红灯常亮**：供电不足
   - **绿灯闪烁**：等待Pi通信
   - **绿灯常亮**：就绪状态
3. **多电机控制**：扩展示例
```python
# 双电机差速转向控制
left_wheel = Motor('A')
right_wheel = Motor('B')

def turn_left(speed=40):
    left_wheel.start(-speed)
    right_wheel.start(speed)
```

---

通过上述代码可实现：
- 方向/速度/时间的精准控制
- 实时位置/速度监控
- 闭环位置调节
- 多电机协同操作