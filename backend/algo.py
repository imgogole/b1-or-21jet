from names import *
from datas import *

REALTIME_B1    = Data(DatasAPI.RealtimeLinePointUrl(LINE_B1, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_B1))
REALTIME_21JET = Data(DatasAPI.RealtimeLinePointUrl(LINE_21JET, PNT_ROND_POINT_DU_PRADO, DIR_RPDP_TO_LUMINY_21JET))

def ToDateTime(hms: str) -> datetime :
    fmt = "%H:%M:%S"
    dt = datetime.strptime(hms, fmt)
    return dt

class Algorithms :
    @staticmethod
    def Start(algo: int, theos: int = 0) :

        """
        Starts the algorithm and return the probability.
        Result is (Probability of taking B1, Probability of taking 21Jet)
        """

        theorems = Theorem.Names(theos)
        if (algo == 0) :
            return Algorithms.SevenMinutesRule()

    @staticmethod
    def SevenMinutesRule() :
        REALTIME_B1.Update()
        REALTIME_21JET.Update()
        
        next_b1_hms = REALTIME_B1.Get("temps_reel/0/DepartureTime/Hour")
        next_21jet_hms = REALTIME_21JET.Get("temps_reel/0/DepartureTime/Hour")
   
        print("Règle des 7 minutes : Prochain B1 :", next_b1_hms + ". Prochain 21Jet :", next_21jet_hms)

        next_b1_hms = ToDateTime(next_b1_hms)
        next_21jet_hms = ToDateTime(next_21jet_hms)

        delta = (next_21jet_hms - next_b1_hms).total_seconds()

        if delta <= 7 * 60 :
            return 0, 1
        return 1, 0
    