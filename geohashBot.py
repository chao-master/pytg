import datetime
import hashlib
import math

from objects import *
from bot import *
from adminableBot import *

class GeoHashBot(AdminableBot):
    def onLocationMessage(self,msg):
        day = datetime.date.today()
        lng,lat = msg.location.longitude,msg.location.latitude
        return self.caculateGeoHash(lat,lng,day)

    def caculateGeoHash(self,lat,lng,day,scale=1):
        if lng >= -30: #30 WEST RULE
            dday = day - datetime.timedelta(1)
        else:
            dday = day
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

    def onCmd_hash(self,msg,day=None,gratical=None):
        if day is None:
            day = datetime.date.today()
        else:
            try:
                day = datetime.datetime.strptime(day,"%Y-%m-%d")
            except ValueError:
                if gratical is None:
                    gratical,day = day,datetime.date.today()
                else:
                    raise BadUserInputError("Day must be in YYYY-MM-DD format")
        if gratical is None:
            #Here we must manually send the message so we can onReply it
            self.sendMessage(msg.chat.id,"Ok where are you at?",
                replyingToId=msg.id,
                replyMarkup={"force_reply":True,"selective":True}
            ).onReply(GeoLocationResponse(day))
            return True
        else:
            try:
                lat,lng = gratical.split(",",2)
                if lat == "-0":lat=-0.01
                if lng == "-0":lng=-0.01
                lat,lng = float(lat),float(lng)
            except (ValueError,TypeError) as e:
                raise BadUserInputError("Gartical must be in format Lat,Lng With both numbers as decimals")
            return self.caculateGeoHash(lat,lng,day)

class GeoLocationResponse(AwaitResponse):
    def __init__(self,day):
        super().__init__()
        self.day = day
    def onLocationMessage(self,msg):
        lng,lat = msg.location.longitude,msg.location.latitude
        return msg._bot.caculateGeoHash(lat,lng,self.day)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("token",help="The Telegram bot's access token")
    parser.add_argument("-v","--verbose",help="Enable verbose bot output",action="store_true")
    parser.add_argument("-a","--adminId",help="Admin's telegram id for debugging")
    parser.add_argument("-r","--reportLevel",help="Level of logging to report to the admin via telegram, default: error",
        choices=["critical","error","warning","info","debug"],default="error"
    )
    args = parser.parse_args()

    bot=GeoHashBot(token=args.token,verbose=args.verbose,adminId=args.adminId,reportLevel=args.reportLevel.upper())
    try:
        bot.handleMessages()
    except Exception as e:
        bot.logger.critical("Critical Error, the bot has gone down.",exc_info=true)
