import subprocess
import sys
import platform
import shutil

base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

py_file_path = os.path.join(base_path, 'FilesSpy.py')

python_path = os.path.join(base_path, 'python')

pythonw_path = os.path.join(base_path, 'pythonw')

py_file = 'FilesSpy.py'

if not os.path.exists(py_file):
    shutil.copy(py_file_path, py_file)
    print(f'已复制核心脚本: {py_file}')

mode = input("请选择运行模式 (1: 普通模式, 2: 静默模式): ")

if mode == '1':
    subprocess.run([python_path, py_file])
elif mode == '2':
    current_system = platform.system()
    if current_system == 'Windows':
        subprocess.Popen([pythonw_path, py_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    elif current_system == 'Linux':
        subprocess.Popen([python_path, py_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE, close_fds=True)
    elif current_system == 'Darwin':  # macOS
        subprocess.Popen([pythonw_path, py_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setpgrp)
    else:
        print("不支持的操作系统。")
else:
    print("无效的选择。请输入 1 或 2 来选择运行模式。")
