import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy.core.defchararray as np_f
import math
from enum import Enum


class Graph_Type(Enum):
    H_vs_R = 0
    T_vs_R = 1
    Both = 2

class Graph_Output_File(Enum):
    png = 0
    pdf = 1

class Color(Enum):
    red = 0
    black = 1
    green = 2
    blue = 3
    orange = 4
    yellow = 5
    purple = 6
    grey = 7

class Tol_Type(Enum):
    Bands = 0
    Boxes = 1

def create_graph(
        data,
        data_path,
        title_1,
        title_2,
        tol_path,
        tol_band_color,
        graph_type,
        height_min,
        height_max,
        height_interval,
        resistance_max,
        resistance_interval,
        time_max,
        time_interval,
        graph_output_file,
        auto_open,
        tol_type):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    graph_type = Graph_Type(graph_type)  # convert graph type to an enum
    graph_output_file = Graph_Output_File(graph_output_file)  # convert graph output file to an enum
    tol_band_color = Color(tol_band_color)  # convert tol band color to an enum
    tol_type = Tol_Type(tol_type)  # convert tol type to an enum

    # LS data
    data = np.array(data)
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
    if graph_type in [Graph_Type.Both, Graph_Type.H_vs_R]:
        data = data[:end_height_index, :]
    time = data[:, 0]

    # separate data into e-to-f and f-to-e
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

    lns = ax.plot()

    # height vs resistance
    if graph_type in [Graph_Type.Both, Graph_Type.H_vs_R]:
        ax.set_xlim(int(height_min), int(height_max))
        ax.set_ylim(0, float(resistance_max))
        e_to_f_plot = ax.plot(empty_to_full_sys, empty_to_full, linewidth=0.5, label='R vs. H - fill', color='blue')
        f_to_e_plot = ax.plot(full_to_empty_sys, full_to_empty, linewidth=0.5, label='R vs. H - drain', color='magenta')
        ax.set_xlabel('Height (mm)', fontsize=7)
        ax.set_ylabel(r'Resistance ($\Omega$)', fontsize=7)
        ax.xaxis.set_ticks(np.append(np.arange(height_min, height_max, height_interval), height_max))
        ax.yaxis.set_ticks(np.append(np.arange(0, resistance_max, resistance_interval), resistance_max))
        lns = e_to_f_plot + f_to_e_plot
        if graph_type == Graph_Type.H_vs_R:
            fig.suptitle(title_1, fontsize=10, fontweight='bold')
            ax.set_title(title_2, fontsize=10, y=1.03)

    # time vs resistance (with height vs resistance)
    if graph_type == Graph_Type.Both:
        ax2 = ax.twiny()
        ax2.set_xlim(0, time_max)
        r_vs_t = ax2.plot(time, ls_ohms, linewidth=0.5, label='Resistance vs. Time', color='orange')
        ax2.set_xlabel('Time (sec)', fontsize=7)
        ax2.xaxis.set_ticks(np.append(np.arange(0, time_max, time_interval), time_max))
        lns = lns + r_vs_t
        ax2.tick_params(labelsize=5)
        plt.subplots_adjust(top=0.835)
        fig.suptitle(title_1, fontsize=10, fontweight='bold')
        ax.set_title(title_2, fontsize=10, y=1.095)  # this raises the title to fit the top x-axis

    # time vs resistance (only)
    if graph_type == Graph_Type.T_vs_R:
        ax.set_xlim(0, time_max)
        ax.set_ylim(0, resistance_max)
        r_vs_t = ax.plot(time, ls_ohms, linewidth=0.5, label='Resistance vs. Time', color='orange')
        ax.set_xlabel('Time (sec)', fontsize=7)
        ax.set_ylabel(r'Resistance ($\Omega$)', fontsize=7)
        ax.xaxis.set_ticks(np.append(np.arange(0, time_max, time_interval), time_max))
        ax.yaxis.set_ticks(np.append(np.arange(0, resistance_max, resistance_interval), resistance_max))
        lns = r_vs_t
        fig.suptitle(title_1, fontsize=10, fontweight='bold')
        ax.set_title(title_2, fontsize=10, y=1.03)

    # tolerance bands
    if tol_path != '' and graph_type != Graph_Type.T_vs_R:
        tol_data = np.genfromtxt(tol_path, delimiter=',', dtype=str, skip_header=1)
        tol_data = np_f.replace(tol_data, '"', '')  # the csv files have double quotes for some reason - these need to be removed
        tol_data = tol_data.astype(np.float)  # convert remaining data to float
        if tol_type == Tol_Type.Bands:
            # bands
            low_tol_plot = ax.plot(tol_data[:, 0], tol_data[:, 1], linewidth=0.5, color=tol_band_color.name, label='Tolerance', linestyle=':')
            up_tol_plot = ax.plot(tol_data[:, 2], tol_data[:, 3], linewidth=0.5, color=tol_band_color.name, linestyle=':')
            lns = lns + low_tol_plot
        else:
            # boxes
            for row in tol_data:
                # Parameters: (bottom-left-x, bottom-left-y), width, height
                rect = patches.Rectangle((row[0], row[1]), (row[2]-row[0]), (row[3]-row[1]), linewidth=0.5, edgecolor=tol_band_color.name, facecolor='none')
                ax.add_patch(rect)
            tol_legend = ax.plot(0, 0, linewidth=0.5, color=tol_band_color.name, label='Tolerance')  # this is a blank plot just to get Tolerance into the legend
            lns = lns + tol_legend

    # create legend
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=3, fontsize='x-small')

    ax.tick_params(labelsize=5)
    ax.grid(linewidth=0.1)

    # output graph to file
    graph_path = data_path.replace('.csv','.' + graph_output_file.name)
    if graph_output_file == Graph_Output_File.png:
        fig.savefig(graph_path, dpi=1000)
    elif graph_output_file == Graph_Output_File.pdf:
        make_pdf(graph_path)

    if auto_open:
        subprocess.Popen([graph_path], shell=True)

    #plt.show()

    plt.close(fig)  # must close figure, or there will be a memory error when running batch_graph_creator.py

def make_pdf(path):
    pp = PdfPages(path)
    pp.savefig()
    pp.close()

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


if __name__ == "__main__":

    file_path = r'C:\Users\garre\Downloads\GQPS 66587 Dry (no header).csv'
    data = np.genfromtxt(file_path, delimiter=',', dtype=str,)
    data = np_f.replace(data, '"', '')  # the csv files have double quotes for some reason - these need to be removed
    data = data.astype(np.float)  # convert remaining data to float

    create_graph(data=data,
                 data_path=file_path,
                 title_1='Title 1',
                 title_2='Title 2',
                 tol_path=r'C:\Users\garre\OneDrive - Tetil Engineering Inc\Documents\Projects\Reliability-Sweeper\Source\Files\Tolerances\Nissan P42QR Tolerance.csv',
                 tol_band_color=0,
                 graph_type=2,
                 height_min=-0,
                 height_max=160,
                 height_interval=10,
                 resistance_max=300,
                 resistance_interval=20,
                 time_max=5,
                 time_interval=1,
                 graph_output_file=0,
                 auto_open=1,
                 tol_type=1)





