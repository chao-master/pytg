from PIL import Image
import requests

from objects import *
from bot import *
from adminableBot import *

class MyLittleFaceWhenBot(AdminableBot):
    def onCmd_find(self):
      self.sendMessage(msg.chat.id,"What do you want me to find for you? Give me a comma seperated list of tags.",
          replyingToId=msg.id,
      ).onReply(TagGetResponse())
      return True
    def onCmd_cancel(self):
      return "Im not doing anything for you right now."

class TagGetResponse(AwaitResponse):
    def __init__():
        super().__init__()
        self.tags = set()
        
    def onCmd_cancel(self,msg):
        return "Operation canceled"
    
    def onTextMessage(self,msg):
        for t in msg.split(","):
            t=t.strip()
            if t[0] == "-":
                self.tags.remove(t[1:])
            else
                self.tags.add(t)
        msg._bot.sendMessage(msg.chat.id,
    
    def makeResponseImage(self):
        data = requests.get("http://mylittlefacewhen.com/api/v2/face",{
            "limit":6,
            "order":"-id",
            "format":json,
            "search":list(self.tags)
        }).json()
        thumbs = []
        for i in data["objects"]:
            r = requests.get("http://mylittlefacewhen.com"+i["thumbs"]["jpg"])
            r.raw.decode_content = True
            thumbs.append(Image.open(r.raw))
        thumbs.sort(key=lambda i:return i.size[0])
        maxWidth = max([sum([i.size[0] for i in thumbs[j::3]]) for j in range(2)])
        thumb = Image.new("RGB",[maxWidth,300],(255,255,255))
        for r in range(2):
            x=0
            for c in range(3):
                thumb.paste(thumb[r*3+c],(x,r*100)
                x+=thumb[r*3+c].size[0]
        return thumb