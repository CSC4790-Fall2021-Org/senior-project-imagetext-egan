#Main driver of the program
#Determines if program to be run in cmd or on web server
import sys

#Assume by default that it runs in cmd

if len(sys.argv) > 1 and sys.argv[1] == "web":
    import FlaskLayer
    FlaskLayer.runServer()
else:
    import InputLayer
    InputLayer.cmdDriver()
