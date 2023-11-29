import os
import shutil
import configparser
import logging
from logging.handlers import TimedRotatingFileHandler
import time

class FilesSpy:
    def __init__(self, config_path='config.ini'):
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, config_path)
        config = configparser.ConfigParser()
        config.read(config_path)
        self.destination_path = config.get('FilesSpyConfig', 'destination_path')
        self.sources_path = config.get('FilesSpyConfig', 'sources_path')
        self.include_names = config.get('FilesSpyConfig', 'include_names').split(',')
        self.retry_count = 0

    def FilesCopy(self):
        try: 
            if os.path.exists(self.sources_path):
                for folders, subfolders, filenames in os.walk(self.sources_path, topdown=True):
                    subfolders[:] = [d for d in subfolders if os.path.join(folders, d) != self.destination_path]
                    for filename in filenames:
                        if any(name.strip() in filename for name in self.include_names):
                            sources_path_back = os.path.join(folders, filename)
                            destination_path_back = os.path.join(self.destination_path, os.path.relpath(os.path.join(folders, filename), self.sources_path))
                            destination_dir = os.path.dirname(destination_path_back)
                            if not os.path.exists(destination_dir):
                                os.makedirs(destination_dir)
                            if not os.path.exists(destination_path_back):
                                start_time = time.time()
                                shutil.copy(sources_path_back, destination_path_back)
                                end_time = time.time()
                                duration = end_time - start_time
                                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 文件复制: {filename}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
                                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 文件复制: {filename}, 从 {sources_path_back} 到 {destination_path_back}, 用时: {duration:.2f}秒")
            self.retry_count = 0    
        except Exception as e:
            self.retry_count += 1
            if self.retry_count > 3:
                print("无法调用FilesCopy函数，停止运行")
                logging.info("无法调用FilesCopy函数，停止运行")
                exit()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}, 尝试重新调用FilesCopy函数，尝试次数: {self.retry_count}")
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}, 尝试重新调用FilesCopy函数，尝试次数: {self.retry_count}")
            self.FilesCopy()

    def run(self):
        while True:
            self.FilesCopy()

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, 'config.ini')

    log_path = os.path.join(script_dir, 'FilesSpy_log.txt')
    handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=7)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    if not os.path.exists(config_path):
        config = configparser.ConfigParser()
        
        config['FilesSpyConfig'] = {
            'sources_path': '',
            'destination_path': '',
            'include_names': ''
        }

        with open(config_path, 'w') as config_file:
            config.write(config_file)
            
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 配置文件已生成: {config_path}，请修改配置文件以运行FilesSpy")
        
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 配置文件已生成: {config_path}，请修改配置文件以运行FilesSpy")
            
        exit()

    try:
        main_task = FilesSpy()
        main_task.run()
    except Exception as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}")
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 错误: {e}")
