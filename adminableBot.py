import logging
import traceback

from objects import *
from bot import *

class AdminableBot(Bot):
    def __init__(self,adminId,reportLevel=logging.ERROR,**kwargs):
        super().__init__(**kwargs)
        self.adminId = adminId
        self.reporter = None
        if not adminId is None:
            self.reporter = ReportHandler(self,reportLevel)
            self.logger.addHandler(self.reporter)

class ReportHandler(logging.Handler):
    def __init__(self,bot,level):
        super().__init__(level)
        self.bot = bot
    def emit(self,record):
        if record.exc_info:
            self.bot.sendMessage(self.bot.adminId,record.getMessage()+"\n"+traceback.format_exc(),True)
        else:
            self.bot.sendMessage(self.bot.adminId,record.getMessage())
