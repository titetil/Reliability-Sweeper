import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy.core.defchararray as np_f
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--path', dest='path')
parser.add_argument('--tol_path', dest='tol_path')
parser.add_argument('--main_side', dest='main_side')
parser.add_argument('--wet_test', dest='wet_test')
parser.add_argument('--y_axis_max', dest='y_axis_max')
parser.add_argument('--data_start_index', dest='data_start_index')
parser.add_argument('--data_end_index', dest='data_end_index')
parser.add_argument('--mls_test', dest='mls_test')
parser.add_argument('--title', dest='title')

args = parser.parse_args()


def create_graph(file_path, tol_path, main_side, wet_test, y_axis_max, data_start_index, data_end_index, mls_test, title):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # LS data
    file_name = os.path.basename(file_path).split('.')[0]
    data = np.genfromtxt(file_path, delimiter=',', dtype=str, skip_header=data_start_index)
    data = np_f.replace(data, '"', '')  # the csv files have double quotes for some reason - these need to be removed
    data = data.astype(np.float)  # convert remaining data to float
    height_array = data[:,1]
    min_height = np.amin(height_array)
    max_height = np.amax(height_array)
    mid_height = (max_height - min_height) / 2
    first_transition_index = int(np.argwhere(height_array > mid_height)[0])
    second_transition_index = int(np.argwhere(height_array[first_transition_index:] < mid_height - 10)[0]) + first_transition_index
    end_height_index = np.argmin(height_array[second_transition_index:(first_transition_index + second_transition_index)]) + second_transition_index
    data = data[:end_height_index, :]
    #data = data[:data_end_index,:]

    # Tolerance data
    if mls_test == 'True':
        if main_side == 'True':
            if wet_test == 'True':
                tol_file_name = 'MLS Tolerance (MS, wet).csv'
            else:
                tol_file_name = 'MLS Tolerance (MS, dry).csv'
            tol_color = 'black'
        else:
            if wet_test == 'True':
                tol_file_name = 'MLS Tolerance (SS, wet).csv'
            else:
                tol_file_name = 'MLS Tolerance (SS, dry).csv'
            tol_color = 'red'
        tol_file_path = os.path.join(tol_path, tol_file_name)
        tol_data = np.genfromtxt(tol_file_path, delimiter=',', dtype=str, skip_header=1)
        tol_data = np_f.replace(tol_data, '"', '')  # the csv files have double quotes for some reason - these need to be removed
        tol_data = tol_data.astype(np.float)  # convert remaining data to float

    if wet_test == 'True':
        time_axis_inc = 10
    else:
        time_axis_inc = 1
    time = data[:, 0]
    sys_height = data[:,1]
    ls_ohms = data[:,4]
    min_indice = np.argmax(sys_height)
    empty_to_full = ls_ohms[:min_indice]
    full_to_empty = ls_ohms[min_indice:]
    empty_to_full_sys = sys_height[:min_indice]
    full_to_empty_sys = sys_height[min_indice:]

    # height vs resistance
    if mls_test == 'True':
        xmax = tol_data[:, 2].max()
    else:
        xmax = sys_height.max()
    ax.set_xlim(sys_height.min(), xmax)
    ax.set_ylim(0, float(y_axis_max))
    e_to_f_plot = ax.plot(empty_to_full_sys, empty_to_full, linewidth=0.5, label='R vs. H - fill', color='blue')
    f_to_e_plot = ax.plot(full_to_empty_sys, full_to_empty, linewidth=0.5, label='R vs. H - drain', color='magenta')
    ax.set_xlabel('Height / mm', fontsize=7)
    ax.set_ylabel(r'Resistance / $\Omega$', fontsize=7)
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(int(start), end + 10, 10))
    lns = e_to_f_plot + f_to_e_plot

    # time vs resistance
    if mls_test == 'True':
        ax2 = ax.twiny()
        ax2.set_xlim(0, time.max())
        #ax2.set_ylim([0, float(y_axis_max)])
        r_vs_t = ax2.plot(time, ls_ohms, linewidth=0.5, label='Resistance vs. Time', color='orange')
        ax2.set_xlabel('Time / s', fontsize=7)
        start, end = ax2.get_xlim()
        ax2.xaxis.set_ticks(np.arange(start, end, time_axis_inc))
        lns = lns + r_vs_t
        ax2.tick_params(labelsize=5)

    # tolerance bands
    if mls_test == 'True':
        low_tol_plot = ax.plot(tol_data[:, 0], tol_data[:, 1], linewidth=0.5, color=tol_color, label='Tolerance', linestyle=':')
        up_tol_plot = ax.plot(tol_data[:, 2], tol_data[:, 3], linewidth=0.5, color=tol_color, linestyle=':')
        lns = lns + low_tol_plot

    # create legend
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=3, fontsize='x-small')

    ax.tick_params(labelsize=5)
    ax.grid(linewidth=0.1)

    if mls_test == 'True':
        ax.set_title(title, fontsize=10, y=1.08)  # this raises the title to fit the top x-axis
    else:
        ax.set_title(title, fontsize=10)

    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(0, end, 50))

    if mls_test == 'True':
        fig.savefig(file_path.replace('.csv','.png'), dpi=1000)
    else:
        make_pdf(file_path)

    #plt.show()

def make_pdf(file_path):
    pp = PdfPages(file_path.replace('.csv','.pdf'))
    pp.savefig()
    pp.close()


if __name__ == "__main__":

    create_graph(args.path, args.tol_path, args.main_side, args.wet_test, args.y_axis_max, int(args.data_start_index), int(args.data_end_index), args.mls_test, args.title)
    #create_graph(r'C:\Data\MLS script test\36742.csv',
    #             r'C:\Users\gtetil\Documents\Projects\ls-tester-graph-script', 'True', 'False', '1250', 10, 0, 'False', 'Title')





