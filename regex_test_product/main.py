from ui import UI
import re
from datetime import datetime, timedelta





window = UI()

# ESTIMATED_TIME = "Started 1 min 57 sec ago<br> Estimated remaining time: 3 min 18 sec"
# minutes = re.search('.* (\\d+) min (\\d+) sec$', ESTIMATED_TIME).group(1)
# sec = re.search('.* (\\d+) min (\\d+) sec$', ESTIMATED_TIME).group(2)
#
# print(minutes)
# print(sec)
#
# time_duration = timedelta(minutes=int(minutes), seconds=int(sec))
# future_time = datetime.now() + time_duration
#
# CURRENT_TIME = datetime.now()
# print(future_time)
#
# if CURRENT_TIME < future_time:
#     time_difference = future_time - CURRENT_TIME
#     print(f"{int(time_difference.total_seconds()//60)} minutes {int(time_difference.total_seconds() % 60)} sec")
# else:
#     print("time over")

#---------------------- Jenkins Code --------------------------------
