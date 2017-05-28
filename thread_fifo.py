from tools import *

import threading
import RPi.GPIO as GPIO 
from time import sleep, strftime, time, gmtime

#imports used by communications group
import os
import MySQLdb
import csv
from datetime import datetime
import Queue

global door_closed
global j
global k

door_closed = 1

white = (255, 255, 255)
black = (0, 0, 0)

sense = SenseHat()

sense.set_pixels([white for i in range(64)])

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#closed = 1
#open = 2
#door_status interruption
def door(channel): 
	global door_closed 
	if GPIO.input(12):
		door_closed = 1
		sense.set_pixels([white for i in range(64)])
	else:
		door_closed = 2
		sense.set_pixels([black for i in range(64)])




GPIO.add_event_detect(12, GPIO.BOTH, callback=door,bouncetime = 300)

global fifo
fifo = Queue.Queue()

f=open("/home/pi/Desktop/log.csv",'a')
f.close()


j=0
k=0

def sendValues():
	global t,h, fifo, k
	while True:
		print "thread" 
		row = fifo.get()
		col1,col2,col3,col4 = row.split(",")
	 #if connection is sucessfull it sends the data directly, if not (error catched) it saves it to the file log.csv  
		try:
			#executes the connection to the database
			db = MySQLdb.connect(host="192.168.43.119", user = "teste", passwd = "teste", db = "db_pee")
			cur = db.cursor()
			print("Connection successfull")
			if k <= j:
				cur.execute("INSERT INTO containerenvironment VALUES(NUll,1,%s,%s,%s)",(col1,col2,col3))
				db.commit()
				#cur.execute("INSERT INTO containerdoor VALUES(NULL,1,%s,%s)",(col4,col3))
				#db.commit()
				db.close()
				k=k+1
				f = open("/home/pi/Desktop/log.csv", 'a')
				f.write(row)
				f.flush()
				f.close()
                except MySQLdb.OperationalError:
			print("Connection unsucessfull")		
			fifo.put(row)
			sleep(2)
		except MySQLdb.IntegrityError:
			print("Connection lost")
			fifo.put(row)
			sleep(2)
                except KeyboardInterrupt:
                        exit
		
	sleep(3)
	return

threads = []
th = threading.Thread(target=sendValues)
threads.append(th)
th.start()	
	




while True:
  
  #gets sensors value
	
	
	
	print "Estou aqui"
	
	t = round(sense.get_temperature(), 1)
	h = round(sense.get_humidity(), 1)
   
   
	now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	msg = "%.1f,%.1f,%s,%s\n" % (t, h, now, door_closed)
	fifo.put(msg)
	j = j+1
	print k
	print j
	sleep(10) #delay(seconds)  
