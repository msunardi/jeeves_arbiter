#!/usr/bin/env python

import sys
import rospy
from arbiter.srv import *

def arbiter_client(req_itype, req_value):
    rospy.wait_for_service('arbiter_server')
    try:
        foo = rospy.ServiceProxy('arbiter_server', Interact)
        resp = foo(req_itype, req_value)
        return resp.response
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e
        rospy.logerr("Service call failed: %s" % e)

def usage():
    return "%s [type] [value]" % sys.argv[0]

if __name__ == "__main__":
    if len(sys.argv) == 3:
        itype = str(sys.argv[1])
        value = str(sys.argv[2])
    else:
        print usage()
        sys.exit(1)
    print "Requesting {Type: %s, Value: %s}" % (itype, value)
    print "Response: %s" % arbiter_client(itype, value)
