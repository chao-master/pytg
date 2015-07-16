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

    def checkSecureAdmin(self,msg):
        if msg.frm.id == adminId:
            if msg.chat.id == adminId:
                return True
            else:
                self.sendMessage(msg.chat.id,"Admin commands only valid in private chat. @{}".format(self.me.username),
                    replyingToId=msg.id
                )
        else:
            self.sendMessage(msg.chat.id,"You are not authorized to use admin controlls.", replyingToId=msg.id)
        return False


    def onCmd_adminhelp(self,msg):
        if not self.checkSecureAdmin(msg): return
        self.sendMessage(msg.chat.id,"Admin Commands: (None)",replyingToId=msg.id)

class ReportHandler(logging.Handler):
    def __init__(self,bot,level):
        super().__init__(level)
        self.bot = bot
    def emit(self,record):
        if record.exc_info:
            self.bot.sendMessage(self.bot.adminId,record.getMessage()+"\n"+traceback.format_exc(),True)
        else:
            self.bot.sendMessage(self.bot.adminId,record.getMessage())
