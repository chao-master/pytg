from objects import *
import requests
import re
import inspect
import traceback

class Bot():
    def __init__(self,token,verbose=False):
        self.token = token
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

    def pendingMessages(self):
        buffer = []
        lastUpdate = None
        while 1:
            if not buffer:
                d = self.fireRequest("getUpdates",{"timeout":60,"offset":lastUpdate})
                if d["ok"]:
                    buffer = d["result"]
            if buffer:
                lastUpdate = buffer[0]["update_id"]+1
                yield buffer.pop(0)["message"]

    def handleMessages(self):
        for msg in self.pendingMessages():
            try:
                if msg.replyTo is not None:
                    handler = self.awaitingResponses.get(msg.replyTo.id,None)
                    if handler is not None:
                        if self.verbose: print("message is response to earlier messge ",msg.replyTo.id)
                        if getattr(handler,"on"+msg.__class__.__name__,handler.onGenericMessage)(msg):
                            if self.verbose: print("message hadled by reply handler")
                            del self.awaitingResponses[msg.replyTo.id]
                            continue
                if isinstance(msg,TextMessage):
                    if self.checkCommands(msg):
                        continue
                getattr(self,"on"+msg.__class__.__name__,self.onGenericMessage)(msg)
            except BadUserInputError as e:
                self.sendMessage(msg.chat.id,"Error on message {}:{}".format(msg,e),replyingToId=msg.id)
            except Exception as e:
                traceback.print_exc()
                self.sendMessage(msg.chat.id,"Unknown Error handling message {}".format(msg),replyingToId=msg.id)

    def checkCommands(self,msg):
        if not msg.text.startswith("/"):
            return False
        command,_,args = msg.text[1:].partition(" ")
        commandName,named,botName = command.partition("@")
        if named and botName != self.me.username:
            return False
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
