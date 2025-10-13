import requests
from datetime import datetime, date
from time import sleep
import json

"""

Generates the theoric_gap_b1.json and theoric_gap_21jet.json

"""

line_b1 = "RTM:LNE:139"
line_21jet = "RTM:LNE:140"

choosen_date = "2025-10-13" 

def ToDateTime(hms: str) -> datetime:
    fmt = "%H:%M:%S"
    t = datetime.strptime(hms, fmt).time()
    return datetime.combine(date(2025, 1, 2), t)

def get_api_url(line, station, date) :
    return f"https://api.rtm.fr//front/getTheoricalTime?lineRef={line}&direction=1&pointRef={station}&date={date}"


def get_all_schedules(url) :
    result = []
    req = requests.get(url)
    if req.status_code == 200 :
        data = req.json()
        data = data["data"]
        for d in data :
            str_t = d["DepartureTime"][:-6]
            result.append(ToDateTime(str_t).timestamp())
    else :
        print("ERROR !!! for url : ", url)

    return result

b1_all_schedules = []
_21jet_all_schedules = []

with open("../datas/stations.txt", "r") as f :
    lines = f.readlines()
    if not any("RTM:PNT:00001747" in l for l in lines):
        lines.insert(0, "MRPDP|RTM:PNT:00001747|2")
    for station_line in lines :
        _, pnt_ref, which_one = tuple(station_line.strip().split("|"))

        url = get_api_url(line_b1, pnt_ref, choosen_date)
        schedules = get_all_schedules(url)
        b1_all_schedules.append(schedules)
        print("[B1]", url)
        sleep(1)

        if which_one == "2" :
            url = get_api_url(line_21jet, pnt_ref, choosen_date)
            schedules = get_all_schedules(url)
            _21jet_all_schedules.append(schedules)
            print("[21jet]", url)
            sleep(1)

dic_b1 = {}
dic_21jet = {}
        
for i_0 in range(len(b1_all_schedules) - 1) :
    i_1 = i_0 + 1
    gaps = []
    b0 = b1_all_schedules[i_0]
    b1 = b1_all_schedules[i_1]
    for i in range (len(b0)) :
        gaps.append(b1[i] - b0[i])

    value_avg, value_max = sum(gaps) / len(gaps), max(gaps)
    dic_b1[str(i_0)] = { "average" : value_avg, "max" : value_max }

for i_0 in range(len(_21jet_all_schedules) - 1) :
    i_1 = i_0 + 1
    gaps = []
    b0 = _21jet_all_schedules[i_0]
    b1 = _21jet_all_schedules[i_1]
    for i in range (len(b0)) :
        gaps.append(b1[i] - b0[i])

    value_avg, value_max = sum(gaps) / len(gaps), max(gaps)
    dic_21jet[str(i_0)] = { "average" : value_avg, "max" : value_max }
    
with open("../datas/seeking_head/theoric_gap_b1.json", "w") as f:
    f.write(json.dumps(dic_b1))

with open("../datas/seeking_head/theoric_gap_21jet.json", "w") as f:
    f.write(json.dumps(dic_21jet))