import requests
import json
from restRequests import getTime, getTopologies

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def getUrl(endpoint):
    urlDict = {
        'token': '/velocity/api/auth/v2/token',
        'report': '/ito/reporting/v1/reports',
        'cloud': '/velocity/api/cloud/v4/cloud',
        'topology': '/velocity/api/topology/v8/topology',
        'topologies': '/velocity/api/topology/v8/topologies',
        'device': '/velocity/api/inventory/v9/device',
        'reservation': '/velocity/api/reservation/v11/reservation',
        'abstract_resource': '/velocity/api/inventory/v8/abstract_resource'
    }
    return urlDict[endpoint]


def postScheduledReservations(velo='', topologyList=[], duration=0, timeToStart=0):
    postReservationUrl = "https://" + velo + ".spirenteng.com" + getUrl('reservation')
    reservationName = 'Virtual topology reservation test'
    timeToStart = timeToStart * 1000
    currentTime = getTime(velo)
    for i, topId in enumerate(topologyList):
        raw = {}
        raw['name'] = reservationName + str(i + 1)
        raw['duration'] = duration
        raw['start'] = currentTime + timeToStart
        raw['topologyId'] = topId
        rq = requests.post(postReservationUrl, data=json.dumps(raw), verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Error encountered posting reservation: ' + rq.text)
        print(rq.text)


if __name__ == '__main__':
    velo = 'vel-agrama-latest'
    topologies = getTopologies(velo, 'Vcenter test1')
    postScheduledReservations(velo, topologies, duration=600, timeToStart=180)
