import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy.core.defchararray as np_f
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--path', dest='path')
parser.add_argument('--wet_test', dest='wet_test')
parser.add_argument('--y_axis_max', dest='y_axis_max')
parser.add_argument('--data_start_index', dest='data_start_index')

args = parser.parse_args()


def create_graph(file_path, wet_test, y_axis_max, data_start_index):
    fig, ax = plt.subplots()

    file_name = os.path.basename(file_path).split('.')[0]
    data = np.genfromtxt(file_path, delimiter=',', dtype=str, skip_header=data_start_index)
    data = np_f.replace(data, '"', '')  # the csv files have double quotes for some reason - these need to be removed
    data = data.astype(np.float)  # convert remaining data to float
    if wet_test == 'True':
        sys_height = data[:,1]
        ls_ohms = data[:,4]

        ax.set_xlim([0, sys_height.max()])
        ax.set_ylim([0, float(y_axis_max)])
        ax.plot(sys_height, ls_ohms, linewidth=0.1)
        ax.set_xlabel('Height (mm)', fontsize=7)
        ax.set_ylabel('LS Resistance (ohms)', fontsize=7)

        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(0, end, 10))

    else:  #dry test
        ls_time = data[:, 0]
        ls_ohms = data[:, 4]

        ax.set_xlim([0, ls_time.max()])
        ax.set_ylim([0, float(y_axis_max)])
        ax.plot(ls_time, ls_ohms, linewidth=0.1)
        ax.set_xlabel('Time (sec)', fontsize=7)
        ax.set_ylabel('LS Resistance (ohms)', fontsize=7)

        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(0, end, 1))

    ax.tick_params(labelsize=5)
    ax.set_title(file_name, fontsize=7)
    ax.grid(linewidth=0.1)

    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(0, end, 50))

    #fig.savefig("test.png")
    #plt.show()
    make_pdf(file_path)

def make_pdf(file_path):
    pp = PdfPages(file_path.replace('.csv','.pdf'))
    pp.savefig()
    pp.close()


if __name__ == "__main__":

    create_graph(args.path, args.wet_test, args.y_axis_max, int(args.data_start_index))





