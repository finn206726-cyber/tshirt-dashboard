import subprocess
import sys
import os

python_exe = sys.executable
script_path = r'C:\Users\Administrator\.gemini\antigravity\scratch\auto_updater.py'
task_name = 'TShirtWorkbenchAutoUpdater'

print(f"[*] Python 解释器: {python_exe}")
print(f"[*] 更新脚本: {script_path}")

# 1. 尝试删除已有的同名任务
subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 2. 创建系统计划任务（每 2 小时运行一次，每天从 08:00 开始循环运行 24 小时）
# schtasks /create /tn TShirtWorkbenchAutoUpdater /tr "\"python\" \"script\"" /sc minute /mo 120 /st 08:00
cmd = [
    'schtasks', '/create',
    '/tn', task_name,
    '/tr', f'"{python_exe}" "{script_path}"',
    '/sc', 'MINUTE',
    '/mo', '120',
    '/st', '08:00',
    '/f'
]

print(f"[*] 正在注册 Windows 系统计划任务...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("错误提示:", result.stderr)

# 3. 立即运行一次验证
print("[*] 正在手动触发一次测试运行...")
run_res = subprocess.run(['schtasks', '/run', '/tn', task_name], capture_output=True, text=True)
print(run_res.stdout)

# 4. 查询任务详情与下次执行时间
print("[*] 查询计划任务状态:")
query_res = subprocess.run(['schtasks', '/query', '/tn', task_name, '/fo', 'LIST', '/v'], capture_output=True, text=True)
print(query_res.stdout)
