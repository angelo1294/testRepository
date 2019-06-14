from miscellaneous import indexManagement, outputNrOfElements
import requests
import json
import requests.packages.urllib3.exceptions
import yaml
import sys

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


##################
###URL handling###
##################
def getUrl(endpoint):
    urlDict = {
        'token':             '/velocity/api/auth/v2/token',
        'report':            '/ito/reporting/v1/reports',
        'cloud':             '/velocity/api/cloud/v4/cloud',
        'topology':          '/velocity/api/topology/v8/topology',
        'device':            '/velocity/api/inventory/v9/device',
        'reservation':       '/velocity/api/reservation/v11/reservation',
        'abstract_resource': '/velocity/api/inventory/v8/abstract_resource',
        'logout':            '/velocity/api/auth/v2/logout',
        'user':              '/velocity/api/user/v8/profile'
    }
    return urlDict[endpoint]


################
###Get Token####
################
def getToken(velo='', username='spirent', password='spirent'):
    url = 'https://' + velo + '.spirenteng.com' + getUrl('token')
    rq = requests.get(url, verify=False, auth=(username, password))
    if 'errorId' not in rq.text:
        return json.loads(rq.text)['token']
    else:
        print('Error encountered when retrieving token')


def getTime(velo=''):
    url = 'https://' + velo + '.spirenteng.com/velocity/api/util/v1/time'
    rq = requests.get(url, verify=False, auth=('spirent', 'spirent'))
    return json.loads(rq.text)['time']


#########################
####Get Report Id########
#########################
def getReportId(velo='', testName=''):
    url = "https://" + velo + '.spirenteng.com' + getUrl(
        'report') + '?searchString=' + testName + '&sortBy=createTime&sortOrder=desc'
    token = getToken(velo)

    rq = requests.get(url, verify=False, auth=('spirent', 'spirent'),
                      headers={'X-Auth-Token': token, 'Content-type': 'application/json'})
    if 'errorId' not in rq.text:
        return json.loads(rq.text)['content'][0]['guid']
    else:
        print('Error encountered when retrieving report id: ' + rq.text)


def getTopologies(velo='', searchString=''):
    topologyList = []
    url = 'https://' + velo + '.spirenteng.com' + getUrl('topologies') + '?searchString=' + searchString + '&limit=100'
    rq = requests.get(url, verify=False, auth=('spirent', 'spirent'))
    if 'errorId' in rq.text:
        print('Error encountered when fetching topologies: ' + rq.text)
        return topologyList
    for topology in json.loads(rq.text)['topologies']:
        topologyList.append(topology['id'])
    return topologyList


def userLogout(velo='', token=''):
    url = 'https://' + velo + '.spirenteng.com' + getUrl('logout')
    state = True
    rq = requests.get(url, verify=False, headers={'X-Auth-Token': token, 'Content-type': 'application/json'})
    if 'errorId' in rq.text:
        state = False
    return state


def iteUserHandling(ite='', mode='', userid='', name='', password='', sysUser='root', sysPass='admin'):
    state = True
    url = 'https://' + ite + '.spirenteng.com/useradm'
    data = 'mode=%s&userid=%s&name=%s&password=%s' % (mode, userid, name, password)
    rq = requests.post(url, data=data, verify=False, auth=(sysUser, sysPass))
    if 'errorId' in rq.text:
        print('Error encountered when creating user')
        state = False
    return state


###########################
###Get report id details###
###########################
def getReportDetails(velo='', reportId=''):
    url = "https://" + velo + '.spirenteng.com/ito/reporting/v1/reports/' + reportId
    token = getToken(velo)
    '''Get report result '''
    rq = requests.get(url, verify=False, headers={'X-Auth-Token': token, 'Content-type': 'application/json'})
    if 'errorId' not in rq.text:
        result = json.loads(rq.text)['result']
    else:
        print('Error encountered in retrieving report result: ' + rq.text)
    ''' Get report data '''
    rq = requests.get(url + '/print', verify=False, headers={'X-Auth-Token': token, 'Content-type': 'application/json'})
    if 'errorId' not in rq.text:
        data = rq.text
    else:
        print('Error encountered in retrieving report result: ' + rq.text)
    if result:
        return result


def getUsers(velo='', limit=200, username='spirent', password='spirent'):
    offset = 0
    userIdList = []
    while (True):
        url = 'https://' + velo + '.spirenteng.com' + getUrl('user') + 's' + '/' + '?limit=' + str(
            limit) + '&offset=' + str(offset)
        rq = requests.get(url, verify=False, auth=(username, password))
        if 'errorId' not in rq.text:
            response = json.loads(rq.text)
            for index in range(0, int(response['count'])):
                userIdList.append(response['profiles'][index]['id'])
            if (int(json.loads(rq.text)['offset']) + limit) > int(json.loads(rq.text)['total']):
                return list(set(userIdList))
            else:
                offset = offset + limit
        else:
            print('Error encountered when fetching user list')
            return list(set(userIdList))


###############################
##Create vSphere Clouds########
###############################
def createVsphereClouds(velo, qty='', startIndex='', stopIndex='', cloudName='Performance vSphere Cloud',
                        username='spirent@vshphere.local', password='Spirent123!',
                        endpoint='https://vcenter-apt-dut.spirenteng.com/sdk'):
    BaseUrl = "https://" + velo + ".spirenteng.com" + getUrl('cloud')
    toDelete = {'cloudList': []}
    ####Index Management###
    startIndex, stopIndex = indexManagement(qty, startIndex, stopIndex)
    ####Create Clouds####
    for i in range(startIndex, stopIndex):
        body = {}
        body['providerType'] = 'VMWARE'
        body['name'] = cloudName + str(i)
        body['description'] = 'vSferaIndex Testing <-> Agrama teritory. Beware of clickbaits'
        body['endpoint'] = endpoint
        body['credentials'] = {'username': username, 'password': password}
        body = json.dumps(body)
        rq = requests.post(BaseUrl, data=body, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Resource creation error. Message: ' + result['message'])
        else:
            toDelete['cloudList'].append(result['id'])
    testResult = outputNrOfElements(cloudName, stopIndex - startIndex, len(toDelete['cloudList']))
    return toDelete, testResult


###############################
##Create OpenStack clouds######
###############################
def createOpenStackClouds(velo, qty='', startIndex='', stopIndex='', cloudName='Performance OpenStack Cloud',
                          username='admin_gimi', password='admin_gimi!', endpoint='http://10.140.71.22:5000/v3'):
    BaseUrl = "https://" + velo + ".spirenteng.com" + getUrl('cloud')
    toDelete = {'cloudList': []}
    ####Index Management###
    startIndex, stopIndex = indexManagement(qty, startIndex, stopIndex)
    ####Create Clouds####
    for i in range(startIndex, stopIndex):
        body = {}
        body['providerType'] = 'OPEN_STACK'
        body['name'] = cloudName + str(i)
        body['description'] = 'OpixStiva <-> Agrama teritory. Beware of clickbaits'
        body['endpoint'] = endpoint
        body['credentials'] = {'username': username, 'password': password}
        body['properties'] = [{'id': 'domain', 'value': 'gimi_test'}, {'id': 'region', 'value': 'RegionOne'},
                              {'id': 'tenant', 'value': 'admin_gimi'}]
        body = json.dumps(body)
        rq = requests.post(BaseUrl, data=body, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Resource creation error. Message: ' + result['message'])
        else:
            toDelete['cloudList'].append(result['id'])
    testResult = outputNrOfElements(cloudName, stopIndex - startIndex, len(toDelete['cloudList']))
    return toDelete, testResult


########################################
##Copy published abstract topology######
########################################
def createCopyTopologies(velo, topologyBodyPath, qty='', startIndex='', stopIndex='',
                         topologyName='Performance Topology Test'):
    initPostUrl = "https://" + velo + ".spirenteng.com" + getUrl('topology')
    toDelete = {'topologyList': []}
    ####Open initial topology#####
    with open(topologyBodyPath, 'r') as stream:
        try:
            topologyBody = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
    ####Post initial topology###
    data = yaml.dump(topologyBody, default_flow_style=False)
    rq = requests.post(initPostUrl, data=data, verify=False, auth=('spirent', 'spirent'),
                       headers={'Content-type': 'application/vnd.spirent-velocity.topology.tosca+yaml'})
    initial = json.loads(rq.text)
    if 'errorId' in rq.text:
        print('Topology creation error. Message: ' + initial['message'])
    copyPostUrl = initPostUrl + '?copyFrom=' + initial['id']
    ####Index Management###########
    startIndex, stopIndex = indexManagement(qty, startIndex, stopIndex)
    ####Copy the topology and publish it########
    for i in range(startIndex, stopIndex):
        raw = {}
        raw['name'] = topologyName + ' ' + str(i)
        raw['isAbstract'] = 'true'
        raw = json.dumps(raw)
        rq = requests.post(copyPostUrl, data=raw, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        BaseUrlPUT = "https://" + velo + ".spirenteng.com" + getUrl('topology') + '/' + result['id']
        body = {}
        body['isDraft'] = 'false'
        body = json.dumps(body)
        rq = requests.put(BaseUrlPUT, data=body, verify=False, auth=('spirent', 'spirent'),
                          headers={'Content-type': 'application/json'})
        topology = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Topology publishing error. Message: ' + topology['message'])
        else:
            toDelete['topologyList'].append(topology['id'])
    testResult = outputNrOfElements(topologyName, stopIndex - startIndex, len(toDelete["topologyList"]))
    ####Delete initial topology####
    rq = requests.delete(initPostUrl + '/' + initial['id'], verify=False, auth=('spirent', 'spirent'))
    return toDelete, testResult


##############################
##Create port groups##########
##############################
def createPortGroups(velo, deviceTemplateId='fea52e8b-8d75-455e-baa5-80751d9625c7',
                     portTemplateId='a5266606-f35b-482b-8c3f-a4317c1ccbb9',
                     qty='', startIndex='', stopIndex='', portsPerGroup=5, deviceName='Performance Port Group Test'):
    devicePostUrl = "https://" + velo + ".spirenteng.com" + getUrl('device')
    toDelete = {'deviceList': []}
    previousGroupId = ''
    ####Create ports json#################
    portsBody = {}
    portsBody['ports'] = []
    port = {}
    for i in range(1, portsPerGroup + 1):
        port['groupId'] = 'Some Id'
        port['name'] = 'Port ' + str(i)
        port['templateId'] = portTemplateId
        portsBody['ports'].append(port.copy())
    ####Index management##########################
    startIndex, stopIndex = indexManagement(qty, startIndex, stopIndex)
    ########Device handling######################
    for i in range(startIndex, stopIndex):
        deviceBody = {}
        deviceBody['name'] = deviceName + str(i)
        deviceBody['templateId'] = deviceTemplateId
        deviceBody = json.dumps(deviceBody)
        rq = requests.post(devicePostUrl, data=deviceBody, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        deviceResult = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Topology publishing error. Message: ' + deviceResult['message'])
        else:
            toDelete['deviceList'].append(deviceResult['id'])
        ########Port Group handling##############
        portGroupPostUrl = "https://" + velo + ".spirenteng.com/velocity/api/inventory/v8/device/" + deviceResult[
            'id'] + "/port_group"
        groupBody = {}
        groupBody['name'] = 'Port Group ' + str(i)
        manualAssociations = {}
        manualAssociations['id'] = previousGroupId
        groupBody['manualAssociations'] = [manualAssociations]
        groupBody = json.dumps(groupBody)
        rq = requests.post(portGroupPostUrl, data=groupBody, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        portGroupResult = json.loads(rq.text)
        ########Save group id as previous to link device port group to the next#####
        previousGroupId = portGroupResult['id']
        # ########Ports handling####################
        portPostUrl = "https://" + velo + ".spirenteng.com/velocity/api/inventory/v8/device/" + deviceResult[
            'id'] + "/ports"
        for d in portsBody['ports']:
            d.update({'groupId': portGroupResult['id']})
        portsBodyResult = json.dumps(portsBody.copy())
        rq = requests.post(portPostUrl, data=portsBodyResult, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
    testResult = outputNrOfElements(deviceName, stopIndex - startIndex, len(toDelete["deviceList"]))
    return toDelete, testResult


###################################
#######Reserve topologies##########
###################################
def reserveTopologies(velo, topologyIdList, start='', end='', duration='600'):
    postReservationUrl = "https://" + velo + ".spirenteng.com" + getUrl('reservation')
    toDelete = {'reservationList': []}
    reservationName = 'Topology reservation test'
    for i, topId in enumerate(topologyIdList):
        raw = {}
        raw['name'] = reservationName + str(i + 1)
        if duration:
            raw['duration'] = duration
        if start:
            raw['start'] = start
        if end:
            raw['end'] = end
        raw['topologyId'] = topId
        rq = requests.post(postReservationUrl, data=json.dumps(raw), verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        toDelete['reservationList'].append(result['id'])
    testResult = outputNrOfElements(reservationName, len(topologyIdList), len(toDelete['reservationList']))
    return toDelete, testResult


###################################
#######Create Resources(PC)########
###################################        
def createResources(velo, qty='', startIndex='', stopIndex='', templateId='fea52e8b-8d75-455e-baa5-80751d9625c7'):
    BaseUrl = "https://" + velo + ".spirenteng.com" + getUrl('device')
    toDelete = {'deviceList': []}
    deviceName = 'Performance PC'
    ####Index Management#####
    startIndex, stopIndex = indexManagement(qty, startIndex, stopIndex)
    ####Create resources#####
    for i in range(startIndex, stopIndex):
        raw = {}
        raw['name'] = deviceName + str(i)
        raw['templateId'] = templateId
        body = json.dumps(raw.copy())
        rq = requests.post(BaseUrl, data=body, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Resource creation error. Message: ' + result['message'])
        else:
            toDelete['deviceList'].append(result['id'])
    testResult = outputNrOfElements(deviceName, stopIndex - startIndex, len(toDelete['deviceList']))
    return toDelete, testResult


###################################
#######Create Abstract resources Resources(PC)########
###################################        
def createAbstractResources(velo, qty='', startIndex='', stopIndex='', condition=''):
    BaseUrl = "https://" + velo + ".spirenteng.com" + getUrl('abstract_resource')
    toDelete = {'abstractDeviceList': []}
    deviceName = 'Abstract Performance Device'
    ####Index Management#####
    startIndex, stopIndex = indexManagement(qty, startIndex, stopIndex)
    ####Create resources#####
    for i in range(startIndex, stopIndex):
        raw = {}
        raw['name'] = deviceName + str(i)
        raw['type'] = 'DEVICE'
        raw['condition'] = condition
        body = json.dumps(raw.copy())
        rq = requests.post(BaseUrl, data=body, verify=False, auth=('spirent', 'spirent'),
                           headers={'Content-type': 'application/json'})
        result = json.loads(rq.text)
        if 'errorId' in rq.text:
            print('Resource creation error. Message: ' + result['message'])
        else:
            toDelete['abstractDeviceList'].append(result['id'])
    testResult = outputNrOfElements(deviceName, stopIndex - startIndex, len(toDelete['abstractDeviceList']))
    return toDelete, testResult


def putUser(velo='', userIdList=[], email='no@reply.com'):
    for userId in userIdList:
        url = 'https://' + velo + '.spirenteng.com' + getUrl('user') + '/' + userId
        data = {}
        data['receivesEmailNotifications'] = True
        data['email'] = email
        rq = requests.put(url, data=json.dumps(data), verify=False, auth=('spirent', 'spirent'),
                          headers={'Content-type': 'application/json'})


################################################
#########Cleanup Procedure######################
################################################
def cleanup(toDelete={}, velo='vel-agrama-latest', testResult=0):
    urlDict = {'deviceList':         '.spirenteng.com' + getUrl('device') + '/',
               'topologyList':       '.spirenteng.com' + getUrl('topology') + '/',
               'reservationList':    '.spirenteng.com' + getUrl('reservation') + '/',
               'abstractDeviceList': '.spirenteng.com' + getUrl('abstract_resource') + '/',
               'cloudList':          '.spirenteng.com' + getUrl('abstract_resource') + '/'}
    ####Cancel reservation####
    try:
        if toDelete['reservationList']:
            for elem in toDelete['reservationList']:
                delUrl = 'https://' + velo + urlDict['reservationList'] + elem + '/action?type=cancel'
                rq = requests.post(delUrl, verify=False, auth=('spirent', 'spirent'))
                try:
                    if 'error' in rq.text:
                        print('Reservation cancel error. Message: ' + rq.text)
                        testResult = 1
                except Exception as error:
                    print('Script error in cleanup -> reservation cancel. Error message: \n' + error.message)
                    testResult = 1
            toDelete.pop('reservationList')
    except KeyError:
        pass
    ####Delete elements#######
    for key in toDelete:
        for elem in toDelete[key]:
            delUrl = 'https://' + velo + urlDict[key] + elem
            rq = requests.delete(delUrl, verify=False, auth=('spirent', 'spirent'))
            try:
                if 'error' in rq.text:
                    print('Item delete error. Message: ' + rq.text)
            except Exception as error:
                print('Script error in cleanup.Error message: \n' + error.message)
    assert not testResult, sys.exit(1)
