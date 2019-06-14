from miscellaneous import printRuntime
import threading
import restRequests
import argparse
import atexit
import psutil
import time


def updateToDelete(newDict, toUpdate):
    for key in newDict:
        for elem in newDict[key]:
            try:
                toUpdate[key].append(elem)
            except:
                toUpdate[key] = newDict[key]
                break
    return toUpdate


##################################################
###Sample and output performance utilization data####
##################################################
def performanceUtilization(stop_event, interval):
    utilization = {'cpu': {'min': 0, 'max': 0, 'values': []}, 'memory': {'min': 0, 'max': 0, 'values': []}}
    startTime = time.perf_counter()
    while not stop_event.is_set():
        try:
            utilization['cpu']['values'].append(psutil.cpu_percent(interval=interval))
            # utilization['memory']['values'].append(psutil.Process(os.getpid()).memory_info().rss / float(2 ** 20))
            utilization['memory']['values'].append(round(psutil.virtual_memory().used / float(2 ** 20)))
        except:
            print('ERROR when getting cpu/memory info')
    try:
        utilization['cpu']['min'] = min(utilization['cpu']['values'])
        utilization['cpu']['max'] = max(utilization['cpu']['values'])
        utilization['memory']['min'] = min(utilization['memory']['values'])
        utilization['memory']['max'] = max(utilization['memory']['values'])
    except:
        print('ERROR when assigning cpu/memory utilization data into dictionary')
    try:
        '''Output of CPU utilization '''
        print('- CPU utilization(%) - ')
        print('Minimum: ' + str(utilization['cpu']['min']))
        print('Maximum: ' + str(utilization['cpu']['max']))
        print('Average: ' + str(round(sum(utilization['cpu']['values']) / len(utilization['cpu']['values']), 2)))
    except:
        print('ERROR when returning to output CPU utilization results')
    try:
        '''Output of Memory utilization '''
        print('- Memory utilization(Mbs) - ')
        print('Minimum: ' + str(utilization['memory']['min']))
        print('Maximum: ' + str(utilization['memory']['max']))
        print('Average: ' + str(round(sum(utilization['memory']['values']) / len(utilization['memory']['values']), 2)))
    except:
        print('ERROR when returning to output Memory utilization results')
    try:
        print('Execution time: ' + printRuntime(round(time.perf_counter() - startTime)))
    except:
        print('ERROR when returning execution time')
    print('- Execution finished -')


###################################################
###Main execution thread for performance testing###
###################################################
def executionThread(velo, resources, abstractResources, topologies, subtopologies, portGroupsResources, vSphereClouds,
                    openstackClouds, LayerTopology, Abstract_Topology):
    '''Variable Definition'''
    toDelete = {}
    testResult = 0
    print('- Begining of execution -')

    '''At script exit -> call cleanup'''
    atexit.register(restRequests.cleanup, toDelete=toDelete, velo=velo, testResult=testResult)

    ##############################
    ######Create Resources########
    ##############################
    '''Create resources and update cleaning object'''
    resources, testResult = restRequests.createResources(velo, resources)
    toDelete = updateToDelete(resources, toDelete)

    '''Create abstract resources and update cleaning object'''
    abstractResources, testResult = restRequests.createAbstractResources(velo, abstractResources,
                                                                         condition='template[PC]')
    toDelete = updateToDelete(abstractResources, toDelete)

    ############################################
    ###Publish topology and copy it X times#####
    ############################################
    '''			X Topologies require X resources in order to reserve
    '''
    topologies, testResult = restRequests.createCopyTopologies(velo, Abstract_Topology, qty=topologies,
                                                               topologyName='PerformanceTestTopology')
    toDelete = updateToDelete(topologies, toDelete)

    #######################################################
    ###Publish 5 layer subtopology and copy it X times#####
    #######################################################
    '''			X Topologies require 5X resources in order to reserve
    '''
    topologies, testResult = restRequests.createCopyTopologies(velo, LayerTopology, qty=subtopologies,
                                                               topologyName='Performance5LayerTestTopology')
    toDelete = updateToDelete(topologies, toDelete)

    ############################################
    ##########Reserve topologies################
    ############################################
    reservations, testResult = restRequests.reserveTopologies(velo, topologies['topologyList'])
    toDelete = updateToDelete(reservations, toDelete)

    ##################################################
    #####Create devices with ports and port groups####
    ##################################################
    '''Create resources and add ports and port groups
    '''
    portGroupsResources, testResult = restRequests.createPortGroups(velo, qty=portGroupsResources)
    toDelete = updateToDelete(portGroupsResources, toDelete)

    ########################
    ###Create Clouds########
    ########################
    '''Create vSphere Clouds
    '''
    vSphereClouds, testResult = restRequests.createVsphereClouds(velo, qty=vSphereClouds)
    toDelete = updateToDelete(vSphereClouds, toDelete)

    '''Create vSphere Clouds
    '''
    openstackClouds, testResult = restRequests.createOpenStackClouds(velo, qty=openstackClouds)
    toDelete = updateToDelete(openstackClouds, toDelete)


######Arguments parser##############
parser = argparse.ArgumentParser(description=
                                 """NOTE: The given ranges of various elements creation 
                                 should be compatible with one another. (Number of 
                                 resources should coincide with number of topologies)""")

######Argument List###################
parser.add_argument('-resources',
                    help="Number of resources to create. Nr of resources must be: topologies + 5*subtopologies")
parser.add_argument('-abstractResources', help="Number of abstract resources to create")
parser.add_argument('-topologies', help="Number of topologies to create")
parser.add_argument('-subtopologies', help="Number of 5 layer topologies to create")
parser.add_argument('-portGroupsResources', help="Number of devices with port groups linked to each other")
parser.add_argument('-vsphereClouds', help="Number of vSphere clouds to create")
parser.add_argument('-openstackClouds', help="Number of OpenStack clouds to create")
parser.add_argument('-velo', help="Velocity VM")
parser.add_argument('-LayerTopology', help="path to topology file")
parser.add_argument('-Abstract_Topology', help="path to topology file")

args = parser.parse_args()

if __name__ == '__main__':
    try:
        interval = 10  # Interval to get cpu/memory utilization
        pill2kill = threading.Event()
        t = threading.Thread(target=performanceUtilization, args=(pill2kill, interval))
        t.start()
        executionThread(args.velo, int(args.resources), int(args.abstractResources), int(args.topologies),
                        int(args.subtopologies), int(args.portGroupsResources), int(args.vsphereClouds),
                        int(args.openstackClouds), args.LayerTopology, args.Abstract_Topology)
    # testResult = executionThread('vel-agrama-latest', 10, 5, 1, 1, 5, 2, 2)
    except Exception as e:
        print("ERROR at creating performanceUtilization thread or starting of execution: " + str(e))
    finally:
        pill2kill.set()
        t.join()
