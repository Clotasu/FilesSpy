import os
import shutil
import configparser
import logging
from logging.handlers import TimedRotatingFileHandler
import time
from datetime import datetime, time as time2

class FilesSpy:
    def __init__(self, config_path='config.ini'):
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, config_path)
        config = configparser.ConfigParser()
        config.read(config_path)
        self.destination_path = config.get('FilesSpyConfig', 'destination_path')
        self.sources_path = config.get('FilesSpyConfig', 'sources_path')
        self.include_names = config.get('FilesSpyConfig', 'include_names').split(',')
        self.any = config.getboolean('FilesSpyConfig', 'any')
        self.use_schedule = config.getboolean('ScheduleConfig', 'use_schedule')
        if self.use_schedule == True: # 当启用时间表时才设置相关变量
            self.schedule_start_hour = config.getint('ScheduleConfig', 'schedule_start_hour')
            self.schedule_start_minute = config.getint('ScheduleConfig', 'schedule_start_minute')
            self.schedule_stop_hour = config.getint('ScheduleConfig', 'schedule_stop_hour')
            self.schedule_stop_minute = config.getint('ScheduleConfig', 'schedule_stop_minute')
            self.start_time = time2(self.schedule_start_hour, self.schedule_start_minute)
            self.end_time = time2(self.schedule_stop_hour, self.schedule_stop_minute)
        self.retry_count = 0

    def FilesCopy(self):
        try: 
            if os.path.exists(self.sources_path):
                if self.any == False: # 匹配字段 & 文件复制
                    for folders, subfolders, filenames in os.walk(self.sources_path):
                        subfolders[:] = [d for d in subfolders if os.path.join(folders, d) != self.destination_path] # 跳过遍历self.destination_path路径
                    
                        if any(name.strip() in os.path.basename(folders) for name in self.include_names): # 标记匹配的目录
                            sources_path_back = folders
                            destination_path_back = os.path.join(self.destination_path, os.path.relpath(folders, self.sources_path))
                            if not os.path.exists(destination_path_back):
                                start_time = time.time()
                                shutil.copytree(sources_path_back, destination_path_back) # 复制目录
                                end_time = time.time()
                                duration = end_time - start_time # 计算复制用时
                                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 目录复制: {os.path.basename(folders)}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 目录复制: {os.path.basename(folders)}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                self.retry_count = 0 # 重置尝试计数，下同

                        for filename in filenames:
                            if any(name.strip() in filename for name in self.include_names): # 标记匹配的文件
                                sources_path_back = os.path.join(folders, filename)
                                destination_path_back = os.path.join(self.destination_path, os.path.relpath(os.path.join(folders, filename), self.sources_path))
                                destination_dir = os.path.dirname(destination_path_back)
                                if not os.path.exists(destination_dir): # 如果没有目标目录，就进行创建
                                    os.makedirs(destination_dir)
                                if not os.path.exists(destination_path_back):
                                    start_time = time.time()
                                    shutil.copy(sources_path_back, destination_path_back) # 复制文件
                                    end_time = time.time()
                                    duration = end_time - start_time # 计算复制用时
                                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 文件复制: {filename}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 文件复制: {filename}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                    self.retry_count = 0
                if self.any == True: # 不经过字段匹配
                    for folders, subfolders, filenames in os.walk(self.sources_path):
                        subfolders[:] = [d for d in subfolders if os.path.join(folders, d) != self.destination_path]

                        for filename in filenames:
                            sources_path_back = os.path.join(folders, filename)
                            destination_path_back = os.path.join(self.destination_path, os.path.relpath(os.path.join(folders, filename), self.sources_path))
                            destination_dir = os.path.dirname(destination_path_back)
                            if not os.path.exists(destination_dir):
                                os.makedirs(destination_dir)
                            if not os.path.exists(destination_path_back):
                                start_time = time.time()
                                shutil.copy(sources_path_back, destination_path_back) # 复制文件
                                end_time = time.time()
                                duration = end_time - start_time
                                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 文件复制: {filename}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 文件复制: {filename}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                self.retry_count = 0
            self.retry_count = 0
        except Exception as e:
            self.retry_count += 1 # 尝试次数每次加1
            if self.retry_count > 3: # 尝试次数大于3时停止运行
                print("无法调用FilesCopy函数，停止运行")
                logging.info("无法调用FilesCopy函数，停止运行")
                exit()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}, 尝试重新调用FilesCopy函数，尝试次数: {self.retry_count}")
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}, 尝试重新调用FilesCopy函数，尝试次数: {self.retry_count}")
            self.FilesCopy()

    def run(self):
        while True:
            if self.use_schedule == False: # 不使用时间表
                self.FilesCopy()
            if self.use_schedule == True: # 使用时间表
                current_time = datetime.now().time() # 获取当前时间
                if self.start_time <= current_time <= self.end_time: # 判断当前时间是否在设定范围内
                    self.FilesCopy()

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, 'config.ini')

    log_path = os.path.join(script_dir, 'FilesSpy_log.txt')
    handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=7)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    if not os.path.exists(config_path): # 如果目录没有配置文件，就进行配置文件的创建
        config = configparser.ConfigParser()
        
        config['FilesSpyConfig'] = {
            'sources_path': '',
            'destination_path': '',
            'include_names': '',
            'any': 'False'
        }
        
        config['ScheduleConfig'] = {
            'use_schedule': 'False',
            'schedule_start_hour': '',
            'schedule_start_minute': '',
            'schedule_stop_hour': '',
            'schedule_stop_minute': ''
        }

        with open(config_path, 'w') as config_file: # 写入文件
            config_file.write('# sources_path: 资源目录\n# destination_path: 目标目录\n# include_names: 检测的字段，用逗号隔开多个字段\n# any: 是否直接复制资源目录下全部文件 (True/False)\n# use_schedule: 是否启用时间表 (True/False)\n# schedule_start_hour: 开始时间 (时)\n# schedule_start_minute: 开始时间 (分)\n# schedule_stop_hour: 结束时间 (时)\n# schedule_stop_minute: 开始时间 (分)\n\n')
            config.write(config_file)
            
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 配置文件已生成: {config_path}，请修改配置文件以运行FilesSpy")
        
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 配置文件已生成: {config_path}，请修改配置文件以运行FilesSpy")
            
        exit()

    try:
        main_task = FilesSpy()
        main_task.run() # 运行函数
    except Exception as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}")
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}")

