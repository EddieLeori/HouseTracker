from lib.utility import *
# from tornado.web import Application
# from tornado import ioloop
from tornado.ioloop import IOLoop
from src.worker import Worker


class TrackerServer:
    def __init__(self):
        self.Init()

    def Start(self):
        Log("TrackerServer start method is called.")

        # todo: start all worker
        work = Worker()
        work.Start()

        IOLoop.current().start()

    def Init(self):
        Log("TrackerServer init")

        # todo: load setting
        # 1. system setting
        # 2. all member info
        # 3. all web's setting

