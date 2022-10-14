from datetime import date
import numpy as np
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
import pyautogui
import PIL
import re
import time
from dateutil import parser

SCREEN_WIDTH = 1680
SCREEN_HEIGHT = 1050
NATIVE_SCREEN_WIDTH = None
NATIVE_SCREEN_HEIGHT = None

PTP_THRESH = 40
SUM_THRESH = 160

def screenshot(roi=None):
	s = cv2.cvtColor(np.array(pyautogui.screenshot().convert("RGB")), cv2.COLOR_RGB2BGR)
	if roi is None:
		return s
	x1, y1, x2, y2 = roi
	return s[y1:y2,x1:x2]

def display_roi(img, roi, color=(255, 0, 0), thickness=1):
	disp = img.copy()
	x1, y1, x2, y2 = roi
	disp = cv2.rectangle(disp, (x1, y1), (x2, y2), color, thickness)
	cv2.imshow("ROI", disp)
	cv2.waitKey(0)

def set_screen_scale():
	global NATIVE_SCREEN_WIDTH, NATIVE_SCREEN_HEIGHT
	NATIVE_SCREEN_HEIGHT, NATIVE_SCREEN_WIDTH, _ = screenshot().shape

# Scale roi to fit actual screenshot dimensions
def screen_scale(locs, reverse=False):
	if NATIVE_SCREEN_WIDTH is None:
		set_screen_scale()
	factor = (SCREEN_WIDTH / NATIVE_SCREEN_WIDTH) if reverse else (NATIVE_SCREEN_WIDTH / SCREEN_WIDTH)
	if(type(locs) is int):
		return int(locs * factor)
	else:
		return tuple([int(loc * factor) for loc in locs])

def scale_img(img, scaling_factor):
	height, width = img.shape[:2]
	return cv2.resize(img, (int(width * scaling_factor), int(height * scaling_factor)), interpolation = cv2.INTER_AREA)

def get_selection_yrange(img, x, y1, y2, target_px):
	close = [np.allclose(px, target_px, atol=10, rtol=0) for px in img[y1:y2,x]]
	start, end = np.where(close)[0][[0, -1]]
	return y1+start, y1+end

def run_tesseract(img, roi, min_conf, scaling_factor=1.0, blur_size=0, disp=False):
	if roi is None:
		roi = (0, 0, img.shape[1], img.shape[0])
	x1, y1, x2, y2 = roi

	img_cropped = img[y1:y2,x1:x2]
	
	if scaling_factor != 1.0:
		img_cropped = scale_img(img_cropped, scaling_factor)

	if(blur_size > 0):
		img_cropped = cv2.blur(img_cropped, (blur_size,blur_size))

	if(disp):
		cv2.imshow("tesseract input", img_cropped)
		cv2.waitKey(0)

	results = pytesseract.image_to_data(img_cropped, output_type=pytesseract.Output.DICT)
	# filter out weak confidence text localizations
	filtered = {}
	for i in range(len(results["text"])):
		if(int(results["conf"][i]) >= min_conf):
			for key in results.keys():
				if key not in filtered.keys():
					filtered[key] = []
				
				if(key == "left"):
					filtered[key].append(results[key][i] + roi[0])
				elif(key == "top"):
					filtered[key].append(results[key][i] + roi[1])
				else:
					filtered[key].append(results[key][i])
	return filtered

def process_dropdown_text(text):
	return " ".join(text).lower()

def midpoint(roi):
	x1, y1, x2, y2 = roi
	return (int((x1 + x2) / 2.0), int((y1 + y2) / 2.0))

def parse_onh_score(text):
	regexp = re.compile("\(\d{1,2}\)")
	return int(re.search(regexp, text).group()[1:-1])

def interact_dropdown(dropdown, image_type):
	x1, base_y = dropdown['loc']
	x2 = x1 + dropdown['width']
	done = False
	counter = 0
	max_score = -1
	target_onh_option_num = None
	num_onhs = 0
	dropdown_options = []

	while not done:
		if counter >= dropdown['num_visible_options']:
			pyautogui.click(dropdown['down_button'])
			time.sleep(0.1)

		y1 = int(base_y + min(counter, dropdown['num_visible_options'] - 1)*dropdown['option_height'])
		y2 = int(y1 + dropdown['option_height'])
		current_option_roi = (x1, y1, x2, y2)

		s = screenshot()

		results = run_tesseract(s, current_option_roi, 10)
		text = process_dropdown_text(results['text'])
		dropdown_options.append(text)

		# if text[0:3] == "onh":
		# 	score = parse_onh_score(text)
		# 	if(score > max_score):
		# 		target_onh_option_num = counter
		# 		max_score = score

		# 	num_onhs += 1

		done = np.all([np.allclose(px, dropdown['empty_color'], atol=10, rtol=0) for px in s[y2+dropdown['sample_margin_y']][x1:x1+30]])
		
		#failsafe
		if(counter > dropdown['max_options']):
			break
		
		counter += 1
	
	# if(len(dropdown_options) <= dropdown['num_visible_options']):
	# 	y1 = int(base_y + target_onh_option_num*dropdown['option_height'])
	# 	y2 = int(y1 + dropdown['option_height'])
	# else:
	# 	for _ in range((len(dropdown_options) - dropdown['num_visible_options']) - target_onh_option_num):
	# 		pyautogui.click(dropdown['up_button'])
	# 		time.sleep(0.1)
	# 	y1 = int(base_y)
	# 	y2 = int(y1 + dropdown['option_height'])
	
	# pyautogui.click(midpoint((x1, y1, x2, y2)))

	print("\n".join(dropdown_options))
	return

	return max_score

def wait_for_czmi_search(timeout_sec=30):
	timer = 0
	done_counter = 0
	sleep_time = 0.3
	while done_counter < 3:
		if timer > timeout_sec:
			return False
		s = screenshot()
		crop = s[160:170,1795:1810] # 'h' in "Search" disappears 
		if np.all([np.allclose(px, (225, 225, 225), atol=10, rtol=0) for px in crop]):
			done_counter = 0
		else:
			done_counter += 1
		time.sleep(sleep_time)
		timer += sleep_time
	return True

def wait_for_chart_open(timeout_sec=30):
	timer = 0
	done_counter = 0
	sleep_time = 0.3
	while done_counter < 3:
		if timer > timeout_sec:
			return False
		s = screenshot()
		crop = s[160:170,1795:1810] # gray search box disappears into white background once loaded
		if not np.all([np.allclose(px, (255, 255, 255), atol=10, rtol=0) for px in crop]):
			done_counter = 0
		else:
			done_counter += 1
		time.sleep(sleep_time)
		timer += sleep_time
	return True

def wait_for_scan_loading(timeout_sec=30):
	timer = 0
	done_counter = 0
	sleep_time = 0.5
	while done_counter < 3:
		if(timer > timeout_sec):
			return False
		s = screenshot()
		if np.all([np.allclose(px, (255, 255, 255), atol=10, rtol=0) for px in s[940:1100,1400]]):
			done_counter = 0
		else:
			done_counter += 1
		time.sleep(sleep_time)
		timer += sleep_time
	return True

def get_exam_date_time(exam_date_time_bbox):
	s = screenshot()
	results = run_tesseract(s, exam_date_time_bbox, 10)
	text = " ".join(results["text"]).lower()
	
	if(text[0:4] != "date"):
		raise RuntimeError("Could not parse exam date time")
	
	date_regexp = re.compile("\d{1,2}\/\d{1,2}\/\d{4}")
	date_str = re.search(date_regexp, text).group()

	time_regexp = re.compile("\d{1,2}:\d{1,2}:\d{2}\s?[ap]m")
	time_str = re.search(time_regexp, text).group()

	return (date_str, time_str)
