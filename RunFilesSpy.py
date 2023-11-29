import subprocess
import sys
import platform

mode = input("请选择运行模式 (1: 普通模式, 2: 静默模式): ")

if mode == '1':
    subprocess.run(['python', 'FilesSpy.py'])
elif mode == '2':
    current_system = platform.system()
    if current_system == 'Windows':
        subprocess.Popen(['python', 'FilesSpy.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    elif current_system == 'Linux':
        subprocess.Popen(['python', 'FilesSpy.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE, close_fds=True)
    elif current_system == 'Darwin':  # macOS
        subprocess.Popen(['python', 'FilesSpy.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setpgrp)
    else:
        print("不支持的操作系统。")
else:
    print("无效的选择。请输入 1 或 2 来选择运行模式。")
