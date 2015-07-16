import datetime
import hashlib
import math

from objects import *
from bot import *

class GeoHashBot(Bot):
    def onGenericCommand(self,commandName,args):
        print("command:",commandName,args)
    def onGenericMessage(self,msg):
        print("message:",msg)
    def onLocationMessage(self,msg):
        day = datetime.date.today()
        lng,lat = msg.location.longitude,msg.location.latitude
        if lng >= -30: #30 WEST RULE
            day -= datetime.timedelta(1)
        r=requests.get("http://geo.crox.net/djia/{day.year}/{day.month}/{day.day}".format(day=day))
        dateDjia = datetime.date.today().strftime("%Y-%m-%d-").encode("ascii")+r.content
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

        Location(_bot=self,latitude=nLat,longitude=nLng).sendTo(msg.chat.id,msg.id)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("token",help="The Telegram bot's access token")
    parser.add_argument("-v","--verbose",help="Enable verbose bot output",action="store_true")
    args = parser.parse_args()

    GeoHashBot(args.token,verbose=args.verbose).handleMessages()
