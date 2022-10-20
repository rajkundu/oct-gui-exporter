import sys
import pyautogui
import numpy as np
import cv2
import time
import utils
from pathlib import Path

# User switches to application
time.sleep(3)

# Screen size = 1920x1080
PATIENT_ID_ENTRY = (417, 167)
FIRST_PATIENT = (50, 300, 115, 315)
FINISH_BUTTON = (1840, 1024)

EXPORT_BASE_PATH = Path("D:/AutoExport")
OUTPUT_CSV_PATH = EXPORT_BASE_PATH / "output_main.csv"

img = utils.screenshot()
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# cv2.imshow('ss', img) #cv2.imread("F:/eye/1.png"))
# cv2.waitKey(0)
# sys.exit(0)

VISIT_DATES_DROPDOWN = {
	"loc": (10, 63),
	"width": 115,
	"option_height": 22,
	"num_visible_options": 4,
	"up_button": (136, 70),
	"down_button": (136, 150),
	"sample_margin_y": 8,
	"empty_color": (255, 255, 255),
	"max_options": 20
}
EYE_RIGHT_DROPDOWN = {
	"eye": "OD",
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
EYE_LEFT_DROPDOWN = {
	"eye": "OS",
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

def get_data(pt_id, eye):

	eye = eye.upper()
	if eye not in ("OD", "OS"):
		raise ValueError("eye param must be one of ('OD', 'OS')")


	# 1) Activate patient ID field
	pyautogui.click(PATIENT_ID_ENTRY)
	time.sleep(0.7)
	pyautogui.doubleClick(PATIENT_ID_ENTRY)
	time.sleep(0.1)

	# 2) Enter patient ID and search
	pyautogui.press('backspace')
	pyautogui.typewrite(pt_id)
	pyautogui.press('enter')
	if not utils.wait_for_czmi_search(timeout_sec=8):
		raise TimeoutError(f"Search for chart of pt {pt_id} exceeded 8 sec")
	
	# If the row where the patient's record should be (FIRST_PATIENT) is all white, then patient's CZMI returned 0 records
	if np.all([np.allclose(px, (255, 255, 255), atol=10, rtol=0) for px in utils.screenshot(roi=FIRST_PATIENT)]):
		raise RuntimeError(f"No chart found for pt {pt_id}")

	# 3) Open patient chart
	pyautogui.doubleClick(utils.midpoint(FIRST_PATIENT))
	if not utils.wait_for_chart_open(timeout_sec=10):
		raise TimeoutError(f"Opening chart of pt {pt_id} exceeded 10 sec")

	# 4) Dropdown stuff
	if eye == "OS":
		dropdown = EYE_LEFT_DROPDOWN
	else:
		dropdown = EYE_RIGHT_DROPDOWN
	save_path = EXPORT_BASE_PATH / f"{pt_id.upper()}_{eye}" # folder name = CZMI000000001_OD
	save_path.mkdir(parents=True, exist_ok=True) # ensure pt. folder exists

	#print(f"{pt_id}_{eye}")
	#print("date\t\toptic\tmaccb\tonh  \t6x6  \t3x3  \thd21 \tunknw")
	ret_data = []
	for date in utils.visit_dates_generator(VISIT_DATES_DROPDOWN):
		ret = utils.interact_dropdown(dropdown, save_path)
		scan_names, (num_optic_disc, num_mac_cube, num_onh, num_6x6, num_3x3, num_hd21, num_unknown) = ret
		#print(f"{date}\t{num_optic_disc}\t{num_mac_cube}\t{num_onh}\t{num_6x6}\t{num_3x3}\t{num_hd21}\t{num_unknown}")
		with open(str(save_path / "scan_list.txt"), 'a') as scan_list_file:
			scan_list_file.write(f"DATE: {date}\n")
			for scan_name in scan_names:
				scan_list_file.write(scan_name + "\n")
		ret_data.append((date, ret))
	
	# 7) Click finish
	pyautogui.click(FINISH_BUTTON)
	time.sleep(1)

	return ret_data

if __name__ == "__main__":
	# Write output CSV header if file doesn't exist
	if not OUTPUT_CSV_PATH.exists():
		with open(str(OUTPUT_CSV_PATH), 'w') as output_csv:
			output_csv.write(",".join([
				"CZMI_EYE",
				"NUM_TOTAL_DATES",
				"DATE",
				"NUM_OPTIC_DISC",
				"NUM_MAC_CUBE",
				"NUM_ONH",
				"NUM_6x6",
				"NUM_3x3",
				"NUM_HD21",
				"NUM_UNKNOWN",
			]) + "\n")
	with open("input.txt", "r") as input_txt:
		for line in input_txt:
			line = line.strip().upper()

			# Skip lines that begin with "#"
			if line[0] == "#":
				print(f"Skipping '{line}'")
				continue

			pt_id, od_os = line[:-3].upper(), line[-2:].upper()
			csv_rows = []
			try:
				data = get_data(pt_id, od_os)
				for date, ret in data:
					scan_names, (num_optic_disc, num_mac_cube, num_onh, num_6x6, num_3x3, num_hd21, num_unknown) = ret
					csv_row = ",".join([
						pt_id + "_" + od_os,
						str(len(data)),
						date,
						str(num_optic_disc),
						str(num_mac_cube),
						str(num_onh),
						str(num_6x6),
						str(num_3x3),
						str(num_hd21),
						str(num_unknown)
					])
					csv_rows.append(csv_row)
				print(f"Finished {line}")
			except Exception as e:
				if isinstance(e, pyautogui.FailSafeException): # raise PyAutoGui failsafe exception
					raise e
				csv_row = ",".join([
					pt_id + "_" + od_os,
					"[ERROR]",
					str(e)
				])
				print(f"[ERROR] {str(e)}")

			with open(str(OUTPUT_CSV_PATH), "a") as output_csv:
					for csv_row in csv_rows:
						output_csv.write(csv_row + "\n")
