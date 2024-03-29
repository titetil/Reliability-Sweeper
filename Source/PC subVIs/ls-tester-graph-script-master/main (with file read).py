import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy.core.defchararray as np_f
from argparse import ArgumentParser
import math

parser = ArgumentParser()
parser.add_argument('--path', dest='path')
parser.add_argument('--tol_path', dest='tol_path')
parser.add_argument('--main_side', dest='main_side')
parser.add_argument('--wet_test', dest='wet_test')
parser.add_argument('--x_axis_min', dest='x_axis_min')
parser.add_argument('--x_axis_max', dest='x_axis_max')
parser.add_argument('--x2_axis_max', dest='x2_axis_max')
parser.add_argument('--y_axis_max', dest='y_axis_max')
parser.add_argument('--data_start_index', dest='data_start_index')
parser.add_argument('--ls_series', dest='ls_series')
parser.add_argument('--title', dest='title')
parser.add_argument('--time_v_res', dest='time_v_res')

args = parser.parse_args()


def create_graph(file_path, tol_path, main_side, wet_test, x_axis_min, x_axis_max, x2_axis_max, y_axis_max, data_start_index, ls_series, title, time_v_res):
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
    low_to_high_sweep = True if height_array[0] < mid_height else False
    if low_to_high_sweep:  # if sweep starts low and goes high, use this algorithm
        first_transition_index = int(np.argwhere(height_array > mid_height)[0])
        second_transition_index = int(np.argwhere(height_array[first_transition_index:] < mid_height - 10)[0]) + first_transition_index
        end_height_index = np.argmin(height_array[second_transition_index:(first_transition_index + second_transition_index)]) + second_transition_index
    else: # if sweep starts high and goes low, use this algorithm
        first_transition_index = int(np.argwhere(height_array < mid_height)[0])
        second_transition_index = int(np.argwhere(height_array[first_transition_index:] > mid_height + 10)[0]) + first_transition_index
        end_height_index = np.argmax(height_array[second_transition_index:(first_transition_index + second_transition_index)]) + second_transition_index
    data = data[:end_height_index, :]

    show_tolerance = True if ls_series in ['MLS', 'E7x', 'F1x', 'F2x'] else False

    # Tolerance data
    if show_tolerance:
        if ls_series == 'MLS' and main_side == 'True' and wet_test == 'True':
            tol_file_name = 'MLS Tolerance (MS, wet).csv'
        if ls_series == 'MLS' and main_side == 'True' and wet_test == 'False':
            tol_file_name = 'MLS Tolerance (MS, dry).csv'
        if ls_series == 'MLS' and main_side == 'False' and wet_test == 'True':
            tol_file_name = 'MLS Tolerance (SS, wet).csv'
        if ls_series == 'MLS' and main_side == 'False' and wet_test == 'False':
            tol_file_name = 'MLS Tolerance (SS, dry).csv'

        if ls_series == 'E7x' and main_side == 'True' and wet_test == 'True':
            tol_file_name = 'E7x Tolerance (MS, wet).csv'
        if ls_series == 'F1x' and main_side == 'True' and wet_test == 'True':
            tol_file_name = 'F1x Tolerance (MS, wet).csv'
        if ls_series == 'F2x' and main_side == 'True' and wet_test == 'True':
            tol_file_name = 'F2x Tolerance (MS, wet).csv'
        if ls_series == 'E7x' and main_side == 'False' and wet_test == 'True':
            tol_file_name = 'E7x Tolerance (SS, wet).csv'
        if ls_series == 'F1x' and main_side == 'False' and wet_test == 'True':
            tol_file_name = 'F1x Tolerance (SS, wet).csv'

        if ls_series == 'E7x' and main_side == 'True' and wet_test == 'False':
            tol_file_name = 'E7x Tolerance (MS, dry).csv'
        if ls_series == 'F1x' and main_side == 'True' and wet_test == 'False':
            tol_file_name = 'F1x Tolerance (MS, dry).csv'
        if ls_series == 'F2x' and main_side == 'True' and wet_test == 'False':
            tol_file_name = 'F2x Tolerance (MS, dry).csv'
        if ls_series == 'E7x' and main_side == 'False' and wet_test == 'False':
            tol_file_name = 'E7x Tolerance (SS, dry).csv'
        if ls_series == 'F1x' and main_side == 'False' and wet_test == 'False':
            tol_file_name = 'F1x Tolerance (SS, dry).csv'

        tol_color = 'black' if main_side == 'True' else 'red'

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
    if low_to_high_sweep:
        min_indice = np.argmax(sys_height)
        empty_to_full = ls_ohms[:min_indice]
        full_to_empty = ls_ohms[min_indice:]
        empty_to_full_sys = sys_height[:min_indice]
        full_to_empty_sys = sys_height[min_indice:]
    else:
        min_indice = np.argmin(sys_height)
        empty_to_full = ls_ohms[min_indice:]
        full_to_empty = ls_ohms[:min_indice]
        empty_to_full_sys = sys_height[min_indice:]
        full_to_empty_sys = sys_height[:min_indice]

    plot_time_v_res = True if ls_series == 'MLS' or time_v_res == 'True' else False

    # height vs resistance
    ax.set_xlim(int(x_axis_min), int(x_axis_max))
    ax.set_ylim(0, float(y_axis_max))
    e_to_f_plot = ax.plot(empty_to_full_sys, empty_to_full, linewidth=0.5, label='R vs. H - fill', color='blue')
    f_to_e_plot = ax.plot(full_to_empty_sys, full_to_empty, linewidth=0.5, label='R vs. H - drain', color='magenta')
    ax.set_xlabel('Height / mm', fontsize=7)
    ax.set_ylabel(r'Resistance / $\Omega$', fontsize=7)
    start, end = ax.get_xlim()
    if plot_time_v_res:
        ax.xaxis.set_ticks(np.arange(int(start), end + 10, 10))
    else:
        increment = roundup((end - start) / 25)
        ax.xaxis.set_ticks(np.arange(int(start), end, 50))
    lns = e_to_f_plot + f_to_e_plot

    # time vs resistance
    if plot_time_v_res:
        ax2 = ax.twiny()
        ax2.set_xlim(0, int(x2_axis_max))
        #ax2.set_ylim([0, float(y_axis_max)])
        r_vs_t = ax2.plot(time, ls_ohms, linewidth=0.5, label='Resistance vs. Time', color='orange')
        ax2.set_xlabel('Time / s', fontsize=7)
        start, end = ax2.get_xlim()
        ax2.xaxis.set_ticks(np.arange(start, end, time_axis_inc))
        lns = lns + r_vs_t
        ax2.tick_params(labelsize=5)

    # tolerance bands
    if show_tolerance:
        low_tol_plot = ax.plot(tol_data[:, 0], tol_data[:, 1], linewidth=0.5, color=tol_color, label='Tolerance', linestyle=':')
        up_tol_plot = ax.plot(tol_data[:, 2], tol_data[:, 3], linewidth=0.5, color=tol_color, linestyle=':')
        lns = lns + low_tol_plot

    # create legend
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=3, fontsize='x-small')

    ax.tick_params(labelsize=5)
    ax.grid(linewidth=0.1)

    if plot_time_v_res:
        ax.set_title(title, fontsize=10, y=1.08)  # this raises the title to fit the top x-axis
    else:
        ax.set_title(title, fontsize=10)

    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(0, end, 50))

    if plot_time_v_res:
        fig.savefig(file_path.replace('.csv','.png'), dpi=1000)
    else:
        make_pdf(file_path)

    #plt.show()

    plt.close(fig)  # must close figure, or there will be a memory error when running batch_graph_creator.py

def make_pdf(file_path):
    pp = PdfPages(file_path.replace('.csv','.pdf'))
    pp.savefig()
    pp.close()

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


if __name__ == "__main__":

    create_graph(args.path, args.tol_path, args.main_side, args.wet_test, args.x_axis_min, args.x_axis_max, args.x2_axis_max, args.y_axis_max, int(args.data_start_index), args.ls_series, args.title, args.time_v_res)
    #create_graph(r'C:\Data\MLS main wet\3164-1.csv',
    #             r'C:\Users\gtetil\Documents\Projects\Reliability-Sweeper\Source\PC subVIs\ls-tester-graph-script-master', 'True', 'True', -15, 225, 120, 1250, 10, 'MLS', 'Title', 'False')





