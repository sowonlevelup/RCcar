import sys
sys.path.append('./Raspi-MotorHAT-python3')
from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtSql
import time
import atexit

from sense_emu import SenseHat
from time import sleep

sense = SenseHat()

class pollingThread(QThread):
 def __init__(self):
     super().__init__()
 
 def run(self): 
    self.db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
    self.db.setHostName("3.34.192.207") 
    self.db.setDatabaseName("1-4")
    self.db.setUserName("ssafy1_8")
    self.db.setPassword("ssafy1234")
    ok = self.db.open()
    print(ok) 
    
    self.mh = Raspi_MotorHAT(addr=0x6f )
    self.myMotor = self.mh.getMotor(2)
    self.myMotor.setSpeed(100)
 
    self.pwm = PWM(0x6F)
    self.pwm.setPWMFreq(60)
    while True:
      time.sleep(1)
      self.getQuery()
      self.setQuery()
 
 
 def setQuery(self):
    pressure = sense.get_pressure()
    temp = sense.get_temperature()
    humidity = sense.get_humidity()

    p = round((pressure - 1000) / 100, 3)
    t = round(temp / 100, 3)
    h = round(humidity / 100, 3)

    msg = "Press : " + str(p) + "  Temp : " + str(t) + "  Humid : " + str(h)
    print(msg)
    self.query = QtSql.QSqlQuery();
    self.query.prepare("insert into sensing1_8 (time, num1, num2, num3, meta_string, is_finish) values (:time, :num1, :num2, :num3, :meta, :finish)");
    time = QDateTime().currentDateTime()
    self.query.bindValue(":time", time)
    self.query.bindValue(":num1", p)
    self.query.bindValue(":num2", t)
    self.query.bindValue(":num3", h)
    self.query.bindValue(":meta", "")
    self.query.bindValue(":finish", 0)
    self.query.exec()

    a = int((p * 1271) % 256)
    b = int((t * 1271) % 256)
    c = int((h * 1271) % 256)
    sense.clear(a, b, c)
 
 def getQuery(self):
      time.sleep(0.5)
      query = QtSql.QSqlQuery("select * from command1_8 order by time desc limit 1");
      query.next()
      cmdTime = query.record().value(0)
      cmdType = query.record().value(1)
      cmdArg = query.record().value(2)
      is_finish = query.record().value(3)
 
      if is_finish == 0 : 
       #detect new command
         print(cmdTime.toString(), cmdType, cmdArg)
 
         #update
         query = QtSql.QSqlQuery("update command1_8 set is_finish=1 where is_finish=0");
         #motor 
         if cmdType == "go": self.go() 
         if cmdType == "back": self.back()
         if cmdType == "left": self.left()
         if cmdType == "right": self.right()
         if cmdType == "mid": self.middle()
         if cmdType == "front" and cmdArg == "press" : 
           self.go()
           self.middle()
         if cmdType == "leftside" and cmdArg == "press" : 
           self.go()
           self.left()
         if cmdType == "rightside" and cmdArg == "press" : 
           self.go()
           self.right()
         
         if cmdType == "front" and cmdArg == "release" : self.stop()
         if cmdType == "leftside" and cmdArg == "release" : self.stop()
         if cmdType == "rightside" and cmdArg == "release" : self.stop()
 
 def stop(self):
   print("MOTOR STOP")
   self.myMotor.run(Raspi_MotorHAT.RELEASE)
 def go(self):
   print("MOTOR GO")
   self.myMotor.setSpeed(50)
   self.myMotor.run(Raspi_MotorHAT.FORWARD)
 
 def back(self):
   print("MOTOR BACK")
   self.myMotor.setSpeed(50)
   self.myMotor.run(Raspi_MotorHAT.BACKWARD)
   
 def left(self):
   print("MOTOR LEFT")
   self.pwm.setPWM(0, 0, 150);

 def right(self):
   print("MOTOR RIGHT")
   self.pwm.setPWM(0, 0, 400);

 def middle(self ):
   print("MOTOR MIDDLE")
   self.pwm.setPWM(0, 0, 350);


   
th = pollingThread()
th.start()
app = QApplication([])

#infinity loop
while True: 
 pass
