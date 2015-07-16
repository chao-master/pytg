import logging
import traceback

from objects import *
from bot import *

class AdminableBot(Bot):
    def __init__(self,adminId,reportLevel=logging.ERROR,**kwargs):
        super().__init__(**kwargs)
        self.adminId = int(adminId)
        self.reporter = None
        if not adminId is None:
            self.reporter = ReportHandler(self,reportLevel)
            self.logger.addHandler(self.reporter)

    def checkSecureAdmin(self,msg):
        if msg.frm.id == self.adminId:
            if msg.chat.id == self.adminId:
                return True
            else:
                self.sendMessage(msg.chat.id,"Admin commands only valid in private chat. @{}".format(self.me.username),
                    replyingToId=msg.id
                )
        else:
            self.sendMessage(msg.chat.id,"You are not authorized to use admin controlls.", replyingToId=msg.id)
        return False


    def onCmd_adminhelp(self,msg):
        if not self.checkSecureAdmin(msg): return True
        self.sendMessage(msg.chat.id,"""Admin Commands:
    /adminLevel [logLevel {critical,error,warning,info,debug}] - gets/set reporting debug level""",replyingToId=msg.id)
        return True

    def onCmd_adminlevel(self,msg,level=None):
        if level is None:
            cLevel = self.reporter.level
            try:
                cLevel = ["notset","debug","info","warning","error","critical"][cLevel//10]
            except (TypeError,IndexError):
                pass
            self.sendMessage(msg.chat.id,"Reporting level is {}".format(cLevel),replyingToId=msg.id)
            return True
        
        if level.upper() in ["CRITICAL","ERROR","WARNING","INFO","DEBUG"]:
            self.reporter.setLevel(getattr(logging,level))
            self.sendMessage(msg.chat.id,"Level updated succesfully",replyingToId=msg.id)
        else:
            raise BadUserInputError("{} is not a valid option, valid options are: critical, error, warning, info and debug".format(level))
        return True


class ReportHandler(logging.Handler):
    def __init__(self,bot,level):
        super().__init__(level)
        self.bot = bot
    def emit(self,record):
        if record.exc_info:
            self.bot.sendMessage(self.bot.adminId,record.getMessage()+"\n"+traceback.format_exc(),True)
        else:
            self.bot.sendMessage(self.bot.adminId,record.getMessage())
