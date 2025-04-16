import os
import tempfile

def generate_coze_head_script(workflow_id="7490536647290699787", output_path=None):
    """
    生成用于启动Coze工作流的sh脚本
    
    参数:
        workflow_id: Coze工作流ID
        output_path: 输出脚本的路径，如果为None则使用临时文件
        
    返回:
        生成的脚本路径
    """
    # 如果未指定输出路径，则创建临时文件
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
        script_path = temp_file.name
        temp_file.close()
    else:
        script_path = output_path
    
    # 写入sh文件内容
    with open(script_path, 'w') as f:
        f.write(f'''#!/bin/bash
curl -X POST 'https://api.coze.cn/v1/workflow/stream_run' \\
-H "Authorization: Bearer pat_6Vkv0jN3NhumeU5EPbTx14b8e0g40f4gUp0LsMdgCXXx2e4XsUZu2RXwPvYUpHPt" \\
-H "Content-Type: application/json" \\
-d '{{
  "parameters": {{
    "head_input": ""
  }},
  "workflow_id": "{workflow_id}"
}}'
''')
    
    # 设置执行权限
    os.chmod(script_path, 0o755)

    
    return script_path

def generate_coze_resume_script(workflow_id="7490536647290699787", event_id="", type_num="", output_path=None):
    """
    生成用于恢复Coze工作流的sh脚本
    
    参数:
        workflow_id: Coze工作流ID
        event_id: 事件ID
        output_path: 输出脚本的路径，如果为None则使用临时文件
        
    返回:
        生成的脚本路径
    """
    # 如果未指定输出路径，则创建临时文件
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
        script_path = temp_file.name
        temp_file.close()
    else:
        script_path = output_path
    
    # 写入sh文件内容
    with open(script_path, 'w') as f:
        f.write(f'''#!/bin/bash
curl -X POST 'https://api.coze.cn/v1/workflow/stream_resume' \\
-H "Authorization: Bearer pat_6Vkv0jN3NhumeU5EPbTx14b8e0g40f4gUp0LsMdgCXXx2e4XsUZu2RXwPvYUpHPt" \\
-H "Content-Type: application/json" \\
-d '{{
  "workflow_id": "{workflow_id}",
  "event_id": "{event_id}",
  "interrupt_type": {type_num},
  "resume_data": "next"
}}'
''')
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    return script_path

