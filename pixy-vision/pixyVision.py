from __future__ import print_function
import pixy 
import time
import json
from ctypes import *
from pixy import *
from constants import *
from networktables import NetworkTablesInstance
from networktables import NetworkTables


# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

configFile = "/boot/frc.json"

class CameraConfig: pass

team = None
server = False

def parseError(str):
    """Report parse error."""
    print("config error in '" + configFile + "': " + str, file=sys.stderr)

def readConfig():
    """Read configuration file."""
    global team
    global server

    # parse file
    try:
        with open(configFile, "rt", encoding="utf-8") as f:
            j = json.load(f)
    except OSError as err:
        print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
        return False

    # top level must be an object
    if not isinstance(j, dict):
        parseError("must be JSON object")
        return False

    # team number
    try:
        team = j["team"]
        print("Team set to {}".format(team))
    except KeyError:
        parseError("could not read team number")
        return False

    # ntmode (optional)
    if "ntmode" in j:
        str = j["ntmode"]
        if str.lower() == "client":
            server = False
        elif str.lower() == "server":
            server = True
        else:
            parseError("could not understand ntmode value '{}'".format(str))

    return True



#Main function
def main():

  # read configuration
  if not readConfig():
      sys.exit(1)

  print("Starting pixy...")

  #Init pixy and change mode to color connected components
  pixy.init ()
  print("Pixy init succeeded")

  pixy.set_lamp(1,0)
  

  pixy.change_prog("color_connected_components")
  print("Pixy change_prog succeeded")
  
  #Define BlockArray which will be used to get a list of objects that the pixy detects
  blocks = BlockArray(100)

  # start NetworkTables
  ntinst = NetworkTablesInstance.getDefault()
  if server:
      print("Setting up NetworkTables server")
      ntinst.startServer()
  elif team == 9999:
      addr = "192.168.4.47"
      print("Connecting to server at {}".format(addr))
      ntinst.startClient(addr)
      ntinst.startDSClient()
  else:
      print("Setting up NetworkTables client for team {}".format(team))
      ntinst.startClientTeam(team)
      ntinst.startDSClient()

  sd = NetworkTables.getTable("SmartDashboard")


  # ntinst.enableVerboseLogging()

  if not (ntinst.isServer()):
    while not (ntinst.isConnected()):
      time.sleep(1)


  fms = ntinst.getTable("FMSInfo")

  redAlliance = fms.getValue("IsRedAlliance", True)

  print ("IsRedAlliance: {}".format(redAlliance))

  targetColor: int = 0

  if redAlliance:
      targetColor = 1 # constants.RED_BALL_SIG
  else:
      targetColor = 2 # constants.BLUE_BALL_SIG


  #Main loop
  while True:

    fms = ntinst.getTable("FMSInfo")

    redAlliance = fms.getValue("IsRedAlliance", True)

    if redAlliance:
      targetColor = 1 # constants.RED_BALL_SIG
    else:
      targetColor = 2 # constants.BLUE_BALL_SIG


    print ("IsRedAlliance: {}".format(redAlliance))

    sd.putNumber("target Color", targetColor)

    print ("TargetColorIs: {}".format(targetColor))
    #Get number of objects that the pixy detcts
    try:
      count = pixy.ccc_get_blocks (100, blocks)
    except:
      print ("pixy returned error, wait 1 sec")
      time.sleep(1)




    targetSignatureCount: int = 0

    

    #If the pixy detects an object...
    if count > 0:

      #Define the closest object
      closestObjectDistance: float = None

      #Loop through each block every frame
      for index in range (0, count):

        #Define block object and signature var
        block = blocks[index]
        aspectRatio = block.m_width / block.m_height
        signature: int = block.m_signature
        print("Index {0}: width={1} height={2} aspectRatio={3}".format(index, block.m_width, block.m_height, aspectRatio) )
        closestObjectDistance: float = 99

        #Map x value from pixy to -1 and 1
        if (aspectRatio < 4):
            distance: float = translate(block.m_x, 0, pixyConstants.WIDTH, -1, 1)
        
            #Check to see if the signture matches
            if(signature == targetColor):
                #Increase the target signature count
                targetSignatureCount += 1

            #Check to see if the distance is closest or if the closest distance has not been assigned
            if(closestObjectDistance == 99 or distance > closestObjectDistance):
                closestObjectDistance = distance
            
      #Print results
      print("Found {0} objects of signture {1}, closest distance: {2}, index {3}".format(targetSignatureCount, targetColor, closestObjectDistance, index))

      sd.putNumber("target offset", closestObjectDistance)




#Returns a percentage that reflects where value falls in between min and max value
def translate(value, oldMin, oldMax, newMin, newMax):
    # Figure out how wide each range is
    oldSpan = oldMax - oldMin
    newSpan = newMax - newMin

    # Convert the left range into a 0-1 range
    valueScaled = (value - oldMin) / oldSpan

    # Convert the 0-1 range into a value in the right range
    return newMin + (valueScaled * newSpan)

  


#Start program
if __name__ == "__main__":
  main()