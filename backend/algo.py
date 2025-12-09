from datas import *
from names import *
import json

REALTIME_B1    = Data(DatasAPI.RealtimeLinePointUrl(LINE_B1, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_B1))
REALTIME_21JET = Data(DatasAPI.RealtimeLinePointUrl(LINE_21JET, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_21JET))

THEORIC_B1     = Data(DatasAPI.TheoricLinePointUrl(LINE_B1, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_B1, DatasAPI.WakeUpDay), SECONDS_ONE_DAY, DatasAPI.WakeUpDay())
THEORIC_21JET  = Data(DatasAPI.TheoricLinePointUrl(LINE_21JET, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_21JET, DatasAPI.WakeUpDay), SECONDS_ONE_DAY, DatasAPI.WakeUpDay())

ALL_STATIONS_B1     : list
ALL_STATIONS_21JET  : list

SEEKING_HEAD_TIME_BETWEEN_REQUESTS = 0.05

THRESHOLD_NEXT_BUS_TIME = 30

def NextBusTime(b1_prob: float, jet21_prob: float, bus_to_watch: int = 0, threshold: float = THRESHOLD_NEXT_BUS_TIME) -> float:
    # ignores if we cannot track any bus
    if bus_to_watch >= 2 or (b1_prob == jet21_prob == 0):
        return -1

    if b1_prob > jet21_prob:
        hms = REALTIME_B1.Get(f"temps_reel/{bus_to_watch}/DepartureTime/Hour")
    else:
        hms = REALTIME_21JET.Get(f"temps_reel/{bus_to_watch}/DepartureTime/Hour")

    # rtm api gives no info about this bus
    if hms is None:
        return -1

    dt = ToDateTime(hms)
    now = Now()
    delta = (dt - now).total_seconds()

    if delta > 0:
        return delta # the time is in the future
    elif -threshold < delta <= 0:
        return 0 # we accept a small negative delta as "the bus is arriving now"
    else:
        return NextBusTime(b1_prob, jet21_prob, bus_to_watch + 1, threshold) # the bus has already passed, try the next one


def ToDateTime(hms: str) -> datetime:
    fmt = "%H:%M:%S"
    t = datetime.strptime(hms, fmt).time()
    return datetime.combine(date(1970, 1, 2), t)

def Now() -> datetime:
    tz = timezone(timedelta(hours=1))
    n = datetime.now(tz)
    return datetime(1970, 1, 2, n.hour, n.minute, n.second, n.microsecond)

def ToSeconds(hms: str) -> float :
    dt = ToDateTime(hms)
    return dt.timestamp()

class Algorithms :
    @staticmethod
    def InitConstants() :
        global ALL_STATIONS_B1
        global ALL_STATIONS_21JET

        ALL_STATIONS_B1 = []
        ALL_STATIONS_21JET = []
        with open("../datas/stations.txt", "r") as f :
            lines = f.readlines()
            for line in lines :
                _, pnt_ref, which_one = tuple(line.split("|"))
                ALL_STATIONS_B1.append(Data(DatasAPI.RealtimeLinePointUrl(LINE_B1, pnt_ref, DIR_RPDP_TO_LUMINY_B1)))
                if which_one == "2" :
                    ALL_STATIONS_21JET.append(Data(DatasAPI.RealtimeLinePointUrl(LINE_21JET, pnt_ref, DIR_RPDP_TO_LUMINY_B1)))

    @staticmethod
    def Start(algo: int, theos: int = 0) :

        """
        Starts the algorithm and return the probability.
        Result is (Probability of taking B1, Probability of taking 21Jet)
        """

        # Ignores if the last 21Jet passed
        if datetime.now().time() > HOUR_LAST_21JET :
           print("The 21Jet bus can't pass for now, take B1")
           return 1, 0, NextBusTime(1, 0)
        
        theorems = Theorem.Names(theos)
        b1_prob, jet21_prob = Algorithms.GetResultFromAlgo(algo, theorems)
        next_bus_time = NextBusTime(b1_prob, jet21_prob)

        return b1_prob, jet21_prob, next_bus_time

        
    def GetResultFromAlgo(algo: int, theorems: list[str]) :
        if (algo == 0) :
            return Algorithms.SevenMinutesRule()
        elif (algo == 1) :
            return Algorithms.SeekingHeadRule(theorems)

    @staticmethod
    def SevenMinutesRule() :
        REALTIME_B1.Update()
        REALTIME_21JET.Update()
        
        next_b1_hms = REALTIME_B1.Get("temps_reel/0/DepartureTime/Hour")
        next_21jet_hms = REALTIME_21JET.Get("temps_reel/0/DepartureTime/Hour")
   
        print("[SEVEN_MINUTES_RULE] Prochain B1 :", str(next_b1_hms) + ". Prochain 21Jet :", str(next_21jet_hms))

        if next_b1_hms is None and next_21jet_hms is not None :
            return 0, 1
        if next_b1_hms is not None and next_21jet_hms is None :
            return 1, 0
        if next_b1_hms is None and next_21jet_hms is None :
            return 0, 0

        next_b1_hms = ToDateTime(next_b1_hms)
        next_21jet_hms = ToDateTime(next_21jet_hms)

        delta = (next_21jet_hms - next_b1_hms).total_seconds()

        if delta <= 7 * 60 :
            return 0, 1
        return 1, 0
    
    @staticmethod
    def SeekingHeadRule(theorems) :
        REALTIME_B1.Update()
        REALTIME_21JET.Update()

        next_b1_hms = REALTIME_B1.Get("temps_reel/0/DepartureTime/Hour")
        next_21jet_hms = REALTIME_21JET.Get("temps_reel/0/DepartureTime/Hour")

        if next_b1_hms is None and next_21jet_hms is not None :
            return 0, 1
        if next_b1_hms is not None and next_21jet_hms is None :
            return 1, 0
        if next_b1_hms is None and next_21jet_hms is None :
            return 0, 0
        
        next_b1_hms = ToDateTime(next_b1_hms)
        next_21jet_hms = ToDateTime(next_21jet_hms)
        
        current_hms_b1 = next_b1_hms.timestamp()
        current_hms_21jet = next_21jet_hms.timestamp()

        now = Now().timestamp()

        accumulator_b1 = (current_hms_b1 - now)
        accumulator_21jet = (current_hms_21jet - now)

        slowness_obelisk_theorem = 1.25 if Theorem.OBELISK_THEOREM in theorems else 1.0

        # B1

        ## realtime

        cant_further_b1 = False
        look_at_b1 = 0
        i = 0

        while look_at_b1 < 2 and not cant_further_b1 and i < len(ALL_STATIONS_B1) :
            station_i: Data = ALL_STATIONS_B1[i]

            #As long as we do an update, it's better to sleep a while to avoid being blocked by the RTM API, even if they don't give a fuck about 5000 requests per sec from a 21 yo nerd
            station_i.Update()
            tme.sleep(SEEKING_HEAD_TIME_BETWEEN_REQUESTS)

            b1_at_i_hms = station_i.Get(f"temps_reel/{look_at_b1}/DepartureTime/Hour")
            if b1_at_i_hms is None :
                # There is no realtime bus, switch to theoric method
                cant_further_b1 = True
                break
            
            b1_at_i_hms = ToDateTime(b1_at_i_hms).timestamp()

            if current_hms_b1 < b1_at_i_hms :
                # The next bus at this station is currently the bus we are tracking, keep tracking him.
                gap = b1_at_i_hms - current_hms_b1
                accumulator_b1 += gap
                current_hms_b1 = b1_at_i_hms
                i += 1
            else :
                # The next bus is not the bus we are tracking, the bus after it is now the tracked one.
                look_at_b1 += 1
                # Don't increase i and restart the while loop with the new look_at value

        ## theoric

        with open("../datas/seeking_head/theoric_gap_b1.json", "r") as f :
            theoric_gap_b1 = json.loads(f.read())
            while i < len(ALL_STATIONS_B1) :
                gap_choice = theoric_gap_b1[str(i)]
                gap : float
                if Theorem.SEEKING_HEAD_CONSIDER_MAX in theorems :
                    gap = gap_choice["max"] 
                else :
                    gap = gap_choice["average"] + gap_choice["std"]
                if Theorem.OBELISK_THEOREM in theorems and i <= 8 :
                    gap *= slowness_obelisk_theorem
                accumulator_b1 += gap
                i += 1

        # 21Jet

        cant_further_21jet = False
        look_at_21jet = 0
        i = 0

        while look_at_21jet < 2 and not cant_further_21jet and i < len(ALL_STATIONS_21JET) :
            station_i: Data = ALL_STATIONS_21JET[i]
            station_i.Update()
            tme.sleep(SEEKING_HEAD_TIME_BETWEEN_REQUESTS)

            _21jet_at_i_hms = station_i.Get(f"temps_reel/{look_at_21jet}/DepartureTime/Hour")
            if _21jet_at_i_hms is None :
                cant_further_21jet = True
                break
            
            _21jet_at_i_hms = ToDateTime(_21jet_at_i_hms).timestamp()

            if current_hms_21jet < _21jet_at_i_hms :
                gap = _21jet_at_i_hms - current_hms_21jet
                accumulator_21jet += gap
                current_hms_21jet = _21jet_at_i_hms
                i += 1
            else :
                look_at_21jet += 1

        ## theoric

        with open("../datas/seeking_head/theoric_gap_21jet.json", "r") as f :
            theoric_gap_21jet = json.loads(f.read())
            while i < len(ALL_STATIONS_21JET) :
                gap_choice = theoric_gap_21jet[str(i)]
                gap : float
                if Theorem.SEEKING_HEAD_CONSIDER_MAX in theorems :
                    gap = gap_choice["max"] 
                else :
                    gap = gap_choice["average"] + gap_choice["std"]
                accumulator_21jet += gap
                i += 1

        print("[SEEKING_HEAD_RULE] Temps B1 :", accumulator_b1, "Temps 21jet :", accumulator_21jet)

        if accumulator_b1 < accumulator_21jet :
            return 1, 0
        return 0, 1
