import json
import functools

class TGobj():
    mapping = {}
    supMapping = {}

    @classmethod
    def fromJson(cls,bot,string):
        def oh(obj):
            return cls(_bot=bot,**obj)
        return json.loads(string,object_hook=oh)

    def __new__(cls,_bot,**kwargs):
        def check(sCls):
            for ssCls in sCls.__subclasses__():
                r = check(ssCls)
                if r: return r
            if sCls.mapping:
                for jAttr,(attr,req,default) in sCls.mapping.items():
                    if (not jAttr in kwargs) and req:
                        return None
                return super(TGobj,cls).__new__(sCls)
        r = check(cls)
        if r:
            return r
        else:
            return kwargs

    def __init__(self,_bot,**kwargs):
        self._bot = _bot
        def add(jAttr,attr,req,default):
            if attr is None:
                return
            try:
                setattr(self,attr,kwargs[jAttr])
            except KeyError as e:
                if req:
                    raise e
                else:
                    setattr(self,attr,default)
        for jAttr,(attr,req,default) in self.mapping.items():
            add(jAttr,attr,req,default)
        for jAttr,(attr,req,default) in self.supMapping.items():
            add(jAttr,attr,req,default)

    def __eq__(self,other):
        return self.toDict() == other.toDict()
    def __ne__(self,other):
        return self.toDict() != other.toDict()

    def __hash__(self):
        return hash(self.toDict(True))

    def __repr__(self):
        return repr(self.toDict())

    def toDict(self,deep=False):
        r={}
        def add(jAttr,attr,req,default):
            if req:
                a = getattr(self,attr)
            else:
                a = getattr(self,attr,default)
            if deep and isinstance(a,TGobj):
                a = a.toDict(self,True)
            r[jAttr] = a
        for jAttr,(attr,req,default) in self.mapping.items():
            add(jAttr,attr,req,default)
        for jAttr,(attr,req,default) in self.supMapping.items():
            add(jAttr,attr,req,default)
        return r

class User(TGobj):
    mapping = {
        "id":("id",True,0),
        "first_name":("firstName",True,0),
        "last_name":("lastName",False,""),
        "username":("username",False,"")
    }

class GroupChat(TGobj):
    mapping = {
        "id":("id",True,0),
        "title":("title",True,0)
    }

class Contact(TGobj):
    mapping = {
        "phone_number":("number",True,0),
        "first_name":("firstName",True,0),
        "last_name":("lastName",False,""),
        "user_id":("id",False,None)
    }

class PhotoSize(TGobj):
    mapping = {
        "file_id":("id",True,0),
        "width":("width",True,0),
        "height":("height",True,0),
        "file_size":("size",False,None)
    }
    def sendTo(self,chatId,caption=None,replyingToId=None,replyMarkup=None):
        return self._bot.fireRequest("sendPhoto",{
            "chat_id":chatId,
            "photo":self.id,
            "caption":caption,
            "reply_to_message_id":replyingToId,
            "reply_markup":replyMarkup
        })["result"]

class Audio(TGobj):
    mapping = {
        "file_id":("id",True,0),
        "duration":("duration",True,0),
        "mime_type":("mime",False,None),
        "file_size":("size",False,None)
    }
    def sendTo(self,chatId,replyingToId=None,replyMarkup=None):
        return self._bot.fireRequest("sendAudio",{
            "chat_id":chatId,
            "audio":self.id,
            "reply_to_message_id":replyingToId,
            "reply_markup":replyMarkup
        })["result"]

class Sticker(TGobj):
    mapping = {
        "file_id":("id",True,0),
        "width":("width",True,0),
        "height":("height",True,0),
        "thumb":("thumb",True,0),
        "file_size":("size",False,None)
    }
    def sendTo(self,chatId,replyingToId=None,replyMarkup=None):
        return self._bot.fireRequest("sendSticker",{
            "chat_id":chatId,
            "sticker":self.id,
            "reply_to_message_id":replyingToId,
            "reply_markup":replyMarkup
        })["result"]


class Video(TGobj):
    mapping = {
        "file_id":("id",True,0),
        "width":("width",True,0),
        "height":("height",True,0),
        "duration":("duration",True,0),
        "thumb":("thumb",True,0),
        "mime_type":("mime",False,None),
        "file_size":("size",False,None),
        "caption":("caption",False,"")
    }
    def sendTo(self,chatId,replyingToId=None,replyMarkup=None):
        return self._bot.fireRequest("sendVideo",{
            "chat_id":chatId,
            "video":self.id,
            "reply_to_message_id":replyingToId,
            "reply_markup":replyMarkup
        })["result"]

class Location(TGobj):
    mapping = {
        "longitude":("longitude",True,0),
        "latitude":("latitude",True,0)
    }
    def sendTo(self,chatId,replyingToId=None,replyMarkup=None):
        return self._bot.fireRequest("sendLocation",{
            "chat_id":chatId,
            "latitude":self.latitude,
            "longitude":self.longitude,
            "reply_to_message_id":replyingToId,
            "reply_markup":replyMarkup
        })["result"]

class UserProfilePhotos(TGobj):
    mapping = {
        "total_count":("count",True,0),
        "photos":("photos",True,0)
    }

class ReplyKeyboardMarkup(TGobj):
    mapping = {
        "keyboard":("keyboard",True,0),
        "resize_keyboard":("resize",False,False),
        "one_time_keyboard":("oneTime",False,False),
        "selective":("selective",False,False)
    }

class ReplyKeybaordHide(TGobj):
    mapping = {
        "hide_keyboard":("hide",True,True),
        "selective":("selective",False,False)
    }

class ForceReply(TGobj):
    mapping = {
        "force_reply":("force",True,True),
        "selective":("selective",False,False)
    }

#Messages
class Message(TGobj):
    supMapping = {
        "message_id":("id",True,0),
        "from":("frm",True,0),
        "date":("timestamp",True,0),
        "chat":("chat",True,0),
        "forward_from":("forwardFrom",False,None),
        "forward_date":("forwardDate",False,None),
        "reply_to_message":("replyTo",False,None)
    }
    def onReply(self,responseHandler):
        self._bot.awaitingResponses[self.id] = responseHandler
    def __str__(self):
        try:
            return self.text
        except AttributeError:
            return "[{}]".format(self.__class__.__name__)

class TextMessage(Message):
    mapping = {
        "text":("text",True,0)
    }

class AudioMessage(Message):
    mapping = {
        "audio":("audio",True,0)
    }

class DocumentMessage(Message):
    mapping = {
        "document":("document",True,0)
    }

class PhotoMessage(Message):
    mapping = {
        "photo":("photo",True,0)
    }

class StickerMessage(Message):
    mapping = {
        "sticker":("sticker",True,0)
    }

class VideoMessage(Message):
    mapping = {
        "video":("video",True,0)
    }

class ContactMessage(Message):
    mapping = {
        "contact":("contact",True,0)
    }

class LocationMessage(Message):
    mapping = {
        "location":("location",True,0)
    }

class JoinMessage(Message):
    mapping = {
        "new_chat_participant":("join",True,0)
    }

class PartMessage(Message):
    mapping = {
        "left_chat_participant":("part",True,0)
    }

class TitleMessage(Message):
    mapping = {
        "new_chat_title":("title",True,0)
    }

class IconMessage(Message):
    mapping = {
        "new_chat_photo":("icon",True,0)
    }

class IconBlankMessage(Message):
    mapping = {
        "delete_chat_photo":(None,True,0)
    }

class GroupCreatedMessage(Message):
    mapping = {
        "group_chat_created":(None,True,0)
    }
