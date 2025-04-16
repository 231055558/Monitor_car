# 电机控制API文档

本文档详细说明了如何通过JSON命令控制电机。所有命令都通过`execute_motor_command`函数执行，该函数接收JSON格式的命令字符串，并返回执行结果。

## 命令格式

所有命令都必须是有效的JSON字符串，包含以下基本字段：

- `type`: 命令类型（必填）
- `port`: 电机端口（单电机命令必填，默认为'A'）
- `ports`: 电机端口列表（多电机命令必填，默认为['A', 'B']）

## 单电机命令

### 创建电机

```json
{
  "type": "create_motor",
  "port": "A"
}
```

### 创建多个电机

```json
{
  "type": "create_multiple_motors",
  "ports": ["B", "C"],
  "wheel_circumferences": [17.5, 17.5]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）
- `wheel_circumferences`: 轮子周长列表（厘米，默认为None，表示所有电机使用默认值17.5厘米）

### 按圈数运行

```json
{
  "type": "run_for_turns",
  "port": "A",
  "turns": 2,
  "speed": 50,
  "direction": 1
}
```

参数说明：
- `turns`: 圈数（浮点数，默认为1）
- `speed`: 速度（-100到100，默认为50）
- `direction`: 方向（1表示正向，-1表示反向，默认为1）

### 运行到指定位置

```json
{
  "type": "run_to_position",
  "port": "A",
  "position": 90,
  "speed": 50,
  "direction": "shortest"
}
```

参数说明：
- `position`: 目标位置（度数，默认为0）
- `speed`: 速度（-100到100，默认为50）
- `direction`: 方向（'shortest'表示最短路径，'clockwise'表示顺时针，'counterclockwise'表示逆时针，默认为'shortest'）

### 持续运行

```json
{
  "type": "run_forever",
  "port": "A",
  "speed": 50,
  "direction": 1
}
```

参数说明：
- `speed`: 速度（-100到100，默认为50）
- `direction`: 方向（1表示正向，-1表示反向，默认为1）

### 按距离运行

```json
{
  "type": "run_for_distance",
  "port": "A",
  "distance": 20,
  "speed": 50,
  "direction": 1
}
```

参数说明：
- `distance`: 距离（厘米，默认为10）
- `speed`: 速度（-100到100，默认为50）
- `direction`: 方向（1表示正向，-1表示反向，默认为1）

### 停止电机

```json
{
  "type": "stop",
  "port": "A"
}
```

### 获取速度

```json
{
  "type": "get_speed",
  "port": "A"
}
```

### 获取位置

```json
{
  "type": "get_position",
  "port": "A"
}
```

### 释放电机

```json
{
  "type": "release",
  "port": "A"
}
```

## 多电机命令

### 多电机按圈数运行

```json
{
  "type": "run_motors_for_turns",
  "ports": ["A", "B"],
  "turns": 2,
  "speeds": [50, 50],
  "directions": [1, -1]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）
- `turns`: 圈数（浮点数或列表，默认为1）
- `speeds`: 速度列表（-100到100，默认为None，表示所有电机使用相同速度）
- `directions`: 方向列表（1表示正向，-1表示反向，默认为None，表示所有电机使用相同方向）

### 多电机运行到指定位置

```json
{
  "type": "run_motors_to_positions",
  "ports": ["A", "B"],
  "positions": [90, 270],
  "speeds": [50, 50],
  "direction": "shortest"
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）
- `positions`: 目标位置列表（度数，默认为[0, 0]）
- `speeds`: 速度列表（-100到100，默认为None，表示所有电机使用相同速度）
- `direction`: 方向（'shortest'表示最短路径，'clockwise'表示顺时针，'counterclockwise'表示逆时针，默认为'shortest'）

### 停止多个电机

```json
{
  "type": "stop_motors",
  "ports": ["A", "B"]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）

### 多电机持续运行

```json
{
  "type": "run_motors_forever",
  "ports": ["A", "B"],
  "speeds": [50, 50],
  "directions": [1, -1]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）
- `speeds`: 速度列表（-100到100，默认为None，表示所有电机使用相同速度）
- `directions`: 方向列表（1表示正向，-1表示反向，默认为None，表示所有电机使用相同方向）

### 多电机按距离运行

```json
{
  "type": "run_motors_for_distances",
  "ports": ["A", "B"],
  "distances": [20, 20],
  "speeds": [50, 50],
  "directions": [1, -1]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）
- `distances`: 距离列表（厘米，默认为[10, 10]）
- `speeds`: 速度列表（-100到100，默认为None，表示所有电机使用相同速度）
- `directions`: 方向列表（1表示正向，-1表示反向，默认为None，表示所有电机使用相同方向）

### 获取多个电机的速度

```json
{
  "type": "get_motors_speeds",
  "ports": ["A", "B"],
  "directions": [1, -1]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）
- `directions`: 方向列表（1表示正向，-1表示反向，默认为None，表示所有电机使用相同方向）

### 获取多个电机的位置

```json
{
  "type": "get_motors_positions",
  "ports": ["A", "B"]
}
```

参数说明：
- `ports`: 电机端口列表（默认为['A', 'B']）

### 释放所有端口

```json
{
  "type": "release_all_ports"
}
```

## 返回值格式

所有命令执行后都会返回一个JSON格式的结果，包含以下字段：

- `success`: 布尔值，表示命令是否成功执行
- `message`: 字符串，描述执行结果（成功时）
- `error`: 字符串，描述错误信息（失败时）
- 其他特定字段：根据命令类型返回不同的数据

### 成功示例

```json
{
  "success": true,
  "message": "电机 A 运行 2 圈"
}
```

### 失败示例

```json
{
  "success": false,
  "error": "端口 A 已被使用，请选择其他端口或先释放该端口"
}
```

## 电机实例管理

本库实现了电机实例的持久化管理，避免重复创建电机实例导致的回弹问题。使用JSON命令接口时，电机实例会被自动管理：

1. 首次使用某个端口时，会创建电机实例并存储在内部字典中
2. 后续使用同一端口的命令会重用已创建的实例
3. 使用`release`命令可以释放单个电机
4. 使用`release_all_ports`命令可以释放所有电机

这种方式可以确保电机的状态一致性，避免因重复创建实例导致的问题。

## 使用示例

### Python代码示例

```python
import json
from motor_utils import execute_motor_command

# 创建电机
command = json.dumps({
    'type': 'create_motor',
    'port': 'A'
})
result = execute_motor_command(command)
print(result)

# 创建多个电机
command = json.dumps({
    'type': 'create_multiple_motors',
    'ports': ['B', 'C']
})
result = execute_motor_command(command)
print(result)

# 按圈数运行
command = json.dumps({
    'type': 'run_for_turns',
    'port': 'A',
    'turns': 2,
    'speed': 50
})
result = execute_motor_command(command)
print(result)

# 获取位置
command = json.dumps({
    'type': 'get_position',
    'port': 'A'
})
result = execute_motor_command(command)
print(result)

# 停止电机
command = json.dumps({
    'type': 'stop',
    'port': 'A'
})
result = execute_motor_command(command)
print(result)

# 释放电机
command = json.dumps({
    'type': 'release',
    'port': 'A'
})
result = execute_motor_command(command)
print(result)
```

### 多电机控制示例

```python
import json
from motor_utils import execute_motor_command

# 创建多个电机
command = json.dumps({
    'type': 'create_multiple_motors',
    'ports': ['A', 'B', 'C']
})
result = execute_motor_command(command)
print(result)

# 多电机按圈数运行
command = json.dumps({
    'type': 'run_motors_for_turns',
    'ports': ['A', 'B'],
    'turns': 2,
    'speeds': [50, 50],
    'directions': [1, -1]
})
result = execute_motor_command(command)
print(result)

# 获取多个电机的位置
command = json.dumps({
    'type': 'get_motors_positions',
    'ports': ['A', 'B']
})
result = execute_motor_command(command)
print(result)

# 停止多个电机
command = json.dumps({
    'type': 'stop_motors',
    'ports': ['A', 'B']
})
result = execute_motor_command(command)
print(result)

# 释放所有端口
command = json.dumps({
    'type': 'release_all_ports'
})
result = execute_motor_command(command)
print(result)
```

## 注意事项

1. 在使用多电机命令时，确保指定的端口数量与参数列表长度匹配。
2. 在执行命令前，确保电机已正确连接到指定端口。
3. 使用完电机后，记得释放端口，以避免端口冲突。
4. 对于持续运行的命令，需要手动调用停止命令来停止电机。
5. 所有角度值都会被转换为整数，并且会被限制在0-359度范围内。
6. 使用JSON命令接口时，建议先创建电机，再进行控制操作。
7. 多电机控制时，确保所有电机都已创建。 