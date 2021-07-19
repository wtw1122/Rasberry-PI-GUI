
import sys
import RPi.GPIO as GPIO
import time
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import uic
GPIO.setwarnings(False)

led1 = 20
led2 = 21
piezo = 13
Trigger = 0
Echo = 1
servo = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(Trigger, GPIO.OUT)
GPIO.setup(Echo, GPIO.IN)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(piezo, GPIO.OUT)

pwm = GPIO.PWM(piezo, 1.0)
s_pwm = GPIO.PWM(servo, 50)
melody = [262, 294, 330, 349, 392, 440, 494, 523]
note = [4, 4, 5, 5, 4, 4, 2, 4, 4, 2, 2, 1,
		4, 4, 5, 5, 4, 4, 2, 4, 4, 2, 2, 1,
		4, 4, 5, 5, 4, 4, 2, 4, 4, 2, 2, 1]

class Thread(QThread):
	threadEvent = QtCore.pyqtSignal(int)
	def __init__(self, parent = None):
		super().__init__()
		self.n = 0
		self.main = parent
		self.isRun = False
	def run(self):
		while self.isRun:
			pwm.start(50.0)
			pwm.ChangeFrequency(melody[note[self.n]])
			time.sleep(0.5)
			self.n += 1
			if self.n >= 36:
				self.isRun = False
				pwm.stop()
				self.n = 0

class Thread1(QThread):
	threadEvent1 = QtCore.pyqtSignal(int)
	def __init__(self, parent = None):
		super().__init__()
		self.distance = 0
		self.main = parent
		self.isRun = False

	def run(self):
		while self.isRun:
			self.distance = self.measure()
			self.threadEvent1.emit(self.distance)
			time.sleep(1)

	def measure(self):
		GPIO.output(Trigger, True)
		time.sleep(0.0001)
		GPIO.output(Trigger, False)
		start = time.time()

		while GPIO.input(Echo) == False:
			start = time.time()
		while GPIO.input(Echo) == True:
			stop = time.time()
		elapsed = stop - start
		distance = (elapsed * 19000) /2
		return distance

class myWindow(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.ui = uic.loadUi("PROJECT.ui", self)
		self.ui.show()

		self.th = Thread(self)
		self.th.daemon = True
		self.th.threadEvent.connect(self.threadEventHandler)
		self.th1 = Thread1(self)
		self.th1.daemon = True
		self.th1.threadEvent1.connect(self.threadEventHandler1)

	def slot_LED1_ON(self):
		self.ui.label_3.setText("LED1 ON")
		GPIO.output(led1, True)
	def slot_LED1_OFF(self):
		self.ui.label_3.setText("LED1 OFF")
		GPIO.output(led1, False)
	def slot_LED2_ON(self):
		self.ui.label_3.setText("LED2 ON")
		GPIO.output(led2, True)
	def slot_LED2_OFF(self):
		self.ui.label_3.setText("LED2 OFF")
		GPIO.output(led2, False)

	def slot_Melody(self):
		if not self.th.isRun:
			self.th.isRun = True
			self.th.start()

	def slot_stop(self):
		if self.th.isRun:
			self.th.isRun = False
			pwm.stop()

	def slot_ultra(self):
		if not self.th1.isRun:
			self.th1.isRun = True
			self.th1.start()

	def slot_stop2(self):
	 	if self.th1.isRun:
	 		self.th1.isRun = False

	def threadEventHandler(self, n):
		pass
	def threadEventHandler1(self, distance):
		self.ui.label_2.setText("distance: %.2f cm" %distance)

	def slot_diar(self):
		diar = self.ui.lcdNumber.value()
		s_pwm.start(3.0)
		s_pwm.ChangeDutyCycle(diar / 18.0)
		time.sleep(0.01)

	def slot_exit(self):
		print("exit")
		GPIO.cleanup()
		sys.exit()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	myapp = myWindow()
	app.exec_()
