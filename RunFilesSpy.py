import subprocess

mode = input("请选择运行模式 (1: 普通模式, 2: 静默模式): ")

if mode == '1':
    subprocess.run(['python', 'FilesSpy.py'])
elif mode == '2':
    subprocess.Popen(['python', 'FilesSpy.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
else:
    print("无效的选择。请输入 1 或 2 来选择运行模式。")