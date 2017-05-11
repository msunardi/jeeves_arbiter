#!/usr/bin/env python

import sys, os, time, json, string
import rospy
import aiml                               # Artificial Intelligence Markup Language
from std_msgs.msg import String
import random as r
import time
import subprocess
import rospkg

rospack = rospkg.RosPack()

# Set current working directory
cwd = os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/../');
cwd = os.getcwd() + '/';

jeeves = aiml.Kernel()
jeeves.learn(cwd + "jeeves.xml")
jeeves.respond('load aiml b') #finished initializing

locations = {'ee': 'EE FISHBOWL', \
             'NEAR_lab': 'NEAR LAB', \
             'robot_lab': 'ROBOTICS LAB', \
             'Biomedical_lab': 'BIOMEDICAL LAB', \
             'stairs': 'EB STAIRS', \
             'portland_state': 'PORTLAND STATE'}

sub = rospy.Subscriber('chatter', String, queue_size=10)
say = rospy.Publisher('/jeeves_speech/speech_synthesis', String, queue_size=10)

spiel = True

collect = 10

def callback(message):
    global spiel
    # topic = "PORTLAND STATE"
    # topic = "INTEL LAB"
    topic = locations[message.data]
    count = 3
    rcvd = []   # Container for spiel

    jk_prob = 0.05
    jk_prob = 0.2
    comment = {'FACTS': ['By the way, did you know . . .', 'It reminds me . . .', 'Here is a little trivia . . .'],
            'JOKES': ['Funny story ...', 'This is a true story ...'],
            'CLOSING': {'FACTS': ['. . . Interesting, isn\'t it?', '. . . Fascinating', '. . . Remarkable', 'Fascinating, no?', ''],
                        'JOKES': ['. . Ha ha ha', 'Get it? . . Heh Heh.', '. . . Heh heh heh.', ''],
                        'END': ['Thank you for your attention.', 'I hope you enjoyed it.', 'Let me know if there is anything else I can do for you.']}}
    fj_count = 0
    for i in range(count):
        rsp = jeeves.respond(topic)

        # If don't know, abort
        if not rsp:
            rcvd.append('I am sorry, but I do not know much about %s yet. ' % topic)
            break
        
        # Collect info
        if rsp not in rcvd:
            rcvd.append(rsp)
            print rsp
            
        # Insert random joke/fact
        ran = r.random()
        if ran < jk_prob:
            factjoke = r.choice(['FACTS', 'JOKES'])
            rx = jeeves.respond(factjoke)
            if rx not in rcvd:
                rx = r.choice(comment[factjoke]) + '. ' + rx + '. ' + r.choice(comment['CLOSING'][factjoke])
                rcvd.append(rx)
                print rx
    rcvd.append('And that is all I can say about %s. %s' % (topic, r.choice(comment['CLOSING']['END'])))
        
    for msg in rcvd:
        if not spiel:
            spiel = True
            msg = "OK. I'll stop."
            festival(msg)
            break
        try:
            festival(msg)
        except Exception as e:
            print e
        finally:
            sl = r.random()*0.5
            print "I'm done - sleeping for %s" % sl        
            time.sleep(sl)

def festival(say):
    subprocess.call(["festival", "--batch", "(SayText \"" + say + "\")"])   

def done(message):
    global spiel
    if message.data == "no":
        spiel = True
    else:
        spiel = False

def nav_spiel():
    rospy.init_node('nav_spiel', anonymous=True)
    rospy.Subscriber("/spiel", String, callback)
    rospy.Subscriber("/done", String, done)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
   
if __name__ == '__main__':
    try:
        nav_spiel()
    except rospy.ROSInterruptException:
        pass