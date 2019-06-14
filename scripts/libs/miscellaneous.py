###############################################
###Get time and convert it to human readable###
###############################################
def printRuntime(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return str(seconds) + 's'
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds - 60 * minutes
        return str(minutes) + 'm : ' + str(seconds) + 's'
    else:
        hours = seconds // 3600
        minutes = (seconds - 3600 * hours) // 60
        seconds = seconds - 3600 * hours - 60 * minutes
        return str(hours) + 'h : ' + str(minutes) + 'm : ' + str(seconds) + 's'


###############################
##Index Management#############
###############################
def indexManagement(qty=int, startIndex=int, stopIndex=int):
    if qty and startIndex:
        stopIndex = qty + startIndex - 1
    elif qty:
        startIndex = 1
        stopIndex = qty + 1
    return startIndex, stopIndex


##################################
###Resources created messaging####
##################################
def outputNrOfElements(resourceType='', inputCount=0, outputCount=0):
    if inputCount == outputCount:
        print("Resource type: " + resourceType + ".All " + str(outputCount) + " resources were created successfully")
        testResult = 0
    else:
        print("Error when creating resources: " + resourceType + " .Input: " + str(inputCount) + " .Output: " + str(
            outputCount))
        testResult = 1
    return testResult
