from datetime import datetime, time
import requests

"""
Here, we are trying to search the variation max_delta_t which
define the maximum amount of difference between two consecutives
schedule cf. schedule(i + 1) + max_delta_t = schedule(i)
"""

def today() :
    return datetime.strftime(datetime.now(), "%Y-%m-%d")

endpoint_b1 = f"https://api.rtm.fr/front/getTheoricalTime?lineRef=RTM:LNE:139&direction=1&pointRef=RTM:PNT:00001747&date={today()}"

req = requests.get()