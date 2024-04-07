from collections import defaultdict
import pickle
from itertools import chain

class Utils:
    def loadMarkers():
        with open('resources/markers.pkl', 'rb') as f:
            markers = pickle.load(f)
            uniqueMarkers = {}
            for i in markers.keys():
                uniqueMarkers[i] = [[],[]]

            markerCountsWC = defaultdict(int)
            markerCountsAU = defaultdict(int)
            allMarks = list(chain(markers))
            for i in allMarks:
                for x in markers[i][0]:
                    markerCountsWC[x] += 1

                for x in markers[i][1]:
                    markerCountsAU[x] += 1

            for i in allMarks:
                for x in range(len(markers[i][0])):
                    if ":" not in markers[i][0][x]:

                        markers[i][0][x] = markers[i][0][x] + ":" + str(markerCountsWC[markers[i][0][x]])
                for x in range(len(markers[i][1])):
                    if ":" not in markers[i][1][x]:
                        markers[i][1][x] = markers[i][1][x] + ":" + str(markerCountsAU[markers[i][1][x]])
                markers[i][0].sort(key=lambda s: int(s.split(":")[1]))
                markers[i][1].sort(key=lambda s: int(s.split(":")[1]))

        return markers