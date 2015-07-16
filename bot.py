from objects import *
import requests
import re
import inspect

class Bot():
    def __init__(self,token,verbose=False):
        self.token = token
        self.awaitingResponses = {}
        self.verbose = verbose
        self.me = self.fireRequest("getMe")

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
            if msg.replyTo is not None:
                handler = self.awaitingResponses.get(msg.replyTo.id,None)
                if handler is not None:
                    if getattr(handler,"on"+msg.__class__.__name__,handler.onGenericMessage)(msg):
                        del self.awaitingResponses[msg.replyTo.id]
                        continue
            if isinstance(msg,TextMessage):
                if self.checkCommands(msg):
                    continue
            getattr(self,"on"+msg.__class__.__name__,self.onGenericMessage)(msg)

    def checkCommands(self,msg):
        if not msg.text.startswith("/"):
            return False
        command,_,args = msg.text[1:].partition(" ")
        commandName,named,botName = command.partition("@")
        if named and botName != self.me.username:
            return False
        def callGeneric():
            self.onGenericCommand(commandName,args)
        cmdFunc = getattr(self,"onCmd_"+commandName,callGeneric)
        nArgs = len(inspect.getargspec(cmdFunc).args)
        if nArgs:
            return cmdFunc(*args.split(" ",nArgs-1))
        else:
            return cmdFunc()

    def onGenericCommand(self,commandName,args):
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

class AwaitResponse():
    def __init__(self,id,bot):
        self.bot = bot
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
