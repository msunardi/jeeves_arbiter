#!/usr/bin/env python

from arbiter.srv import *
import rospy
from std_msgs.msg import *
from basics.srv import *
import random as r
import subprocess

# nav_say = rospy.Publisher('/jeeves_speech/speech_synthesis', String, queue_size=10)
spiel = rospy.Publisher('/spiel', String, queue_size=10)

prompt = ['Excellent choice .', 'Very good .', 'Certainly .', 'Of course .', 'Right . ', 'Naturally .', 'Indeed .', 'Obviously .', 'Indubitably .', 'Why, of course .', 'Marvelous .', 'Magnificent .']

def festival(say):
    subprocess.call(["festival", "--batch", "(SayText \"" + say + "\")"])

def handler(request):
    print "Getting request: %s - %s - %s" % (request.itype, request.value, request.description)
    itype = request.itype
    val = request.value
    description = request.description
    response = "I don't know what you're asking"

    # Make decisions based on type
    if itype == 'nav':
        response = "Navigation request to: %s" % val
        p = r.choice(prompt)
        msg = r.choice(['Ah, ... ', '']) +  description + ', ...  ' + p
        # nav_say.publish(msg)
        festival(msg)

        spiel.publish(val)

        #rospy.wait_for_service('waypoint')
        #rospy.loginfo("Attempting nav: %s" % val)
        #print response
        #try:
        #    wp = rospy.ServiceProxy('waypoint', Waypoint)
        #    resp = wp(val)
        #    return resp.output
        #except rospy.ServiceException, e:
        #    rospy.logerr("Unable to call service 'waypoint'.")
        #    print "Unable to call service. %s" % e
    elif itype == 'tour':
        response = "Tour request"
    elif itype == 'info':
        response = "Requesting info for: %s" % val
    elif itype == 'play':
        response = "Requesting play behavior"

    # nav_say.publish(response)

    return InteractResponse(response)
    # return InteractResponse("Got foo -- itype: %s - value: %s" % (request.itype, request.value))

def arbiter_server():
    rospy.init_node('arbiter_server')
    s = rospy.Service('arbiter_server', Interact, handler)
    print "Ready to receive interaction messages..."
    rospy.spin()

if __name__ == "__main__":
    arbiter_server()
