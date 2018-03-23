#!/bin/python2.7
# getyourbots.com

import cv2
import os
import numpy as np
import inspect
from PIL import Image, ImageOps, ImageEnhance
from random import choice, randint
from string import letters, digits
from shutil import rmtree, copyfile
from sys import exit
import pytesseract

# Nimbus Sans

class TextRecognizer:
	def __init__(self, image_path):
		if not os.path.exists(image_path):
			raise Exception('Image: ' + image_path + ' does not exist.')
		
		self.text = ''
		self.image_path = image_path
	
	# pre-process text
	def preprocess_text(self, text):
		text = text.lower().replace(' ','')
		return text
	
	# get real test
	def get_text(self):
		text = pytesseract.image_to_string(Image.open(self.image_path), lang='eng')
		text = self.preprocess_text(text)
		
		self.text = text
		return self.text

class Extra:
	# sort list by key
	@staticmethod
	def my_sorted(in_list, key=lambda x:x):
		if not inspect.isroutine(key):
			raise ValueError("key must be a function/method")
	
		# convert to [ (key(item1), item1), .... ]
		key_map = map(lambda x: (key(x),x), in_list)
		# standard sort, while effectively sort by key(item)
		key_map.sort()
	
		# convert back original format and return
		return [x for _,x in key_map]
	
	# add element to list in "own" way
	@staticmethod
	def add_to_list(l, e):
		new_l = l
		
		if len(l) == 0:
			new_l.append([e])
			return new_l
		
		inserted = False
		for i in l:
			if i[-1] + 80 >= e:
				i.append(e)
				i.sort()
				inserted = True
				break
		
		if not inserted:
			new_l.append([e])
		
		
		return new_l
		
	# returns a random digits + letters string
	@staticmethod
	def random_string(digit_len=8, letters_len=15):
		digs = ''.join([choice(digits) for i in xrange(digit_len)] )
		chars = ''.join([choice(letters) for i in xrange(letters_len)] )
		return digs + chars
	
	# check if string contains only letters
	@staticmethod
	def is_alpha(s):
		for e in list(s):
			if not e.isalpha():
				return False
		return True
	

class CenterRepo:
	# init
	def __init__(self, points):
		self.points = points
		self.ordered_points = []
	
	# sort the points, and set the order
	def sort_points(self):
		l = []
		x_list = []
		for p in self.points:
			x_list.append(p['x'])
		
		x_list.sort()
		
		for x in x_list:
			exists = False
			if len(l) != 0:
				for e in l:
					if x in e:
						exists = True
						break
			
			if exists:
				continue
			
			l = Extra.add_to_list(l, x)
		
		
		self.ordered_points = l	
	
	# in case we have too less circles, retry
	def wrong_length(self):
		if len(self.ordered_points) >= 5:
			return False
		else:
			return True
	
	# return the real circles
	def get_centers(self):		
		centers = []
		l = Extra.my_sorted(self.ordered_points, key=len)
		l.reverse()
		for e in l:
			if len(centers) == 5:
				break
			last_e = e[-1]
			first_e = e[0]
			middle = int((last_e - first_e) / 2)
			#print 'fe:' + str(first_e)
			#print 'le: ' + str(last_e)
			#print 'mid: ' + str(first_e + middle)
			#a = raw_input('get centers')
			centers.append(first_e + middle)			
		
		return centers

class PofCaptcha:
	def __init__(self, image_path):
		if not os.path.exists(image_path):
			raise Exception('Image: ' + image_path + ' does not exist.')
		
		# set all the paths		
		self.old_working_directory = os.getcwd()
		self.temp_folder = os.path.join(self.old_working_directory, 'tmp')
		if not os.path.exists(self.temp_folder):
			try:
				os.makedirs(self.temp_folder)
			except:
				raise Exception('Cannot create /tmp folder. Set the right permissions to the script, or create it manually.')
		
		self.working_directory = os.path.join(self.temp_folder, Extra.random_string())
		self.image_filename = os.path.join(self.working_directory, 'captcha.jpe')
		
		self.set_directory()
		
		# os.rename
		copyfile(image_path, self.image_filename)
		s = self.image_filename.split('.')
		
		# and more paths ...
		self.temp_file = ''.join(s[:-1]) + '_temp.' + s[-1]
		self.order_file = ''.join(s[:-1]) + '_order.' + s[-1]
		self.text_file = ''.join(s[:-1]) + '_text.' + s[-1]
		
		# init  variables
		self.centers = []
		self.order = []
		for x in range(0,10):
			self.order.append(False)
		self.text = ''
		self.real_text = ''
		self.max_get_order_retries = 5	
	
	# gets a temporary jpe file
	def get_temp_file(self):
		return os.path.join(self.working_directory, 'temp.jpe')
	
	# Crop image, need one for order check and one for text check
	def crop(self):
		with open(self.image_filename, 'rb') as f:
			im = Image.open(f)
			w, h = im.size
			im.crop((0, 0, w, h-38)).save(self.order_file)
			im.crop((0, 12, w, h)).save(self.text_file)
	
	# resize image
	def resize(self, input_file, w=1200, h=90):
		tmp = self.get_temp_file()
		with open(input_file, 'rb') as f:
			im = Image.open(f)
			img = ImageOps.fit(im, (w, h), Image.ANTIALIAS)
			img.save(tmp, 'JPEG')
		
		os.remove(input_file)
		os.rename(tmp, input_file)
	
	# optimize colors
	def optimize_colors(self, input_file, sharpness=0.1):
		tmp = self.get_temp_file()
		image = Image.open(input_file)
		enhancer = ImageEnhance.Sharpness(image)
		image2 = enhancer.enhance(sharpness)
		image2.save(tmp)
		os.remove(input_file)
		os.rename(tmp, input_file)

	# optimize contrast
	def optimize_contrast(self, input_file, contrast=0.5):
		tmp = self.get_temp_file()
		image = Image.open(input_file)
		enhancer = ImageEnhance.Contrast(image)
		image2 = enhancer.enhance(contrast)
		image2.save(tmp)
		os.remove(input_file)
		os.rename(tmp, input_file)
		
	# working directory = random string
	def set_directory(self):
		while os.path.exists(self.working_directory):
			self.working_directory = os.path.join(self.temp_folder, Extra.random_string())
		
		os.makedirs(self.working_directory)
		os.chdir(self.working_directory)
	
	# working directory = old working directory
	# remove(temp)
	def clean(self):
		os.chdir(self.old_working_directory)
		rmtree(self.working_directory)
	
	# replace lines to get better circles
	def replace_lines(self, line_weight=10):
		tmp = self.get_temp_file()
		img = cv2.imread(self.order_file)
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(gray,50,150,apertureSize = 3)
		lines = cv2.HoughLinesP(edges,1,np.pi/180,275, minLineLength = 600, maxLineGap = 100)[0].tolist()

		for x1,y1,x2,y2 in lines:
			for index, (x3,y3,x4,y4) in enumerate(lines):
	
				if y1==y2 and y3==y4: # Horizontal Lines
					diff = abs(y1-y3)
				elif x1==x2 and x3==x4: # Vertical Lines
					del lines[index]
					continue
				else:
					diff = 0
	
				if diff < 10 and diff is not 0:
					del lines[index]
			
		for x1,y1,x2,y2 in lines:        
			cv2.line(img,(x1,y1),(x2,y2),(210,210,210),line_weight)
		
		#cv2.imshow('detected circles',img)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()
		cv2.imwrite(tmp,img)
		os.rename(tmp, self.order_file)		
	
	# get order of circles
	# recursively increase by 0.02
	def set_centers(self, extra_param=1.29, retry=0):
		if retry == self.max_get_order_retries:
			raise Exception('Too many retries for getting captcha order')
			
		# will keep track of found circles (first stage)
		points = []
		img = cv2.imread(self.order_file,0)
		
		cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
		
		circles = cv2.HoughCircles(img,3,extra_param,1,param1=40,param2=35,minRadius=10,maxRadius=70)
		
		
		circles = np.uint16(np.around(circles))
		for i in circles[0,:]:
			x = i[0]
			y = i[1]
			#print i
			# draw the outer circle
			cv2.circle(cimg,(x, y),i[2],(0,255,0),2)
			# draw the center of the circle
			cv2.circle(cimg,(x, y),5,(0,0,255),3)
			center = {}
			center['x'] = x
			center['y'] = y
			
			points.append(center)
		
		
		center_repo = CenterRepo(points)
		center_repo.sort_points()
		if center_repo.wrong_length():
			print 'get order retry ' + str(retry + 1)
			self.set_centers(extra_param + 0.02, retry + 1)
			return
		
		self.centers = center_repo.get_centers()
		self.centers.sort()
		
		#cv2.imshow('detected circles',cimg)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()
		#cv2.imwrite(os.path.join(self.working_directory, 'circles.jpe'),cimg)
		#exit(0)
		
	
	# set the real order
	# this will be used for taking only the text under the circle
	# as POF is expecting it
	def set_real_order(self):
		for e in self.centers:
			if e >= 40 and e < 151:
				self.order[0] = True
			elif e >= 151 and e < 256:
				self.order[1] = True
			elif e >= 256 and e < 370:
				self.order[2] = True
			elif e >= 370 and e < 490:
				self.order[3] = True
			elif e >= 490 and e < 610:
				self.order[4] = True
			elif e >= 610 and e < 720:
				self.order[5] = True
			elif e >= 720 and e < 842:
				self.order[6] = True
			elif e >= 842 and e < 962:
				self.order[7] = True
			elif e >= 962 and e < 1080:
				self.order[8] = True
			elif e >=1080  and e <= 1180:
				self.order[9] = True
			elif e < 40:
				self.order[0] = True
			elif e > 1180:
				self.order[9] = True
	
	# This will return empty string
	# if used before using get_result method
	# get the text (not filtered by circles)
	def get_text(self):
		return self.text
	# get the order
	def get_order(self):
		return self.order
	# get real text
	def get_real_text(self):
		return self.real_text
	
	# set text
	def set_text(self):
		text_reco = TextRecognizer(self.text_file)
		self.text = text_reco.get_text()
		print self.text
		if len(self.text) != 10:
			raise Exception('The text doesn\'t have the right length.')
		
	# compute the real text
	def compute_real_text(self):
		l = list(self.text)
		for i in range(0, len(self.order)):
			if self.order[i]:
				self.real_text += str(l[i])
		
	
	# return a string, the correct captcha for POF
	def get_result(self):
		
		# set stuff ready for getting the order
		try:
			self.crop()
			self.resize(self.order_file)
			self.optimize_colors(self.order_file)
			self.optimize_contrast(self.order_file)
			self.replace_lines()
			self.optimize_colors(self.order_file)
			self.optimize_contrast(self.order_file)
		except Exception, e:
			self.clean()
			raise Exception(e)
		
		# get the real order
		try:
			self.set_centers()
			self.set_real_order()
		except Exception, e:
			self.clean()
			raise Exception(e)
		
		# get text from image
		try:
			self.resize(self.text_file, 310, 76)
			self.optimize_contrast(self.text_file, 2)
			self.optimize_colors(self.text_file)
			self.set_text()
		except Exception, e:
			self.clean()
			raise Exception(e)
		
		
		# set the last real text, finally!
		try:
			self.compute_real_text()
		except Exception, e:
			self.clean()
			raise Exception(e)
		
		
		self.clean()
		return self.real_text