#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/14 17:17
# @Author  : 兵
# @email    : 1747193328@qq.com
import os
import subprocess
import sys
import traceback

import requests
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication
from qfluentwidgets import MessageBox

import utils
from core import MessageManager
from version import RELEASES_URL, RELEASES_API_URL, __version__


@utils.loghandle
class UpdateWoker( QObject):
    version=Signal(dict)
    download_success=Signal( )
    def __init__(self,parent):
        self._parent=parent
        super().__init__(parent)

        self.func=self._check_update
        self.version.connect(self._check_update_call_back)
        self.download_success.connect(self._call_restart)
        self.update_thread=utils.LoadingThread(self._parent,show_tip=False)
        self.down_thread=utils.LoadingThread(self._parent,show_tip=True,title="下载中")

    def download(self,url):
        # url="https://github.moeyy.xyz/"+url
        resp = requests.get(url, stream=True)
        # content_size = int(resp.headers['content-length'])

        count = 0

        with open("update.zip", "wb") as f:
            for i in resp.iter_content(1024):
                if i:
                    f.write(i)
                    count += len(i)

        self.download_success.emit()

    def _call_restart(self):

        box = MessageBox("重启询问？"  ,
                         "更新包下载完成！是否现在重启？\n如果取消，将下次打开软件的时候自动更新！",
                         self._parent
                         )
        box.yesButton.setText("更新")
        box.cancelButton.setText("取消")

        box.exec_()
        if box.result() == 0:
            return
        utils.unzip()





    def _check_update(self):
        MessageManager.send_info_message("检查更新中...")


        try:
            headers={
                "User-Agent": "Awesome-Octocat-App"
            }
            version_info = requests.get(RELEASES_API_URL,headers=headers).json()
            print(version_info)


            self.version.emit(version_info)

        except:
            self.logger.error(traceback.format_exc())
            MessageManager.send_error_message("网络异常！")



    def _check_update_call_back(self,version_info):


        if "message" in version_info:
            MessageManager.send_warning_message(version_info['message'])
            return
        if version_info['tag_name'][1:] == __version__:
            MessageManager.send_success_message("当前版本已经是最新版了！")

            return
        box = MessageBox("检测到新版本：" + version_info["name"] + version_info["tag_name"],
                         version_info["body"],
                         self._parent
                         )
        box.yesButton.setText("更新")
        box.cancelButton.setText("取消")

        box.exec_()
        if box.result() == 0:
            return

        for assets in version_info["assets"]:

            if sys.platform in assets["name"] and "NepTrainKit" in assets["name"]:

                self.down_thread.start_work(self.download,assets["browser_download_url"])
                return
        MessageManager.send_warning_message("没有匹配到适合当前系统的更新包，请手动下载！")



    def check_update(self):
        self.update_thread.start_work(self._check_update)

