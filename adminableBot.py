import logging
import traceback

from objects import *
from bot import *

class AdminableBot(Bot):
    def __init__(self,adminId,reportLevel=logging.ERROR,**kwargs):
        super().__init__(**kwargs)
        print("Admin's bot set to: {}".format(adminId))
        self.adminId = int(adminId)
        self.reporter = None
        if not adminId is None:
            self.reporter = ReportHandler(self,reportLevel)
            self.logger.addHandler(self.reporter)

    def isSecureAdmin(self,msg):
        if msg.frm.id == self.adminId:
            if msg.chat.id == self.adminId:
                return True
            else:
                return "Admin commands only valid in private chat. @{}".format(self.me.username)
        else:
            return "You are not authorized to use admin controlls."


    def onCmd_adminhelp(self,msg):
        secure = self.isSecureAdmin(msg)
        if not secure is True: return secure
        return """Admin Commands:
    /adminLevel [logLevel {critical,error,warning,info,debug}] - gets/set reporting debug level
    /adminMemory - Prints debug infomation about the bot's memory"""

    def onCmd_adminlevel(self,msg,level=None):
        secure = self.isSecureAdmin(msg)
        if not secure is True: return secure

        if level is None:
            cLevel = self.reporter.level
            try:
                cLevel = ["notset","debug","info","warning","error","critical"][cLevel//10]
            except (TypeError,IndexError):
                pass
            return "Reporting level is {}".format(cLevel)
        try:
            self.reporter.setLevel(level.upper())
            return "Level updated succesfully"
        except ValueError:
            raise BadUserInputError("{} is not a valid option, valid options are: critical, error, warning, info and debug".format(level))
        return True

    def onCmd_adminmemory(self,msg):
        secure = self.isSecureAdmin(msg)
        if not secure is True: return secure

        return "Bot {}.{} has {} messages in storage awaiting a reply".format(
            self.__class__.__name__,
            hex(id(self))[2:],
            len(self.awaitingResponses)
        )



class ReportHandler(logging.Handler):
    def __init__(self,bot,level):
        super().__init__(level)
        self.bot = bot
    def emit(self,record):
        if record.exc_info:
            self.bot.sendMessage(self.bot.adminId,record.getMessage()+"\n"+traceback.format_exc(),True)
        else:
            self.bot.sendMessage(self.bot.adminId,record.getMessage())
