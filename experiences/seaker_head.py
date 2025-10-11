from datetime import datetime as dt, time, timedelta
from matplotlib.pylab import *
import requests
import json

"""
Here, we are trying to search the variation max_delta_t which
define the maximum amount of difference between two consecutives
schedule cf. schedule(i + 1) + max_delta_t = schedule(i)
"""

SECONDS_ONE_DAY         = 60 * 60 * 24

def today() :
    return dt.strftime(dt.now(), "%Y-%m-%d")

def yesterday():
    return (dt.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def ToDateTime(hms: str) -> datetime :
    fmt = "%H:%M:%S"
    dt = datetime.datetime.strptime(hms, fmt)
    return dt

def effective_variation(values):
    non_zero = [abs(v) for v in values if v != 0]
    if not non_zero:
        return 0
    return sum(non_zero) / len(non_zero)

def write_theoric_schedule() :
    endpoint = f"https://api.rtm.fr/front/getTheoricalTime?lineRef=RTM:LNE:140&direction=1&pointRef=RTM:PNT:00001747&date={yesterday()}"

    req = requests.get(endpoint)

    if req.status_code == 200 :
        data = req.json()
        with open("datas/today_21jet.json", "w") as f :
            f.write(json.dumps(data))
            print("done writing")
    else :
        print("failed")

def get_datetime_from_item(item) :
    departure_time = item["DepartureTime"]
    hour = departure_time[:7]
    return ToDateTime(hour)

buses = ["b1", "21jet"]

target = buses[1]

today_file = open(f"datas/today_{target}.json", "r")
today_json = json.loads(today_file.read())
today_json = today_json["data"]

all_hours = []

for item in today_json :
    all_hours.append(get_datetime_from_item(item))

variations = []

for i in range(len(all_hours) - 1) :
    h_i0 = all_hours[i]
    h_i1 = all_hours[i + 1]

    variation = (h_i0 - h_i1).total_seconds()
    variations.append(abs(((variation + SECONDS_ONE_DAY) % SECONDS_ONE_DAY) - SECONDS_ONE_DAY) / 60.0)

d_variations = []

for i in range(len(variations) - 1) :
    v_i0 = variations[i]
    v_i1 = variations[i + 1]

    variation = v_i0 - v_i1
    d_variations.append(abs(variation))

dict_variation = dict()
for v in d_variations :
    key = int(v)
    if key not in dict_variation.keys() :
        dict_variation[key] = 0
    dict_variation[key] = dict_variation[key] + 1

_norm = len(d_variations)                       # normalize from amount
#norm = max(dict_variation.values())        # normalize from max

normalize = False

if normalize :
    for key, value in dict_variation.items() :
        dict_variation[key] = dict_variation[key] / _norm

keys = sorted(dict_variation.keys())
values = [dict_variation[k] for k in keys]

eff_variation = effective_variation(d_variations)

print(eff_variation)

plt.bar(keys, values)
plt.xlabel('Variation (seconds)')
plt.ylabel('Amount')
plt.title(f'Amount of variations of {target} schedules')
plt.savefig("images/21jet_variations.png", dpi=300, bbox_inches="tight")
plt.show()

