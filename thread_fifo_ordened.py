from tools import *

#imports used by sensors group
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

global fifo_datatosend 
fifo_datatosend = Queue.Queue()
global fifo_datafailed
fifo_datafailed = Queue.Queue()

#make sure the log file exists
f=open("/home/pi/Desktop/log.csv",'a')
f.close()

#fifo_datatosend line counter
j=0
#log.csv line counter
k=0

def sendValues():
	global t,h, fifo_datatosend, fifo_datafailed, k
	while True:
	print "thread" 
		
	 #if connection is sucessfull it sends the data directly, 
		try:
			#executes the connection to the database
			db = MySQLdb.connect(host="193.136.175.118", user = "pee", passwd = "pee#pp", db = "pee")
			cur = db.cursor()
			print("Connection successfull")
						#if fifo with data failed to send isn't empty it sends that data first
                        if fifo_datafailed.empty() is False:
                                row = fifo_datafailed.get()
                                col1,col2,col3,col4 = row.split(",")
                                cur.execute("INSERT INTO containerenvironment VALUES(NUll,1,%s,%s,Null,%s)",(col1,col2,col3))
								db.commit()
						#if fifo_datatosend has more lines than log.csv there is information that needs to be sended
						elif k <= j:
                                row = fifo_datatosend.get()
                                col1,col2,col3,col4 = row.split(",")
				cur.execute("INSERT INTO containerenvironment VALUES(NUll,1,%s,%s,Null,%s)",(col1,col2,col3))
				db.commit()                                
				#cur.execute("INSERT INTO containerdoor VALUES(NULL,1,%s,%s)",(col4,col3))
				#db.commit()
				db.close()
				k=k+1                                
			f = open("/home/pi/Desktop/log.csv", 'a')
			f.write(row)
			f.flush()
			f.close()
        #handler: when ther are problems connecting to database
        except MySQLdb.OperationalError:
			print("Connection unsucessfull")		
			fifo_datafailed.put(row)
			sleep(2)
		#handler: when no connection is detected
		except MySQLdb.IntegrityError:
			print("Connection lost")
			fifo_datafailed.put(row)
			sleep(2)
        #handler: assures that "C" key interrupts the code
        except KeyboardInterrupt:
            exit
		
	sleep(3)
	return
#thread inicialization
threads = []
th = threading.Thread(target=sendValues)
threads.append(th)
th.start()	

while True:
  
  	#gets sensors value with a x seconds pause and sends the info to fifo_datatosend
	print "Estou aqui"
	
	t = round(sense.get_temperature(), 1)
	h = round(sense.get_humidity(), 1)
      
	now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	msg = "%.1f,%.1f,%s,%s\n" % (t, h, now, door_closed)
	fifo_datatosend.put(msg)
	j = j+1
	print k
	print j
	sleep(10) #delay(seconds)  
