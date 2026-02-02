from result import Result
from random import *
from algo import *
import time

def KeyName(algo: int, theos: int) -> str :
    return str(algo) + ":" + str(theos)

class Searcher :
    __work_interval = 60
    __results = dict()

    def StoreCache(key: str, result: Result) -> None :
        Searcher.__results[key] = result

    @staticmethod
    def ResultCached(algo: int, theos: int) -> bool :
        return KeyName(algo, theos) in Searcher.__results.keys()

    @staticmethod
    def SetWorkInterval(interval: int) -> None:
        """
        Set the time interval in which the Searcher will requests RTM API to update the cache.
        """
        __work_interval = max(0, interval)

    def GetResult(algo: int, theos: int) -> Result:
        if Searcher.ResultCached(algo, theos) :
            return Searcher.__results[KeyName(algo, theos)]
        return None

    @staticmethod
    def CheckForUpdate(algo: int, theos: int) -> bool:
        """
        Check if the specified result from the algorithm and theorems need an update.
        """

        must_update = False
        result_if_cached = Searcher.GetResult(algo, theos)
        last_time_updated = result_if_cached.Time() if result_if_cached is not None else 0
        work_interval = Searcher.__work_interval
        now = time.time()

        if (now - last_time_updated > work_interval) :
            must_update = True

        return must_update
    
    @staticmethod
    def Update(algo: int, theos: int) :
        key = KeyName(algo, theos)
        prob_b1, prob_21jet = Algorithms.Start(algo, theos)
        result = Result(prob_b1, prob_21jet, time.time())
        Searcher.StoreCache(key, result)