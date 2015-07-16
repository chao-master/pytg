import datetime
import hashlib
import math

from objects import *
from bot import *

class GeoHashBot(Bot):
    def onLocationMessage(self,msg):
        day = datetime.date.today()
        lng,lat = msg.location.longitude,msg.location.latitude
        self.caculateGeoHash(lat,lng,day).sendTo(msg.chat.id,msg.id)

    def caculateGeoHash(self,lat,lng,day):
        if lng >= -30: #30 WEST RULE
            dday = day - datetime.timedelta(1)
        else:
            ddat = day
        r=requests.get("http://geo.crox.net/djia/{day.year}/{day.month}/{day.day}".format(day=dday))
        dateDjia = day.strftime("%Y-%m-%d-").encode("ascii")+r.content
        djiaHash = hashlib.md5(dateDjia).hexdigest()

        fLat = int(djiaHash[:16],16)/(1<<16*4)
        fLng = int(djiaHash[16:],16)/(1<<16*4)

        aLat = math.floor(abs(lat))+fLat
        aLng = math.floor(abs(lng))+fLng

        nLat = math.copysign(aLat,lat)
        nLng = math.copysign(aLng,lng)

        if self.verbose:
            print ("Lats:",lat,fLat,aLat,nLat)
            print ("Longs:",lng,fLng,aLng,nLng)
            print ("Djia:",dateDjia,djiaHash)

        return Location(_bot=self,latitude=nLat,longitude=nLng)

    def onCmd_hash(self,msg,day=None):
        print (repr(day))
        replyHandler = GeoLocationResponse(day)
        self.sendMessage(msg.chat.id,"Ok where are you at?",
            replyingToId=msg.id,
            replyMarkup={"force_reply":True,"selective":True}
        ).onReply(replyHandler)

class GeoLocationResponse(AwaitResponse):
    def __init__(self,day):
        if day is None:
            self.day = datetime.date.today()
        else:
            try:
                self.day = datetime.datetime.strptime(day,"%Y-%m-%d")
            except ValueError:
                raise BadUserInputError("Day must be in YYYY-MM-DD format")

    def onLocationMessage(self,msg):
        lng,lat = msg.location.longitude,msg.location.latitude
        msg._bot.caculateGeoHash(lat,lng,self.day).sendTo(msg.chat.id,msg.id)
        return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("token",help="The Telegram bot's access token")
    parser.add_argument("-v","--verbose",help="Enable verbose bot output",action="store_true")
    args = parser.parse_args()

    GeoHashBot(args.token,verbose=args.verbose).handleMessages()
