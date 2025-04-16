from buildhat import Motor
import time
import math
import sys
import threading
import queue
import json

# 全局端口管理
_used_ports = set()

# 全局电机实例字典
_active_motors = {}

class MotorController:
    def __init__(self, port='A', wheel_circumference=17.5):
        """
        初始化电机控制器
        :param port: 电机端口，如 'A', 'B', 'C', 'D'
        :param wheel_circumference: 轮子周长（厘米），默认为17.5厘米
        """
        # 检查端口是否已被使用
        if port in _used_ports:
            raise ValueError(f"端口 {port} 已被使用，请选择其他端口或先释放该端口")
        
        try:
            self.motor = Motor(port)
            self.port = port
            self.wheel_circumference = wheel_circumference
            
            # 标记端口为已使用
            _used_ports.add(port)
        except Exception as e:
            print(f"初始化电机时出错: {e}")
            raise
        
    def __del__(self):
        """
        析构函数，释放端口
        """
        if hasattr(self, 'port') and self.port in _used_ports:
            _used_ports.remove(self.port)
    
    def start(self, speed=50, direction=1):
        """
        启动电机，按照指定方向以指定速度运行
        :param speed: 速度，范围 -100 到 100
        :param direction: 方向，1表示正向，-1表示反向
        :return: None
        """
        adjusted_speed = speed * direction
        self.motor.start(abs(adjusted_speed))
        
    def stop(self):
        """
        立即停止电机运动
        :return: None
        """
        self.motor.stop()
        
    def get_speed(self):
        """
        获取当前速度
        :return: 当前速度
        """
        return self.motor.get_speed()
        
    def get_position(self):
        """
        获取当前位置
        :return: 当前位置（度数）
        """
        return self.motor.get_position()
        
    def release(self):
        """
        释放电机端口
        :return: None
        """
        if self.port in _used_ports:
            _used_ports.remove(self.port)

# 独立函数，用于控制电机
def run_for_turns(motor, turns, speed=50, direction=1):
    """
    让电机按照指定方向以指定速度运行n圈
    :param motor: MotorController实例
    :param turns: 圈数（浮点数）
    :param speed: 速度，范围 -100 到 100
    :param direction: 方向，1表示正向，-1表示反向
    :return: None
    """
    degrees = turns * 360
    adjusted_speed = speed * direction
    motor.motor.run_for_degrees(degrees, abs(adjusted_speed))
    

def run_to_position(motor, position, speed=50, direction='shortest'):
    """
    让电机按照指定方向或最短路径以指定速度运行至指定位置
    :param motor: MotorController实例
    :param position: 目标位置（度数）
    :param speed: 速度，范围 -100 到 100
    :param direction: 方向，可选 'shortest', 'clockwise', 'counterclockwise'
    :return: None
    """
    current_pos = motor.motor.get_position()
    
    # 确保position是整数，因为buildhat库要求角度必须是整数
    position = int(position)
    
    # 确保position在有效范围内 (0-359)
    position = position % 360
    
    if direction == 'shortest':
        diff = position - current_pos
        if abs(diff) > 180:
            if diff > 0:
                position -= 360
            else:
                position += 360
    elif direction == 'counterclockwise':
        if position > current_pos:
            position -= 360
    
    # 再次确保position在有效范围内
    position = position % 360
    
    # 打印调试信息
    print(f"当前位置: {current_pos}, 目标位置: {position}")
    
    try:
        motor.motor.run_to_position(position, speed)
    except Exception as e:
        print(f"运行到位置时出错: {e}")
        # 尝试使用另一种方法
        try:
            # 计算需要转动的角度
            diff = position - current_pos
            if abs(diff) > 180:
                if diff > 0:
                    diff -= 360
                else:
                    diff += 360
            
            # 使用run_for_degrees代替run_to_position
            motor.motor.run_for_degrees(diff, speed)
        except Exception as e2:
            print(f"备用方法也失败: {e2}")
            raise

def run_forever(motor, speed=50, direction=1):
    """
    让电机按照指定方向以指定速度一直运行
    :param motor: MotorController实例
    :param speed: 速度，范围 -100 到 100
    :param direction: 方向，1表示正向，-1表示反向
    :return: None
    """
    adjusted_speed = speed * direction
    motor.motor.start(abs(adjusted_speed))

def run_for_distance(motor, distance, speed=50, direction=1):
    """
    让电机按照指定方向以指定速度运行n厘米
    :param motor: MotorController实例
    :param distance: 距离（厘米）
    :param speed: 速度，范围 -100 到 100
    :param direction: 方向，1表示正向，-1表示反向
    :return: None
    """
    # 计算需要转动的圈数
    turns = distance / motor.wheel_circumference
    run_for_turns(motor, turns, speed, direction)

# 多线程同步控制函数
def _motor_thread(motor, action, *args, **kwargs):
    """
    电机线程函数
    :param motor: MotorController实例
    :param action: 要执行的动作函数
    :param args: 位置参数
    :param kwargs: 关键字参数
    :return: None
    """
    action(motor, *args, **kwargs)

def create_multiple_motors(ports, wheel_circumferences=None):
    """
    创建多个电机控制器
    :param ports: 电机端口列表，如 ['A', 'B', 'C']
    :param wheel_circumferences: 轮子周长列表（厘米），如果为None则使用默认值
    :return: MotorController实例列表
    """
    if wheel_circumferences is None:
        wheel_circumferences = [17.5] * len(ports)
    
    motors = []
    for port, wheel_circumference in zip(ports, wheel_circumferences):
        motor = create_motor(port, wheel_circumference)
        motors.append(motor)
    
    return motors

def run_motors_for_turns(motors, turns, speeds=None, directions=None):
    """
    让多个电机按照指定方向以指定速度同步运行n圈
    :param motors: MotorController实例列表
    :param turns: 圈数（浮点数）或圈数列表
    :param speeds: 速度列表，范围 -100 到 100
    :param directions: 方向列表，1表示正向，-1表示反向
    :return: None
    """
    if isinstance(turns, (int, float)):
        turns = [turns] * len(motors)
        
    if speeds is None:
        speeds = [50] * len(motors)
        
    if directions is None:
        directions = [1] * len(motors)
    
    # 创建线程列表
    threads = []
    
    # 为每个电机创建一个线程
    for motor, turn, speed, direction in zip(motors, turns, speeds, directions):
        degrees = turn * 360
        adjusted_speed = speed * direction
        
        # 创建线程，但不启动
        thread = threading.Thread(
            target=_motor_thread,
            args=(motor, lambda m, d, s: m.motor.run_for_degrees(d, s), degrees, abs(adjusted_speed))
        )
        threads.append(thread)
    
    # 同时启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

def run_motors_to_positions(motors, positions, speeds=None, direction='shortest'):
    """
    让多个电机按照指定方向或最短路径以指定速度同步运行至指定位置
    :param motors: MotorController实例列表
    :param positions: 目标位置列表（度数）
    :param speeds: 速度列表，范围 -100 到 100
    :param direction: 方向，可选 'shortest', 'clockwise', 'counterclockwise'
    :return: None
    """
    if isinstance(positions, (int, float)):
        positions = [positions] * len(motors)
        
    if speeds is None:
        speeds = [50] * len(motors)
    
    # 创建线程列表
    threads = []
    
    # 为每个电机创建一个线程
    for motor, position, speed in zip(motors, positions, speeds):
        # 确保position是整数
        position = int(position)
        
        # 计算目标位置
        current_pos = motor.motor.get_position()
        
        if direction == 'shortest':
            diff = position - current_pos
            if abs(diff) > 180:
                if diff > 0:
                    position -= 360
                else:
                    position += 360
        elif direction == 'counterclockwise':
            if position > current_pos:
                position -= 360
                
        # 确保position在有效范围内
        position = position % 360
        
        # 创建线程，但不启动
        thread = threading.Thread(
            target=_motor_thread,
            args=(motor, lambda m, p, s: m.motor.run_to_position(p, s), position, speed)
        )
        threads.append(thread)
    
    # 同时启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

def stop_motors(motors):
    """
    立即停止所有电机运动
    :param motors: MotorController实例列表
    :return: None
    """
    # 创建线程列表
    threads = []
    
    # 为每个电机创建一个线程
    for motor in motors:
        thread = threading.Thread(target=motor.stop)
        threads.append(thread)
    
    # 同时启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

def run_motors_forever(motors, speeds=None, directions=None):
    """
    让多个电机按照指定方向以指定速度同步一直运行
    :param motors: MotorController实例列表
    :param speeds: 速度列表，范围 -100 到 100
    :param directions: 方向列表，1表示正向，-1表示反向
    :return: None
    """
    if speeds is None:
        speeds = [50] * len(motors)
        
    if directions is None:
        directions = [1] * len(motors)
    
    # 创建线程列表
    threads = []
    
    # 为每个电机创建一个线程
    for motor, speed, direction in zip(motors, speeds, directions):
        adjusted_speed = speed * direction
        
        # 创建线程，但不启动
        thread = threading.Thread(
            target=_motor_thread,
            args=(motor, lambda m, s: m.motor.start(s), abs(adjusted_speed))
        )
        threads.append(thread)
    
    # 同时启动所有线程
    for thread in threads:
        thread.start()
    
    # 注意：这里不等待线程完成，因为电机需要一直运行
    # 返回线程列表，以便调用者可以在需要时停止电机
    return threads

def run_motors_for_distances(motors, distances, speeds=None, directions=None):
    """
    让多个电机按照指定方向以指定速度同步运行n厘米
    :param motors: MotorController实例列表
    :param distances: 距离列表（厘米）
    :param speeds: 速度列表，范围 -100 到 100
    :param directions: 方向列表，1表示正向，-1表示反向
    :return: None
    """
    if isinstance(distances, (int, float)):
        distances = [distances] * len(motors)
        
    if speeds is None:
        speeds = [50] * len(motors)
        
    if directions is None:
        directions = [1] * len(motors)
    
    # 创建线程列表
    threads = []
    
    # 为每个电机创建一个线程
    for motor, distance, speed, direction in zip(motors, distances, speeds, directions):
        # 计算需要转动的圈数
        turns = distance / motor.wheel_circumference
        degrees = turns * 360
        adjusted_speed = speed * direction
        
        # 创建线程，但不启动
        thread = threading.Thread(
            target=_motor_thread,
            args=(motor, lambda m, d, s: m.motor.run_for_degrees(d, s), degrees, abs(adjusted_speed))
        )
        threads.append(thread)
    
    # 同时启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

def get_motors_speeds(motors, directions=None):
    """
    获取所有电机的速度
    :param motors: MotorController实例列表
    :param directions: 方向列表，1表示正向，-1表示反向
    :return: 速度列表
    """
    if directions is None:
        directions = [1] * len(motors)
    return [motor.get_speed() * direction for motor, direction in zip(motors, directions)]
    
def get_motors_positions(motors):
    """
    获取所有电机的位置
    :param motors: MotorController实例列表
    :return: 位置列表（度数）
    """
    return [motor.get_position() for motor in motors]

# 便捷函数，用于快速创建和控制电机
def create_motor(port='A', wheel_circumference=17.5):
    """
    创建一个电机控制器
    :param port: 电机端口
    :param wheel_circumference: 轮子周长（厘米）
    :return: MotorController实例
    """
    return MotorController(port, wheel_circumference)

# 释放所有端口
def release_all_ports():
    """
    释放所有已使用的端口
    :return: None
    """
    global _used_ports
    _used_ports.clear()

# 测试函数
def test_motor_control():
    """测试所有电机控制功能"""
    # 确保开始时没有端口被占用
    release_all_ports()
    
    print("开始测试单电机控制...")
    
    try:
        # 测试单电机控制
        command = json.dumps({
            'type': 'create_motor',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"创建电机结果: {result}")
        
        # 测试多电机初始化
        command = json.dumps({
            'type': 'create_multiple_motors',
            'ports': ['B', 'C']
        })
        result = execute_motor_command(command)
        print(f"创建多电机结果: {result}")
        
        print("\n1. 测试按圈数旋转")
        command = json.dumps({
            'type': 'run_for_turns',
            'port': 'A',
            'turns': 2,
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"按圈数旋转结果: {result}")
        time.sleep(1)
        
        print("\n2. 测试旋转到指定位置")
        command = json.dumps({
            'type': 'run_to_position',
            'port': 'A',
            'position': 0,
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"旋转到指定位置结果: {result}")
        time.sleep(1)
        
        print("\n3. 测试按距离旋转")
        command = json.dumps({
            'type': 'run_for_distance',
            'port': 'A',
            'distance': 50,
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"按距离旋转结果: {result}")
        time.sleep(1)
        
        print("\n4. 测试一直运行")
        command = json.dumps({
            'type': 'run_forever',
            'port': 'A',
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"一直运行结果: {result}")
        time.sleep(2)
        
        command = json.dumps({
            'type': 'stop',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"停止电机结果: {result}")
        
        print("\n5. 测试读取速度和位置")
        command = json.dumps({
            'type': 'get_speed',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"获取速度结果: {result}")
        
        command = json.dumps({
            'type': 'get_position',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"获取位置结果: {result}")
        
        print("\n单电机测试完成！")
    except Exception as e:
        print(f"单电机测试出错: {e}")
        # 确保释放端口
        try:
            command = json.dumps({
                'type': 'release',
                'port': 'A'
            })
            execute_motor_command(command)
        except:
            pass
    
    print("\n开始测试多电机控制...")
    
    try:
        # 测试多电机控制 - 使用不同的端口
        command = json.dumps({
            'type': 'run_motors_for_turns',
            'ports': ['B', 'C'],
            'turns': 2,
            'speeds': [30, 30],
            'directions': [1, -1]
        })
        result = execute_motor_command(command)
        print(f"多电机同步旋转结果: {result}")
        time.sleep(1)
        
        print("\n2. 测试多电机同步停止")
        command = json.dumps({
            'type': 'stop_motors',
            'ports': ['B', 'C']
        })
        result = execute_motor_command(command)
        print(f"多电机同步停止结果: {result}")
        
        print("\n3. 测试多电机按距离运行")
        command = json.dumps({
            'type': 'run_motors_for_distances',
            'ports': ['B', 'C'],
            'distances': [30, 30],
            'speeds': [30, 30],
            'directions': [1, -1]
        })
        result = execute_motor_command(command)
        print(f"多电机按距离运行结果: {result}")
        time.sleep(1)
        
        print("\n4. 测试读取多电机状态")
        command = json.dumps({
            'type': 'get_motors_speeds',
            'ports': ['B', 'C'],
            'directions': [1, -1]
        })
        result = execute_motor_command(command)
        print(f"获取多电机速度结果: {result}")
        
        command = json.dumps({
            'type': 'get_motors_positions',
            'ports': ['B', 'C']
        })
        result = execute_motor_command(command)
        print(f"获取多电机位置结果: {result}")
        
    except Exception as e:
        print(f"多电机测试出错: {e}")
        # 确保释放端口
        try:
            command = json.dumps({
                'type': 'release_all_ports'
            })
            execute_motor_command(command)
        except:
            pass
    
    print("\n所有测试完成！")

# 单独测试单电机
def test_single_motor():
    """测试单电机控制功能"""
    release_all_ports()
    
    try:
        command = json.dumps({
            'type': 'create_motor',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"创建电机结果: {result}")
        
        print("1. 测试按圈数旋转")
        command = json.dumps({
            'type': 'run_for_turns',
            'port': 'A',
            'turns': 2,
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"按圈数旋转结果: {result}")
        time.sleep(1)
        
        print("2. 测试旋转到指定位置")
        command = json.dumps({
            'type': 'run_to_position',
            'port': 'A',
            'position': 0,
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"旋转到指定位置结果: {result}")
        time.sleep(1)
        
        print("3. 测试按距离旋转")
        command = json.dumps({
            'type': 'run_for_distance',
            'port': 'A',
            'distance': 50,
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"按距离旋转结果: {result}")
        time.sleep(1)
        
        print("4. 测试一直运行")
        command = json.dumps({
            'type': 'run_forever',
            'port': 'A',
            'speed': 30
        })
        result = execute_motor_command(command)
        print(f"一直运行结果: {result}")
        time.sleep(2)
        
        command = json.dumps({
            'type': 'stop',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"停止电机结果: {result}")
        
        print("5. 测试读取速度和位置")
        command = json.dumps({
            'type': 'get_speed',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"获取速度结果: {result}")
        
        command = json.dumps({
            'type': 'get_position',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"获取位置结果: {result}")
        
        command = json.dumps({
            'type': 'release',
            'port': 'A'
        })
        result = execute_motor_command(command)
        print(f"释放电机结果: {result}")
        
        print("单电机测试完成！")
    except Exception as e:
        print(f"单电机测试出错: {e}")
        try:
            command = json.dumps({
                'type': 'release',
                'port': 'A'
            })
            execute_motor_command(command)
        except:
            pass

# 单独测试多电机
def test_multi_motor():
    """测试多电机控制功能"""
    release_all_ports()
    
    try:
        print("1. 测试多电机同步旋转")
        command = json.dumps({
            'type': 'run_motors_for_turns',
            'ports': ['B', 'C'],
            'turns': 2,
            'speeds': [30, 30],
            'directions': [1, -1]
        })
        result = execute_motor_command(command)
        print(f"多电机同步旋转结果: {result}")
        time.sleep(1)
        
        print("2. 测试多电机同步停止")
        command = json.dumps({
            'type': 'stop_motors',
            'ports': ['B', 'C']
        })
        result = execute_motor_command(command)
        print(f"多电机同步停止结果: {result}")
        
        print("3. 测试多电机按距离运行")
        command = json.dumps({
            'type': 'run_motors_for_distances',
            'ports': ['B', 'C'],
            'distances': [30, 30],
            'speeds': [30, 30],
            'directions': [1, -1]
        })
        result = execute_motor_command(command)
        print(f"多电机按距离运行结果: {result}")
        time.sleep(1)
        
        print("4. 测试读取多电机状态")
        command = json.dumps({
            'type': 'get_motors_speeds',
            'ports': ['B', 'C'],
            'directions': [1, -1]
        })
        result = execute_motor_command(command)
        print(f"获取多电机速度结果: {result}")
        
        command = json.dumps({
            'type': 'get_motors_positions',
            'ports': ['B', 'C']
        })
        result = execute_motor_command(command)
        print(f"获取多电机位置结果: {result}")
        
        command = json.dumps({
            'type': 'release_all_ports'
        })
        result = execute_motor_command(command)
        print(f"释放所有端口结果: {result}")
        
        print("多电机测试完成！")
    except Exception as e:
        print(f"多电机测试出错: {e}")
        try:
            command = json.dumps({
                'type': 'release_all_ports'
            })
            execute_motor_command(command)
        except:
            pass


def execute_motor_command(command_json):
    """
    执行从JSON接收到的电机控制命令
    
    参数:
        command_json (str): JSON格式的命令字符串
        
    返回:
        dict: 包含执行结果的字典
    """
    global _active_motors
    
    try:
        # 解析JSON命令
        command = json.loads(command_json)
        
        # 检查命令类型
        command_type = command.get('type')
        if not command_type:
            return {'success': False, 'error': '缺少命令类型'}
        
        # 获取电机端口
        port = command.get('port', 'A')
        
        # 根据命令类型执行相应操作
        if command_type == 'create_motor':
            # 检查电机是否已存在
            if port in _active_motors:
                return {'success': True, 'message': f'电机 {port} 已存在'}
            
            # 创建电机
            motor = create_motor(port)
            _active_motors[port] = motor
            return {'success': True, 'message': f'电机 {port} 创建成功'}
            
        elif command_type == 'create_multiple_motors':
            # 获取端口列表
            ports = command.get('ports', ['A', 'B'])
            wheel_circumferences = command.get('wheel_circumferences', None)
            
            # 检查是否所有电机都已存在
            all_exist = all(p in _active_motors for p in ports)
            if all_exist:
                return {'success': True, 'message': f'电机 {ports} 已存在'}
            
            # 创建不存在的电机
            created_ports = []
            for p in ports:
                if p not in _active_motors:
                    motor = create_motor(p)
                    _active_motors[p] = motor
                    created_ports.append(p)
            
            if created_ports:
                return {'success': True, 'message': f'电机 {created_ports} 创建成功'}
            else:
                return {'success': True, 'message': f'所有电机 {ports} 已存在'}
            
        elif command_type == 'run_for_turns':
            # 按圈数运行
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            turns = command.get('turns', 1)
            speed = command.get('speed', 50)
            direction = command.get('direction', 1)
            run_for_turns(motor, turns, speed, direction)
            return {'success': True, 'message': f'电机 {port} 运行 {turns} 圈'}
            
        elif command_type == 'run_to_position':
            # 运行到指定位置
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            position = command.get('position', 0)
            speed = command.get('speed', 50)
            direction = command.get('direction', 'shortest')
            run_to_position(motor, position, speed, direction)
            return {'success': True, 'message': f'电机 {port} 运行到位置 {position}'}
            
        elif command_type == 'run_forever':
            # 一直运行
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            speed = command.get('speed', 50)
            direction = command.get('direction', 1)
            run_forever(motor, speed, direction)
            return {'success': True, 'message': f'电机 {port} 持续运行'}
            
        elif command_type == 'run_for_distance':
            # 按距离运行
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            distance = command.get('distance', 10)
            speed = command.get('speed', 50)
            direction = command.get('direction', 1)
            run_for_distance(motor, distance, speed, direction)
            return {'success': True, 'message': f'电机 {port} 运行 {distance} 厘米'}
            
        elif command_type == 'stop':
            # 停止电机
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            motor.stop()
            return {'success': True, 'message': f'电机 {port} 已停止'}
            
        elif command_type == 'get_speed':
            # 获取速度
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            speed = motor.get_speed()
            return {'success': True, 'speed': speed}
            
        elif command_type == 'get_position':
            # 获取位置
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            position = motor.get_position()
            return {'success': True, 'position': position}
            
        elif command_type == 'release':
            # 释放电机
            motor = _active_motors.get(port)
            if not motor:
                return {'success': False, 'error': f'电机 {port} 未创建'}
                
            motor.release()
            del _active_motors[port]
            return {'success': True, 'message': f'电机 {port} 已释放'}
            
        elif command_type == 'run_motors_for_turns':
            # 多电机按圈数运行
            ports = command.get('ports', ['A', 'B'])
            turns = command.get('turns', 1)
            speeds = command.get('speeds', None)
            directions = command.get('directions', None)
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            run_motors_for_turns(motors, turns, speeds, directions)
            return {'success': True, 'message': f'电机 {ports} 运行 {turns} 圈'}
            
        elif command_type == 'run_motors_to_positions':
            # 多电机运行到指定位置
            ports = command.get('ports', ['A', 'B'])
            positions = command.get('positions', [0, 0])
            speeds = command.get('speeds', None)
            direction = command.get('direction', 'shortest')
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            run_motors_to_positions(motors, positions, speeds, direction)
            return {'success': True, 'message': f'电机 {ports} 运行到位置 {positions}'}
            
        elif command_type == 'stop_motors':
            # 停止多个电机
            ports = command.get('ports', ['A', 'B'])
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            stop_motors(motors)
            return {'success': True, 'message': f'电机 {ports} 已停止'}
            
        elif command_type == 'run_motors_forever':
            # 多电机持续运行
            ports = command.get('ports', ['A', 'B'])
            speeds = command.get('speeds', None)
            directions = command.get('directions', None)
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            threads = run_motors_forever(motors, speeds, directions)
            return {'success': True, 'message': f'电机 {ports} 持续运行', 'threads': len(threads)}
            
        elif command_type == 'run_motors_for_distances':
            # 多电机按距离运行
            ports = command.get('ports', ['A', 'B'])
            distances = command.get('distances', [10, 10])
            speeds = command.get('speeds', None)
            directions = command.get('directions', None)
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            run_motors_for_distances(motors, distances, speeds, directions)
            return {'success': True, 'message': f'电机 {ports} 运行距离 {distances}'}
            
        elif command_type == 'get_motors_speeds':
            # 获取多个电机的速度
            ports = command.get('ports', ['A', 'B'])
            directions = command.get('directions', None)
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            speeds = get_motors_speeds(motors, directions)
            return {'success': True, 'speeds': speeds}
            
        elif command_type == 'get_motors_positions':
            # 获取多个电机的位置
            ports = command.get('ports', ['A', 'B'])
            
            # 检查所有电机是否已创建
            motors = []
            for p in ports:
                motor = _active_motors.get(p)
                if not motor:
                    return {'success': False, 'error': f'电机 {p} 未创建'}
                motors.append(motor)
                
            positions = get_motors_positions(motors)
            return {'success': True, 'positions': positions}
            
        elif command_type == 'release_all_ports':
            # 释放所有端口
            for port, motor in list(_active_motors.items()):
                motor.release()
                del _active_motors[port]
            return {'success': True, 'message': '所有端口已释放'}
            
        else:
            return {'success': False, 'error': f'未知命令类型: {command_type}'}
            
    except json.JSONDecodeError:
        return {'success': False, 'error': 'JSON格式错误'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 测试JSON命令执行
def test_json_command():
    """测试JSON命令执行功能"""
    # 测试创建电机
    command = json.dumps({
        'type': 'create_motor',
        'port': 'A'
    })
    result = execute_motor_command(command)
    print(f"创建电机结果: {result}")
    
    # 测试按圈数运行
    command = json.dumps({
        'type': 'run_for_turns',
        'port': 'A',
        'turns': 1,
        'speed': 30
    })
    result = execute_motor_command(command)
    print(f"按圈数运行结果: {result}")
    
    # 测试获取位置
    command = json.dumps({
        'type': 'get_position',
        'port': 'A'
    })
    result = execute_motor_command(command)
    print(f"获取位置结果: {result}")
    
    # 测试停止电机
    command = json.dumps({
        'type': 'stop',
        'port': 'A'
    })
    result = execute_motor_command(command)
    print(f"停止电机结果: {result}")
    
    # 测试释放电机
    command = json.dumps({
        'type': 'release',
        'port': 'A'
    })
    result = execute_motor_command(command)
    print(f"释放电机结果: {result}")

if __name__ == "__main__":
    # 根据命令行参数选择测试模式
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            test_single_motor()
        elif sys.argv[1] == "multi":
            test_multi_motor()
        elif sys.argv[1] == "json":
            test_json_command()
        else:
            test_motor_control()
    else:
        test_motor_control() 