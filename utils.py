import numpy as np
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
import pyautogui
import time
from pathlib import Path
import re
import datetime

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

def scale_img(img, scaling_factor):
	height, width = img.shape[:2]
	return cv2.resize(img, (int(width * scaling_factor), int(height * scaling_factor)), interpolation = cv2.INTER_AREA)

def run_tesseract(img, roi, min_conf, scaling_factor=1.0, blur_size=0, disp=False, psm=None, char_whitelist=None):
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

	# Build config
	cfgstrs = []
	if psm is not None:
		cfgstrs.append(f"--psm {psm}")
	if char_whitelist is not None:
		cfgstrs.append(f"tessedit_char_whitelist={char_whitelist}")
	
	cfgstr = ""
	if len(cfgstrs) > 0:
		cfgstr = " ".join(cfgstrs)

	results = pytesseract.image_to_data(img_cropped, output_type=pytesseract.Output.DICT, config=cfgstr)
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

def click(*args, **kwargs):
	pyautogui.click(*args, **kwargs)
	time.sleep(0.1)

def rightClick(*args, **kwargs):
	pyautogui.rightClick(*args, **kwargs)
	time.sleep(0.1)

def interact_save_dialog(save_path: Path):
	pyautogui.keyDown('ctrl') # focus on path input bar
	pyautogui.press('l')
	pyautogui.keyUp('ctrl')

	pyautogui.typewrite(str(save_path))
	pyautogui.press('enter')
	
	pyautogui.keyDown('alt') # focus on image save type dropdown
	pyautogui.press('t')
	pyautogui.keyUp('alt')
	pyautogui.press('t') # press t to select TIFF

	pyautogui.press('enter') # save image & close dialog
	time.sleep(0.1) # wait for dialog to close

# EXPORT SEQUENCES
def export_optic_disc(save_path: Path, eye: str):
	eye = eye.upper()
	if eye not in ("OD", "OS"):
		raise ValueError("eye param must be one of ('OD', 'OS')")

	wait_for_scan_subdata_load()
	click((1245, 73)) # click on first item in third dropdown column
	pyautogui.moveTo((960, 540)) # move to middle of screen to collapse dropdown
	if not wait_for_loading_popup():
		return False
	check_warning_dialog()

	# Right click on scan
	if eye == 'OD':
		pyautogui.doubleClick((390, 355)) # enter fullscreen
	else:
		pyautogui.doubleClick((1320, 355)) # enter fullscreen
	time.sleep(0.1)

	rightClick((960, 540)) # right click in center of screen for context menu
	pyautogui.press('s') # open save dialog

	time.sleep(0.1)
	interact_save_dialog(save_path)

	# exit fullscreen
	pyautogui.press('tab')
	pyautogui.press('enter')
	time.sleep(0.1)

	return True

def export_mac_cube(save_path: Path, eye: str):
	eye = eye.upper()
	if eye not in ("OD", "OS"):
		raise ValueError("eye param must be one of ('OD', 'OS')")

	wait_for_scan_subdata_load()
	click((1245, 143)) # click on "Ganglion Cell OU Analysis"
	pyautogui.moveTo((960, 540)) # move to middle of screen to collapse dropdown
	if not wait_for_loading_popup():
		return False
	check_warning_dialog()
	
	# Right click on scan
	if eye == 'OD':
		rightClick((180, 320)) # right click for context menu
	else:
		rightClick((1240, 320)) # right click for context menu
	time.sleep(0.1)
	pyautogui.press('s') # select "Save Image As..."
	pyautogui.press('enter') # open save dialog

	time.sleep(0.1)
	interact_save_dialog(save_path)

	# exit fullscreen
	pyautogui.press('tab')
	pyautogui.press('enter')
	time.sleep(0.1)

	return True

def export_onh(save_path: Path):
	wait_for_scan_subdata_load()
	click((1245, 73)) # click on first item in third dropdown column
	pyautogui.moveTo((960, 540)) # move to middle of screen to collapse dropdown
	if not wait_for_loading_popup():
		return False
	check_warning_dialog()
	
	pyautogui.moveTo((780, 235)) # move to & click Fullscreen button
	time.sleep(0.1)
	click()
	time.sleep(0.1)

	click((1195, 15)) # click Save button to open save dialog

	time.sleep(0.1)
	interact_save_dialog(save_path)

	pyautogui.press('esc') # exit fullscreen
	time.sleep(0.1)

	return True

def export_6x6(save_path: Path):
	wait_for_scan_subdata_load()
	click((1245, 73)) # click on first item in third dropdown column
	pyautogui.moveTo((960, 540)) # move to middle of screen to collapse dropdown
	if not wait_for_loading_popup():
		return False
	check_warning_dialog()
	
	click((80, 430)) # open Superficial Capillary Plexus scan
	time.sleep(0.2)

	# Ensure no overlay
	click((1420, 760)) # click "trace"
	time.sleep(0.1)
	click((1330, 760)) # click "map"
	time.sleep(0.1)
	click((1330, 760)) # click "map" again to disable
	time.sleep(0.1)

	pyautogui.moveTo((857, 235)) # move to & click Fullscreen button
	time.sleep(0.1)
	click()
	time.sleep(0.1)

	click((1195, 15)) # click Save button to open save dialog

	time.sleep(0.1)
	interact_save_dialog(save_path)

	pyautogui.press('esc') # exit fullscreen
	time.sleep(0.1)

	return True

def export_3x3(save_path: Path):
	return export_6x6(save_path) # do exact same thing as for 6x6

def export_hd21(save_path: Path):
	# wait for scan load
	if not wait_for_loading_popup():
		return False
	check_warning_dialog()

	pyautogui.doubleClick((960, 540)) # enter fullscreen
	time.sleep(0.1)

	rightClick((960, 540)) # right click in center of screen for context menu
	pyautogui.press('s') # open save dialog

	time.sleep(0.1)
	interact_save_dialog(save_path)

	# exit fullscreen
	pyautogui.press('tab')
	pyautogui.press('enter')
	time.sleep(0.1)

	return True

def visit_dates_generator(dropdown: dict, min_datetime=None):
	x1, base_y = dropdown['loc']
	x2 = x1 + dropdown['width']
	counter = 0

	# Press tab to move focus from date dropdown so that first item not selected/blue
	pyautogui.press('tab')
	time.sleep(0.1)

	while True:
		#failsafe
		if(counter > dropdown['max_options']):
			break

		if counter >= dropdown['num_visible_options']:
			pyautogui.click(dropdown['down_button'])
			time.sleep(0.1)

		y1 = int(base_y + min(counter, dropdown['num_visible_options'] - 1)*dropdown['option_height'])
		y2 = int(y1 + dropdown['option_height'])
		current_option_roi = (x1, y1, x2, y2)
		s = screenshot()
		if np.all([np.allclose(px, dropdown['empty_color'], atol=10, rtol=0) for px in s[(y1+y2)//2][x1:x1+30]]):
			break

		results = run_tesseract(s, current_option_roi, 10, psm=6, disp=False, char_whitelist="0123456789/")
		text = process_dropdown_text(results['text'])

		# Click on option
		click(midpoint(current_option_roi))
		time.sleep(0.5)

		match = re.search(r"\d{1,2}\/\d{1,2}\/\d{4}", text)
		if match is not None:
			text = match.group()
		text = text.replace("/", ".")

		yield text

		counter += 1
		if np.all([np.allclose(px, dropdown['empty_color'], atol=10, rtol=0) for px in s[y2+dropdown['sample_margin_y']][x1:x1+30]]):
			break

	return

def interact_dropdown(dropdown: dict, save_path: Path):
	eye = dropdown['eye'].upper()
	x1, base_y = dropdown['loc']
	x2 = x1 + dropdown['width']
	counter = 0
	dropdown_options = []

	# Counters for # of scans of each type
	num_optic_disc = 0
	num_mac_cube = 0
	num_onh = 0
	num_6x6 = 0
	num_3x3 = 0
	num_hd21 = 0
	num_unknown = 0

	while True:
		#failsafe
		if(counter > dropdown['max_options']):
			break

		if counter >= dropdown['num_visible_options']:
			pyautogui.click(dropdown['down_button'])
			time.sleep(0.1)

		y1 = int(base_y + min(counter, dropdown['num_visible_options'] - 1)*dropdown['option_height'])
		y2 = int(y1 + dropdown['option_height'])
		current_option_roi = (x1, y1, x2, y2)
		s = screenshot()
		if np.all([np.allclose(px, dropdown['empty_color'], atol=10, rtol=0) for px in s[(y1+y2)//2][x1:x1+30]]):
			break

		results = run_tesseract(s, current_option_roi, 10, psm=6)
		text = process_dropdown_text(results['text'])
		dropdown_options.append(text)

		# Optic Disc
		if "optic disc cube" in text:
			pyautogui.click(midpoint((x1, y1, x1+30, y2))) # use x1+30 instead of x2 so that hover hint doesn't spill into third dropdown
			time.sleep(0.2)
			export_optic_disc(save_path, eye)
			num_optic_disc += 1
		# Macular Cube
		elif "macular cube" in text:
			pyautogui.click(midpoint((x1, y1, x1+30, y2)))
			time.sleep(0.2)
			export_mac_cube(save_path, eye)
			num_mac_cube += 1
		# ONH Angiography
		elif "onh angio" in text or ("angio" in text and "4.5" in text):
			pyautogui.click(midpoint((x1, y1, x1+30, y2)))
			time.sleep(0.5)
			export_onh(save_path)
			num_onh += 1
		# 6x6 Angiography
		elif "angio" in text and "6x6" in text:
			pyautogui.click(midpoint((x1, y1, x1+30, y2)))
			time.sleep(0.2)
			export_6x6(save_path)
			num_6x6 += 1
		# 3x3 Angiography
		elif "angio" in text and "3x3" in text:
			pyautogui.click(midpoint((x1, y1, x1+30, y2)))
			time.sleep(0.2)
			export_3x3(save_path)
			num_3x3 += 1
		# HD21
		elif "hd 21" in text:
			pyautogui.click(midpoint((x1, y1, x1+30, y2)))
			time.sleep(0.2)
			export_hd21(save_path)
			num_hd21 += 1
		# Other
		else:
			#print(f"UNKNOWN SCAN: {text}")
			num_unknown += 1

		counter += 1
		if np.all([np.allclose(px, dropdown['empty_color'], atol=10, rtol=0) for px in s[y2+dropdown['sample_margin_y']][x1:x1+30]]):
			break

	return dropdown_options, (num_optic_disc, num_mac_cube, num_onh, num_6x6, num_3x3, num_hd21, num_unknown)

def verify_czmi_entry_page(timeout_sec=5):
	timer = 0
	sleep_time = 0.3
	while timer < timeout_sec:
		s = screenshot()
		crop = s[77:78,30:190] # look for gray background of "Find existing Patient" tab
		if np.all([np.allclose(px, (249, 249, 249), atol=10, rtol=0) for px in crop]):
			return True
		time.sleep(sleep_time)
		timer += sleep_time
	raise AssertionError("Expected gray 'Find Existing Patient' tab, but not found.")

def wait_for_finish_button_active(timeout_sec=30):
	timer = 0
	done_counter = 0
	sleep_time = 0.3
	while done_counter < 1:
		if timer > timeout_sec:
			return False
		pyautogui.moveTo((1790, 1015))
		time.sleep(0.1)
		s = screenshot()
		crop = s[1015:1025,1790:1800]
		if not np.all([np.allclose(px, (250, 241, 231), atol=10, rtol=0) for px in crop]):
			done_counter = 0
		else:
			done_counter += 1
		time.sleep(sleep_time)
		timer += sleep_time
	return True

def search_czmi(pt_id, timeout_sec=30):
	# capture initial screenshot of "Search" button
	s_initial = screenshot()
	crop_initial = s_initial[160:175,1760:1800]

	# execute search
	pyautogui.press('backspace')
	pyautogui.typewrite(pt_id)
	pyautogui.press('enter')
	time.sleep(0.1)

	# wait for "Search" button, which now says "Stop", to say "Search" again by comparing screenshot to initial (no OCR...)
	timer = 0
	done_counter = 0
	sleep_time = 0.3
	while done_counter < 3:
		if timer > timeout_sec:
			return False
		s = screenshot()
		crop = s[160:175,1760:1800]
		if not np.allclose(crop, crop_initial, atol=10, rtol=0):
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

def wait_for_loading_popup(timeout_sec=30):
	timer = 0
	done_counter = 0
	sleep_time = 0.5
	while done_counter < 3:
		if(timer > timeout_sec):
			# possible that loading took forever because of warning dialog
			check_warning_dialog()
			return False
		s = screenshot()
		crop = s[433:434,910:1100] # light blue header of "Loading" popup
		if np.all([np.allclose(px, (249, 243, 240), atol=10, rtol=0) for px in crop]):
			done_counter = 0
		else:
			done_counter += 1
		time.sleep(sleep_time)
		timer += sleep_time
	return True

def wait_for_scan_subdata_load(timeout_sec=30):
	timer = 0
	done_counter = 0
	sleep_time = 0.3
	while done_counter < 3:
		if(timer > timeout_sec):
			return False
		s = screenshot()
		if np.all([np.allclose(px, (255, 255, 255), atol=10, rtol=0) for px in s[65:145,1235:1760]]):
			done_counter = 0
		else:
			done_counter += 1
		time.sleep(sleep_time)
		timer += sleep_time
	return True

def check_warning_dialog():
	s = screenshot()
	# crop_yellow = s[535:550,825:826] # yellow column in hazard symbol
	# crop_blue = s[592:605,1131:1132] # blue column in close button focus outline
	# if np.all([np.allclose(px, (0, 225, 252), atol=10, rtol=0) for px in crop_yellow]) or np.all([np.allclose(px, (215, 120, 0), atol=10, rtol=0) for px in crop_blue]):
	crop_gray = s[582:618,782:794]
	if np.all([np.allclose(px, (235, 235, 235), atol=10, rtol=0) for px in crop_gray]):
		pyautogui.press('esc') # close warning dialog
		time.sleep(10) # wait 10 sec to ensure dialog closed, loading terminated, etc
		raise RuntimeError("Encountered unknown error")
	return True
