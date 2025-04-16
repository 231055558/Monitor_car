import subprocess
import json
import os
import sys
import re
import tempfile
current_dir = "/mnt/Monitor_car"
sys.path.append(current_dir)

# 导入脚本生成函数
from utils.communication.generate_coze_script import generate_coze_head_script, generate_coze_resume_script
from utils.lego_motor.lego_motor_utils import execute_motor_command
def extract_resume_num(data_str):
    # 去除字符串开头的"data: "
    data_str = data_str.lstrip('data: ')
    try:
        # 解析JSON数据
        data = json.loads(data_str)
        # 提取event_id中的第一串数字
        event_id_num = data["interrupt_data"]["event_id"]
        type_num = data["interrupt_data"]["type"]
        return event_id_num, type_num
    except (KeyError, IndexError, json.JSONDecodeError):
        print("解析字符串时出现错误，请检查输入字符串的格式。")
        return None

def content_text(data_str):
    # 去除字符串开头的"data: "
    data_str = data_str.lstrip('data: ')
    try:
        # 解析JSON数据
        data = json.loads(data_str)
        # 提取content
        content = data["content"]
        node_is_finish = data.get("node_is_finish", True)
        return content, node_is_finish
    except (KeyError, IndexError, json.JSONDecodeError):
        print("解析字符串时出现错误，请检查输入字符串的格式。")
        return None, True
    
def run_coze_workflow(workflow_id="7490536647290699787", script_path=None):
    """
    执行Coze工作流并捕获其输出，只显示工作流的实际输出
    
    参数:
        workflow_id: Coze工作流ID
        head_input: 工作流的输入参数
        script_path: 脚本路径，如果为None则自动生成
    """
    # 如果未提供脚本路径，则生成脚本
    script_path = generate_coze_head_script(workflow_id)
    
    try:
        # 执行shell脚本并捕获输出
        task_flag = 0
        bash_flag = 0

        # 实时输出结果，但只显示工作流相关输出
        while True:
            if bash_flag == 0:
                process = subprocess.Popen(
                    ["bash", script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                bash_flag = 1
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            elif output == "event: Message\n":
                task_flag = 1
            elif output == "event: Interrupt\n":
                task_flag = 2

            elif output and task_flag == 1:
                content = content_text(output.strip())
                if isinstance(content, tuple):
                    json_str, _ = content
                    if 'type' in json_str:
                        try:
                            command_data = json.loads(json_str)
                            if isinstance(command_data, dict) and 'type' in command_data:
                                # 如果是电机控制命令，则执行
                                result = execute_motor_command(json.dumps(command_data))
                                print(result)
                            else:
                                print(json_str)
                        except json.JSONDecodeError:
                            print(json_str)
                task_flag = 0

            elif output and task_flag == 2:
                event_id, type_num = extract_resume_num(output.strip())
                script_path = generate_coze_resume_script(workflow_id, event_id, type_num)
                bash_flag = 0
                task_flag = 0
        
        # 获取返回码
        return_code = process.poll()
        
        # 获取所有输出
        stdout, stderr = process.communicate()

    finally:
        # 如果是临时生成的脚本，则删除
        if script_path is None or script_path.startswith(tempfile.gettempdir()):
            try:
                os.unlink(script_path)
            except:
                pass

if __name__ == "__main__":
    # 可以从命令行参数获取workflow_id和head_input

    workflow_id = "7492954257341513755"  # 默认工作流ID

    if len(sys.argv) > 3:
        script_path = sys.argv[3]
    else:
        script_path = None
    
    result = run_coze_workflow(workflow_id, script_path)