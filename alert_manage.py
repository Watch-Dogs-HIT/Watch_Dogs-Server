#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
邮件告警功能管理
"""

from Data.alert_monitor import AlertMonitor

if __name__ == '__main__':
    AlertMonitor().alert_monitor_thread()
