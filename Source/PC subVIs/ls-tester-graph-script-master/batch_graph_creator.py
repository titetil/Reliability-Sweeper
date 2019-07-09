from main import create_graph
import os
import numpy as np


def main():
    data_path = raw_input("Enter data directory path:  ")
    x_axis_min = raw_input("Enter x-axis minimum (for system height):  ")
    x_axis_max = raw_input("Enter x-axis maximum (for system height):  ")
    x2_axis_max = raw_input("Enter x-axis maximum (for time):  ")
    tol_path = os.getcwd()
    for path, subdirs, files in os.walk(data_path):
        for file in files:
            file_path = os.path.join(data_path, file)
            file_name = file.split('.')[0]
            is_csv = True if file.split('.')[1] == 'csv' else False
            if is_csv:
                print 'Working on: ' + file_path
                data = np.genfromtxt(file_path, delimiter=',', dtype=str)
                test_style = data[1,0]
                ca_number = data[1,1]
                part_sn = data[1,2]
                part_model = data[1,3]
                hours_description = data[7,0]
                main_side = 'True' if 'MS' in part_model else 'False'
                wet_test = 'True' if test_style == 'Wet Test' else 'False'
                mls_test = 'True' if 'MLS' in part_model else 'False'
                create_graph(file_path, tol_path, main_side, wet_test, x_axis_min, x_axis_max, x2_axis_max, '1250', 10, mls_test, ca_number + ' ' + part_model + ' ' + part_sn + ' ' + test_style + ' ' + hours_description)
    print 'Batch graph creation complete.'


if __name__ == "__main__":

    main()