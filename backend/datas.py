import requests
import time as tme
from datetime import datetime, time

API_URL                 = "https://api.rtm.fr/front/"
PNT_ROND_POINT_DU_PRADO = "RTM:PNT:00001747"
LINE_21JET              = "RTM:LNE:140"
LINE_B1                 = "RTM:LNE:139"
DIR_RPDP_TO_LUMINY_21JET= "1"
DIR_RPDP_TO_LUMINY_B1   = "1"

class DatasAPI :
    @staticmethod
    def WakeUpDay():
        now = datetime.now()
        date_5h = datetime.combine(now.date(), time(5, 0, 0))
        timestamp_5h = date_5h.timestamp()
        return timestamp_5h
    def RealtimeLinePointUrl(line, point, direction) :
        return API_URL + f"getReelTime?lineRef={line}&direction={direction}&pointRef={point}"
    def TheoricLinePointUrl(line, point, direction, date) :
        return API_URL + f"getReelTime?lineRef={line}&direction={direction}&pointRef={point}&date={date}"


class Data :
    def __init__(self, url, time_update = 60, daily = False) :
        self.url = url
        self.time_update = time_update
        self.last_time = 0
        self.data = {}
        self.daily = daily
    def Get(self, path: str = "", force_update: bool = False) :
        now = tme.time()
        if force_update or (now - self.last_time > self.time_update) :
            self.Update()
        value = self.data
        if path :
            for key in path.split("/"):
                if isinstance(value, list):
                    try:
                        index = int(key)
                        value = value[index]
                    except (ValueError, IndexError):
                        return None
                elif isinstance(value, dict):
                    if key in value:
                        value = value[key]
                    else:
                        return None
                else:
                    return None
        return value
    def Update(self) :
        req = requests.get(self.url)
        if (req.status_code == 200) :
            data = req.json()
            self.data = data["data"]
        self.last_time = DatasAPI.WakeUpDay() if self.daily else tme.time()
    def Url(self) :
        return self.url