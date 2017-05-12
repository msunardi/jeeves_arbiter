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
             'near_lab': 'NEAR LAB', \
             'robot_lab': 'ROBOTICS LAB', \
             'Biomedical_lab': 'BIOMEDICAL SIGNAL LAB', \
             'biomedical_lab': 'BIOMEDICAL SIGNAL LAB', \
             'stairs': 'EB STAIRS', \
             'portland_state': 'PORTLAND STATE', \
             'portland_state_university': 'PORTLAND STATE'}

facts_or_jokes = ['FACTS', 'JOKES']

sub = rospy.Subscriber('chatter', String, queue_size=10)
say = rospy.Publisher('/jeeves_speech/speech_synthesis', String, queue_size=10)

spiel = True
place = ''
arrived = False
speaking = False
stop_all = False

collect = 10

def callback(message):
    global place, spiel, arrived, stop_all
    # topic = "PORTLAND STATE"
    # topic = "INTEL LAB"
    topic = locations[message.data]
    place = topic
    count = 2
    arrived = False
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
            factjoke = r.choice(facts_or_jokes)
            rx = jeeves.respond(factjoke)
            if rx not in rcvd:
                rx = r.choice(comment[factjoke]) + '. ' + rx + '. ' + r.choice(comment['CLOSING'][factjoke])
                rcvd.append(rx)
                print rx
    rcvd.append('And that is all I can say about %s %s. %s' % (topic, r.choice(['for now', '']), r.choice(comment['CLOSING']['END'])))
        
    for msg in rcvd:
        if not spiel:
            spiel = True
            msg = "OK. I'll stop."
            festival(msg)
            break
        try:
            while speaking:
                pass
            festival(msg)
        except Exception as e:
            print e
        finally:
            sl = r.random()*0.5
            print "I'm done - sleeping for %s" % sl        
            time.sleep(sl)
    else:
        spiel = False
    print "Arrived: %s" % arrived
    while not arrived and not spiel:
        try:
            if arrived or stop_all:
                spiel = True
                msg = "OK. I'll stop."
                festival(msg)
                stop_all = False
                break
            factjoke = r.choice(facts_or_jokes)
            rx = jeeves.respond(factjoke)
            rx = r.choice(comment[factjoke]) + '. ' + rx + '. ' + r.choice(comment['CLOSING'][factjoke])
            
            while speaking and not arrived:
                pass
            if arrived and r.random() < 0.3:
                break      
            festival(rx)
        except Exception as e:
            print e
        finally:
            sl = r.random()*3.0
            print "Not arrived yet - sleeping for %s" % sl        
            time.sleep(sl)
    arrived = False
    spiel = True
    stop_all = False

def done(message):
    global spiel, stop_all
    if message.data == "no":
        spiel = True
        arrived = False
        stop_all = False
    else:
        spiel = False
        stop_all = True

def goal_reached(message):
    global place, arrived, spiel, speaking
    print "Arrived: %s" % arrived
    if 'Goal reached' in message.data and not arrived:
        arrive = ['We have reached %s.', 'Well, here we are . . . %s', 'Welcome to the %s . . . ', 'This is the %s . . . ']
        msg = r.choice(arrive) % place
        while speaking or spiel:
            pass
        festival(msg)
        arrived = True
        print "Yes Arrived: %s" % arrived


def festival(say):
    global speaking
    speaking = True
    subprocess.call(["festival", "--batch", "(SayText \"" + say + "\")"])
    speaking = False 

def nav_spiel():
    rospy.init_node('nav_spiel', anonymous=True)
    rospy.Subscriber("/spiel", String, callback)
    rospy.Subscriber("/done", String, done)
    rospy.Subscriber("/move_base/result", String, goal_reached)
    # rospy.Subscriber("/move_base/result", MoveBaseAction, goal_reached)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
   
if __name__ == '__main__':
    try:
        nav_spiel()
    except rospy.ROSInterruptException:
        pass