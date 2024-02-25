from pathlib import Path
import datetime
import pandas as pd

EXPORT_DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"

def generate_image_lists(search_path, output_path):
    exports = (
        # search pattern, output filename
        ("**/*6x6 mm*", '6x6.txt'),
        ("**/*3x3 mm*", '3x3.txt'),
        ("**/*4.5x4.5 mm*", 'ONH.txt'),
        ("**/*HD 21*", 'HD21.txt'),
        ("**/*Macular Cube*", 'MacCube.txt'),
        ("**/*Optic Disc Cube*", 'OpticDiscCube.txt')
    )
    for search_pattern, output_filename in exports:
        with open(str(output_path / output_filename), "w") as f:
            for fname in search_path.glob(search_pattern):
                f.write(str(fname) + "\n")

def generate_index_df(search_path, keep_metadata_cols=False):
    row_data = []
    for filepath in search_path.glob("**/*.tiff"):
        czmi, dob, sex, scan_type, imaging_datetime, laterality, export_datetime = (filepath.stem).split("CZMI")[1].split("_")
        czmi = "CZMI" + czmi

        dob_obj = datetime.datetime.strptime(dob, "%Y%m%d").date()
        dob_str = dob_obj.strftime("%m/%d/%Y")

        imaging_datetime_obj = datetime.datetime.strptime(imaging_datetime, "%Y%m%d%H%M%S")
        imaging_datetime_str = imaging_datetime_obj.strftime(EXPORT_DATETIME_FORMAT)

        export_datetime_obj = datetime.datetime.strptime(export_datetime, "%Y%m%d%H%M%S")
        export_datetime_str = export_datetime_obj.strftime(EXPORT_DATETIME_FORMAT)

        # keep data in EXPORT_COLUMN_NAMES as well as metadata columns for sorting
        row_data.append((czmi, dob_str, sex, scan_type, imaging_datetime_str, laterality, export_datetime_str, str(filepath), imaging_datetime_obj, export_datetime_obj))

    df = pd.DataFrame(data=row_data, columns=["CZMI", "DOB", "SEX", "SCAN_TYPE", "IMAGING_DATETIME", "LATERALITY", "EXPORT_DATETIME" ,"RAW_FILEPATH", "__imaging_datetime_obj", "__export_datetime_obj"])
    df = df.sort_values(["SCAN_TYPE", "__imaging_datetime_obj"], ascending=[True, True]) # sort by imaging datetime
    if not keep_metadata_cols:
        df = df.drop([col for col in df.columns if col.startswith("__")], axis=1)

    return df

if __name__ == "__main__":
    SEARCH_PATH = Path("D:/AutoExport_Raj")

    # Image lists
    # image_list_output_path = Path("./image_lists")
    # image_list_output_path.mkdir(parents=True, exist_ok=True)
    # generate_image_lists(search_path=SEARCH_PATH, output_path=image_list_output_path)

    # Generate Index
    indexing_time = datetime.datetime.now()
    indexing_time_str = indexing_time.strftime('%Y%m%d%H%M%S')
    df = generate_index_df(search_path=SEARCH_PATH, keep_metadata_cols=False)
    df.to_csv(f"./export_index_{indexing_time_str}.csv", index=False)
