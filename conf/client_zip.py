#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程客户端更新及压缩包制作
"""

import os
import tarfile
import zipfile
import requests

from setting import Setting

setting = Setting()
zip_log = setting.logger


def download_client_zip_from_github():
    """从github下载最新客户端压缩包"""
    try:
        github_files = requests.get(setting.CLIENT_DOWNLOAD_LINK)
        with open(setting.CLIENT_FILE_ZIP, "wb") as zip_file:
            zip_file.write(github_files.content)
        zip_log.info("客户端压缩包更新成功 - " + str(setting.CLIENT_FILE_ZIP))
        return "OK"
    except Exception as err:
        if os.path.exists(setting.CLIENT_FILE_ZIP):
            os.remove(setting.CLIENT_FILE_ZIP)
        zip_log.error("下载客户端压缩包出错 : " + str(err))
        return None


def zip2tar(zip_file_path, tar_file_path):
    """zip转tar文件"""
    # reference : https://blog.csdn.net/xiaodongxiexie/article/details/71483693
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            with tarfile.open(tar_file_path, 'w') as tar_file:
                for files in zip_file.namelist():
                    if not os.path.isdir(files):
                        zip_file.extract(files)
                        tar_file.add(files, arcname=files)
        zip_log.info("客户端targz压缩包更新成功 - " + str(setting.CLIENT_FILE_TAR))
    except Exception as err:
        if os.path.exists(os.path.join(setting.CONF_PATH, setting.CLIENT_FILE_TAR)):
            os.remove(os.path.join(setting.CONF_PATH, setting.CLIENT_FILE_TAR))
        zip_log.error("制作targz客户端压缩包出错 : " + str(err))


def make_latest_client_tar_file():
    """制作最新版本的远程客户端压缩包, 并保存在配置文件目录下"""
    if download_client_zip_from_github():
        zip2tar(os.path.join(setting.CONF_PATH, setting.CLIENT_FILE_ZIP),
                os.path.join(setting.CONF_PATH, setting.CLIENT_FILE_TAR))


if __name__ == '__main__':
    make_latest_client_tar_file()
