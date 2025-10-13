from datas import *
from names import *
import json

REALTIME_B1    = Data(DatasAPI.RealtimeLinePointUrl(LINE_B1, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_B1))
REALTIME_21JET = Data(DatasAPI.RealtimeLinePointUrl(LINE_21JET, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_21JET))

THEORIC_B1     = Data(DatasAPI.TheoricLinePointUrl(LINE_B1, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_B1, DatasAPI.WakeUpDay), SECONDS_ONE_DAY, DatasAPI.WakeUpDay())
THEORIC_21JET  = Data(DatasAPI.TheoricLinePointUrl(LINE_21JET, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_21JET, DatasAPI.WakeUpDay), SECONDS_ONE_DAY, DatasAPI.WakeUpDay())

ALL_STATIONS_B1     : list
ALL_STATIONS_21JET  : list

def ToDateTime(hms: str) -> datetime :
    fmt = "%H:%M:%S"
    dt = datetime.strptime(hms, fmt)
    return dt

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
        if datetime.now().time() < HOUR_LAST_21JET :
           print("The 21Jet bus can't pass for now, take B1")
           return 1, 0

        theorems = Theorem.Names(theos)
        if (algo == 0) :
            return Algorithms.SevenMinutesRule()
        elif (algo == 1) :
            return Algorithms.SeekingHeadRule()

    @staticmethod
    def SevenMinutesRule() :
        REALTIME_B1.Update()
        REALTIME_21JET.Update()
        
        next_b1_hms = REALTIME_B1.Get("temps_reel/0/DepartureTime/Hour")
        next_21jet_hms = REALTIME_21JET.Get("temps_reel/0/DepartureTime/Hour")
   
        print("[SEVEN_MINUTES_RULE] Prochain B1 :", next_b1_hms + ". Prochain 21Jet :", next_21jet_hms)

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
    def SeekingHeadRule() :
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
        
        current_hms_b1 = ToDateTime(next_b1_hms).timestamp()
        current_hms_21jet = ToDateTime(next_21jet_hms).timestamp()

        now = datetime.now().timestamp()

        accumulator_b1 = (current_hms_b1 - now)
        accumulator_21jet = (current_hms_21jet - now)

        # B1

        ## realtime

        cant_further_b1 = False
        look_at_b1 = 0
        i = 0

        while look_at_b1 < 2 and not cant_further_b1 and i < len(ALL_STATIONS_B1) :
            station_i: Data = ALL_STATIONS_B1[i]

            #As long as we do an update, it's better to sleep a while to avoid being blocked by the RTM API, even if they don't give a fuck about 5000 requests per sec from a 21 yo nerd
            station_i.Update()
            tme.sleep(0.25)

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
            theoric_gap_b1 = json.loads(f)
            while i < len(ALL_STATIONS_B1) :
                gap = theoric_gap_b1[str(i)]
                accumulator_b1 += gap
                i += 1

        # 21Jet

        cant_further_21jet = False
        look_at_21jet = 0
        i = 0

        while look_at_21jet < 2 and not cant_further_21jet and i < len(ALL_STATIONS_21JET) :
            station_i: Data = ALL_STATIONS_21JET[i]
            station_i.Update()
            tme.sleep(0.25)

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
            theoric_gap_21jet = json.loads(f)
            while i < len(ALL_STATIONS_21JET) :
                gap = theoric_gap_21jet[str(i)]
                accumulator_21jet += gap
                i += 1

        print("[SEEKING_HEAD_RULE] Temps B1 :", accumulator_b1, "Temps 21jet :", accumulator_21jet)

        if accumulator_b1 < accumulator_21jet :
            return 1, 0
        return 0, 1