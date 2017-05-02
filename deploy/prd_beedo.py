# coding=utf-8
from __future__ import absolute_import
import multiprocessing

bind = '127.0.0.1:6002'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
pidfile = 'logs/pid.pid'
