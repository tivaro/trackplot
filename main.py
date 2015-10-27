import numpy as np
import pandas as pd
import cv2
from os import listdir
import os.path
from PIL import Image, ExifTags

#MAIN PROGRAM!

class WondCarousel(object):

	def __init__(self):

		#default settings
		self.imgDir    = 'fotos/'
		self.imgExts   = ['.png','.jpg','.jpeg']
		self.dataPath  = 'measurements.csv'
		self.sizeFactor = 2.2
		self.maxRulers = 2
		self.maxwLines = 2
		self.keys = {
				'next':[63235], #>
				'prev':[63234], #< 
				'escape':[27,113], #esc, q
				'ruler+':[61], #+
				'ruler-':[45], #-
				'ignore':[13], #return
		}

		#initialise variables
		self.curImg      = 0
		self.bufferID    = None
		self.bufferPoint = None
		self.rulers		 = []
		self.wLines		 = []

		self.loadData()

		#load images

		#try to load data

		#create for data for images that don't exist


	def loadData(self):

		#load image paths
		imgPaths= [f for f in listdir(self.imgDir) if os.path.isfile(os.path.join(self.imgDir,f)) and os.path.splitext(os.path.join(self.imgDir,f))[1].lower() in self.imgExts ]

		#try to load data from file
		if not hasattr(self, 'data'):
			try:
				self.data = pd.read_csv(self.dataPath)
			except:
				self.data = pd.DataFrame(columns=['imgPath'])

		#add images that do not have a record yet 
		newData = []
		for imgPath in imgPaths:
			img = Image.open(self.imgDir + imgPath)
			#Load META-data and convert datetime 
			exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
			date,time =  exif['DateTime'].split(' ')
			date = date.replace(':','-')
			datetime = date+" "+time

			if not any(self.data.imgPath ==imgPath):
				newData.append({'imgPath':imgPath,
								'datetime':datetime,
								'ignore':0})

		if len(newData) > 0:
			self.data = self.data.append(newData)
			print "Loaded %i new images" % len(newData)

		self.data['datetime'] = pd.to_datetime(self.data['datetime'])
		self.data = self.data.sort('datetime')
		self.data.reset_index()

		self.resetIDlist()


		#load images, and measurement data if it exists yet


	def bufferImage(self,id=None):

		id = id or self.curImg
		if not self.bufferID == id:
			img = cv2.imread(self.imgDir + self.data.imgPath[id])

			#TODO: resize image to fit window
			newx,newy = int(img.shape[1]/self.sizeFactor),int(img.shape[0]/self.sizeFactor) #new size (w,h)
			img = cv2.resize(img,(newx,newy))

			self.bufferImg = img

		return self.bufferImg

	def resetIDlist(self):
		self.IDlist = self.data[self.data.ignore == 0].index.values


	def nextImg(self):
		allowedNext = self.IDlist[self.IDlist > self.curImg]
		#print self.curImg, allowedNext[0:20]
		if len(allowedNext) > 0:
		 	self.curImg = allowedNext[0]
		 	self.renderImage()

	def prevImg(self):
		allowedPrev = self.IDlist[self.IDlist < self.curImg]
		#print self.curImg, allowedPrev[0:20]
		if len(allowedPrev) > 0:
			self.curImg = allowedPrev[-1]
			self.renderImage()

	def ignoreImg(self):
		#self.data.ignore[self.curImg] = 1
		self.data.loc[self.curImg,'ignore'] = 1
		self.resetIDlist()
		self.nextImg()


	def renderImage(self,id=None):

		img = self.bufferImage(id)

		cv2.imshow('image',img)	

	def mouseCallback(self,event, x, y, flags, param):

		c=(1,0,0)

		

		if event == cv2.EVENT_LBUTTONDOWN:
			print self.bufferPoint
			print self.wLines
			print self.rulers

			if self.bufferPoint:
				#finish this line
				if len(self.rulers) < self.maxRulers:
					self.rulers.append((self.bufferPoint,(x,y)))
				elif len(self.wLines) < self.maxwLines:
					self.wLines.append((self.bufferPoint,(x,y)))
				else:
					self.nextImg()
				self.bufferPoint = None



			else:
				self.bufferPoint = (x,y)



		elif self.bufferPoint:
			#a line is being dragged right now
			img = self.bufferImg.copy()
			cv2.line(img, self.bufferPoint, (x,y),c)
			cv2.imshow('image',img)	



	def run(self):
		"""
		Runs the program until it is closed by user!
		"""

		running = True
		#print dir(cv2)
		cv2.namedWindow('image',cv2.WINDOW_AUTOSIZE)
		#print cv2.getWindowProperty('image',cv2.WND_PROP_ASPECT_RATIO)
		#cv2.setWindowProperty('image',cv2.WND_PROP_ASPECT_RATIO,cv2.CV_WINDOW_KEEPRATIO)
		#print cv2.getWindowProperty('image',cv2.WND_PROP_ASPECT_RATIO)
		#cv2.namedWindow('graph',cv2.WINDOW_NORMAL)
		#cv2.namedWindow('controls',cv2.WINDOW_NORMAL)
		cv2.setMouseCallback("image", self.mouseCallback)

		while running:

			self.renderImage()

			#register which key was pressed
			k = cv2.waitKey(0)

			print k

			if k in self.keys['escape']:
				running=False
			elif k in self.keys['next']:
				self.nextImg()
			elif k in self.keys['prev']:
				self.prevImg()
			elif k in self.keys['ignore']:
				self.ignoreImg()
			else:
				pass



def main():
	w = WondCarousel()
	w.run()
	print w.data
	#w.data.to_csv(w.dataPath)
	

if __name__ == '__main__':
	main()

