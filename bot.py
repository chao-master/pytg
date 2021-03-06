from objects import *
import requests
import re
import inspect
import traceback
import time
import logging

class Bot():
    def __init__(self,token,verbose=False):
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__+"."+hex(id(self))[2:])
        self.logger.addHandler(logging.StreamHandler())
        self.awaitingResponses = {}
        self.verbose = verbose
        self.me = self.fireRequest("getMe")["result"]
        print("Bot booted up succesfully, bot's username is",self.me.username)

    def parseJson(self,string):
        return TGobj.fromJson(self,string)

    def fireRequest(self,endpoint,payload={}):
        r=requests.get("https://api.telegram.org/bot{}/{}".format(self.token,endpoint),payload)
        if self.verbose: print(r.text)
        return self.parseJson(r.text)

    def clearAwaiting(self):
        now = time.time()
        self.awaitingResponses = {k:v for k,v in self.awaitingResponses.items() if v.diesAt>now}

    def pendingMessages(self):
        buffer = []
        lastUpdate = None
        while 1:
            if not buffer:
                d = self.fireRequest("getUpdates",{"timeout":60,"offset":lastUpdate})
                if d["ok"]:
                    buffer = d["result"]
                self.clearAwaiting()
            if buffer:
                lastUpdate = buffer[0]["update_id"]+1
                yield buffer.pop(0)["message"]

    def handleMessages(self):
        def maybeReply(reply):
            if reply is True: return True
            if reply is False or reply is None: return False
            try:
                reply.sendTo(msg.chat.id,replyingToId=msg.id)
            except AttributeError:
                self.sendMessage(msg.chat.id,str(reply),replyingToId=msg.id)
            return True

        for msg in self.pendingMessages():
            try:
                #First see if the message is a response to one we send earlier
                if not msg.replyTo is None:
                    handler = self.awaitingResponses.get(msg.replyTo.id,None)
                    if handler is not None:
                        if maybeReply(getattr(handler,"on"+msg.__class__.__name__,handler.onGenericMessage)(msg)):
                                del self.awaitingResponses[msg.replyTo.id]
                                continue
                #Then if it's a textMessage check the command handling system
                if isinstance(msg,TextMessage):
                    if maybeReply(self.checkCommands(msg)):
                        continue
                #Finally if none of that worked call the handler for this message type
                maybeReply(getattr(self,"on"+msg.__class__.__name__,self.onGenericMessage)(msg))
            except BadUserInputError as e:
                self.logger.debug("Error on message {}:{}".format(msg,e))
                self.sendMessage(msg.chat.id,"Error on message {}:{}".format(msg,e),replyingToId=msg.id)
            except Exception as e:
                self.logger.exception("Unknown Error handling message {}:{}".format(msg,e))
                self.sendMessage(msg.chat.id,"Unknown Error handling message {}".format(msg),replyingToId=msg.id)

    def checkCommands(self,msg):
        if not msg.text.startswith("/"):
            return False
        command,_,args = msg.text[1:].partition(" ")
        commandName,named,botName = command.partition("@")
        if named and botName != self.me.username:
            return False
        commandName = commandName.lower()
        def callGeneric(msg):
            if self.verbose: print("message hadled by generic command handler")
            self.onGenericCommand(msg,commandName,args)
        cmdFunc = getattr(self,"onCmd_"+commandName,callGeneric)
        nArgs = len(inspect.getargspec(cmdFunc).args)

        if nArgs>2 and args:
            return cmdFunc(msg,*args.split(" ",nArgs-2))
        else:
            return cmdFunc(msg)

    def sendMessage(self,chatId,message,disableWebPreview=False,replyingToId=None,replyMarkup=None):
        return self.fireRequest("sendMessage",{
            "chat_id":chatId,
            "text":message,
            "disable_web_page_preview":disableWebPreview,
            "reply_to_message_id":replyingToId,
            "reply_markup":replyMarkup
        })["result"]

    def onGenericCommand(self,msg,commandName,args):
        return False
    def onTextMessage(self,msg): pass
    def onAudioMessage(self,msg): pass
    def onDocumentMessage(self,msg): pass
    def onPhotoMessage(self,msg): pass
    def onStickerMessage(self,msg): pass
    def onVideoMessage(self,msg): pass
    def onContactMessage(self,msg): pass
    def onLocationMessage(self,msg): pass
    def onJoinMessage(self,msg): pass
    def onPartMessage(self,msg): pass
    def onTitleMessage(self,msg): pass
    def onIconMessage(self,msg): pass
    def onIconBlankMessage(self,msg): pass
    def onGroupCreatedMessage(self,msg): pass
    def onGenericMessage(self,msg): pass

class BadUserInputError(Exception):
    pass

class AwaitResponse():
    def __init__(self):
        self.diesAt = time.time()+60*60
    def onTextMessage(self,msg):
        return False
    def onAudioMessage(self,msg):
        return False
    def onDocumentMessage(self,msg):
        return False
    def onPhotoMessage(self,msg):
        return False
    def onStickerMessage(self,msg):
        return False
    def onVideoMessage(self,msg):
        return False
    def onContactMessage(self,msg):
        return False
    def onLocationMessage(self,msg):
        return False
    def onJoinMessage(self,msg):
        return False
    def onPartMessage(self,msg):
        return False
    def onTitleMessage(self,msg):
        return False
    def onIconMessage(self,msg):
        return False
    def onIconBlankMessage(self,msg):
        return False
    def onGroupCreatedMessage(self,msg):
        return False
    def onGenericMessage(self,msg):
        return False
