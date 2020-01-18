"""
负责提供具体能满足哪些请求
"""
from views import *

urls = [
    ('/time',get_time),
    ('/hello',hello),
    ('/bye',bye)
]