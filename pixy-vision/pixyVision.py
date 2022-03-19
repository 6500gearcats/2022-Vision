from __future__ import print_function
import pixy 
from ctypes import *
from pixy import *
from constants import *

#Main function
def main():
  print("Starting pixy...")

  #Init pixy and change mode to color connected components
  pixy.init ()
  pixy.change_prog("color_connected_components")

  #Define BlockArray which will be used to get a list of objects that the pixy detects
  blocks = BlockArray(100)

  #Main loop
  while True:

    #Get number of objects that the pixy detcts
    count = pixy.ccc_get_blocks (100, blocks)
    targetSignatureCount: int = 0

    #If the pixy detects an object...
    if count > 0:

      #Define the closest object
      closestObjectDistance: float = None

      #Loop through each block every frame
      for index in range (0, count):

        #Define block object and signature var
        block = blocks[index]
        signature: int = block.m_signature

        #Map x value from pixy to -1 and 1
        distance: float = translate(block.m_x, 0, pixyConstants.WIDTH, -1, 1)

        #Check to see if the signture matches
        if(signature == constants.TEST_BALL_SIG):

          #Increase the target signature count
          targetSignatureCount += 1

          #Check to see if the distance is closest or if the closest distance has not been assigned
          if(closestObjectDistance == None or distance > closestObjectDistance):
            closestObjectDistance = distance
            
      #Print results
      print("Found {0} objects of signture {1}, closest distance: {2}".format(targetSignatureCount, constants.TEST_BALL_SIG, closestObjectDistance))

        

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