import numpy as np
import cv2
import sys
import random
import argparse
import os

"""
TODO:
Progress bar
Option to name output
"""

# Randomly samples pixels from a sliding window
def average_sampling(img, step):
	channels = [0,0,0]

	for x in range(0, img.shape[0]-step, step):
		for y in range(0, img.shape[1]-step, step):
			for i in range(0,3):
				channels[i] += img[x+random.randint(0,step-1), y+random.randint(0,step-1)][i]

	total = (img.shape[0]*img.shape[1]) / (step**2)

	for i in range(0,3):
		channels[i] /= total

	return channels

# Average of every pixel
def average_regular(img):
	channels = [0,0,0]

	for x in range(0, img.shape[0]):
		for y in range(0, img.shape[1]):
			for i in range(0,3):
				channels[i] += img[x,y][i]

	total = (img.shape[0]*img.shape[1])

	for i in range(0,3):
		channels[i] /= total

	return channels

def vignette(color, height, current):
	if current < height*.20:
		return color*(current/(height*.20))
	elif current > height*.80:
		return color-color*(current-height*.80)/(height*.20)
	else:
		return color

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate movie barcodes.')
	parser.add_argument('filename', help='Input file name.')
	parser.add_argument('--no-sampling', help='Disable random sampling when calculating average color.',
						action='store_true')
	parser.add_argument('--interval', help='Number of frames skipped after calculating a column.',
						type=int, default=5)
	parser.add_argument('--width', help='Width of output image', type=int, default=1920)
	parser.add_argument('--height', help='Height of output image', type=int, default=1080)
	#parser.add_argument('--vignetting', help='Adds vignetting to output image', default=True)
	args = parser.parse_args()

	width = args.width
	height = args.height

	# Get frames from video
	cap = cv2.VideoCapture(args.filename)
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	fps = cap.get(cv2.CAP_PROP_FPS)
	interval = args.interval

	result = np.zeros((height,length,3))
	frame = 0
	success = True

	while success:
		cap.set(1, frame)
		success, img = cap.read()

		if not success:
			break

		if args.no_sampling:
			avg = average_regular(img)
		else:
			avg = average_sampling(img,50)

		for i in range(0, height):
			for j in range(0,3):
				if frame+interval > length:
					for k in range(frame, length):
						result[i,k,j] = avg[j]
				else:
					for k in range(frame,frame+interval):
						result[i,k,j] = avg[j]
		print('{} / {}'.format(frame, length))

		frame += interval

	result = cv2.resize(result, (width, height), cv2.INTER_CUBIC)
	cv2.imwrite('{}.png'.format(os.path.splitext(args.filename)[0]), result)