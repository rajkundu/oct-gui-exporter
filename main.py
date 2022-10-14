import pyautogui
import numpy as np
import cv2
import time
import utils
import winsound

# User switches to application
time.sleep(3)

# Screen size = 1920x1080
PATIENT_ID_ENTRY = (417, 167)
FIRST_PATIENT = (50, 300, 115, 315)
FINISH_BUTTON = (1840, 1024)

img = utils.screenshot()
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# cv2.imshow('ss', img) #cv2.imread("F:/eye/1.png"))
# cv2.waitKey(0)
# import sys
# sys.exit(0)

EYE_LEFT_DROPDOWN = {
	"loc": (710, 63),
	"width": 495,
	"option_height": 20,
	"num_visible_options": 4,
	"up_button": (1220, 70),
	"down_button": (1220, 150),
	"sample_margin_y": 10,
	"empty_color": (255, 255, 255),
	"max_options": 20
}
EYE_RIGHT_DROPDOWN = {
	"loc": (170, 63),
	"width": 495,
	"option_height": 20,
	"num_visible_options": 4,
	"up_button": (680, 70),
	"down_button": (680, 150),
	"sample_margin_y": 10,
	"empty_color": (255, 255, 255),
	"max_options": 20
}

def get_data(pt_id, eye):
	# 1) Activate patient ID field
	pyautogui.click(PATIENT_ID_ENTRY)
	time.sleep(0.7)
	pyautogui.doubleClick(PATIENT_ID_ENTRY)
	time.sleep(0.1)

	# 2) Enter patient ID
	pyautogui.press('backspace')
	pyautogui.typewrite(pt_id)
	pyautogui.press('enter')
	time.sleep(0.5)

	if not utils.wait_for_czmi_search(timeout_sec=5):
		raise TimeoutError(f"Search for chart of pt {pt_id} exceeded 5 sec")
	
	# If the row where the patient's record should be (FIRST_PATIENT) is all white, then patient's CZMI returned 0 records
	if np.all([np.allclose(px, (255, 255, 255), atol=10, rtol=0) for px in utils.screenshot(roi=FIRST_PATIENT)]):
		raise RuntimeError(f"No chart found for pt {pt_id}")

	# 3) Open patient
	pyautogui.doubleClick(utils.midpoint(FIRST_PATIENT))
	time.sleep(2)

	if not utils.wait_for_chart_open(timeout_sec=10):
		raise TimeoutError(f"Opening chart of pt {pt_id} exceeded 10 sec")

	# 4) Dropdown stuff
	utils.interact_dropdown(EYE_LEFT_DROPDOWN if eye.lower() == "left" or eye.lower() == "l" else EYE_RIGHT_DROPDOWN, "6x6")
	if(1 > -1):
		pass
	else:
		# No ONH exam for this patient's L/R eye (whatever was passed)!
		raise RuntimeError(f"ERROR: No ONH scan found")

	# 7) Click finish
	pyautogui.click(FINISH_BUTTON)
	time.sleep(1)

# 	return measurements, exam_date, exam_time
	return None, None, None

if __name__ == "__main__":
	with open("input.txt", "r") as input_txt:
		for line in input_txt:
			line = line.strip()
			if line[0] == "#":
				# print(f"Skipping '{line}'")
				continue
			pt_id, od_os = line[:-3], line[-2:]
			eye = "left" if od_os.lower() == "os" else "right"
			try:
				measurements, exam_date, exam_time = get_data(pt_id, eye)
				# csvrow = ','.join([
				# 	pt_id,
				# 	pt_id + "_" + od_os.upper(),
				# 	1 if od_os.lower() == 'od' else 2,
				# 	exam_date,
				# 	exam_date[:-4],
				# 	exam_time,
				# 	*measurements
				# ]) + '\n'

				# with open("output.csv", "a") as output_csv:
				# 	output_csv.write(csvrow)
				
				print(f"Finished {line}")
			except Exception as e:
				print(f"[ERROR] {str(e)}")
