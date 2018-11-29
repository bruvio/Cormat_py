"""
Module with useful plotting function
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import pathlib
# ----------------------------
__author__ = "L. Kogan"
# ----------------------------

def make_plot(all_data, colours=None, markers=None, labels=None, linestyles=None,
              pformat=None, xtitles=None, ytitles=None, xranges=None, yranges=None,
              vert_lines=None, horz_lines=None,
              vert_lines_many_colors=None, vert_labels=None, title="", ncolumns=2,
              show=True, save_name=""):
    """
    Plot data

    :param all_data: 3D np array of form [[ [x1], [y1] ], [ [x2], [y2] ], ...]
    :param colours: Array with one colour per dataset (default: blue)
    :param markers: Array with one marker style per dataset (default: No markers)
    :param labels: Array with one label per dataset (for the legend, default: no legend)
    :param linestyles: Array with one linestyle per dataset (default: solid line if markers=None, no line otherwise)
    :param pformat: Array describing the number of datasets per subplot, ie. [nplots_subplot1, nplots_subplot2]
    :param xtitles: Array of xtitles for each subplot, with length of pformat
    :param ytitles: Array of ytitles for each subplot, with length of pformat
    :param xranges: Array of xranges for each subplot, with length of pformat
    :param yranges: Array of yranges for each subplot, with length of pformat
    :param vert_lines: 2D array with  x-values for vertical lines to be plotted per subplot, ie. [[x1_subplot1], [x2_subplot2]]
    :param horz_lines: 2D array with y-values for horizontal lines to be plotted per subplot, ie. [[y1_subplot1], [y2_subplot2]]
    :param vert_lines_many_colors: 3D array with x-values for vertical lines to be plotted per subplot, in different colours
    :param vert_labels: labels for vertical lines
    :param show: Set to True to show plot to screen (default : True)
    :param save_name: Set to the name of a file to save as .png

    """

    # Style stuff
    if colours is None:
        colours = ["blue"]*len(all_data)
    if markers is None:
        markers = ["None"]*len(all_data)
    elif linestyles is None:
        linestyles = [""]*len(all_data)
    if linestyles is None:
        linestyles = ["-"]*len(all_data)
    if labels is None:
        labels = [None]*len(all_data)

    # How plots are arranged into subplots
    if pformat is None:
        pformat = [len(all_data)]

    # For putting data in correct subplot
    n_subplots = len(pformat)
    subplot = 1
    count_plot = 0

    # For axes ranges
    xmin = 9e30
    xmax = -9e30
    ymin = 9e30
    ymax = -9e30

    plt.close()

    # Loop over data
    if ncolumns > 1 and n_subplots != 2:
        sub_x = n_subplots
        sub_y = 1
        if n_subplots > ncolumns:
            sub_x = ncolumns
            sub_y = (n_subplots - 1) // ncolumns + 1
    else:
        sub_x = 1
        sub_y = 2
        ncolumns = 1

    f, ax = plt.subplots(sub_y, sub_x, figsize=(14,14), sharex=True)

    if ncolumns > 1 and n_subplots != 2:
        if sub_y == 1:
            ax = [ax]
            if sub_x == 1:
                ax = [ax]
    else:
        if sub_x == 1:
            ax_here = []
            for ax_t in ax:
                ax_here.append([ax_t])
            ax = ax_here
    

    for ind, data in enumerate(all_data):
        ind_y = (subplot - 1) // ncolumns
        ind_x = subplot - ncolumns * (ind_y) - 1        

        lw = 1
        if linestyles[ind] == "--":
            lw = 2
        ax[ind_y][ind_x].plot(data[0], data[1],
                              c=colours[ind], marker=markers[ind],
                              linestyle=linestyles[ind], label=labels[ind], markersize=12, linewidth=lw)

        # For axes ranges (if they haven't been set)
        if xranges is None:
            if np.min(data[0]) < xmin:
                xmin = np.min(data[0])
            if np.max(data[0]) > xmax:
                xmax = np.max(data[0])

        if yranges is None:
            if np.min(data[1]) < ymin:
                ymin = np.min(data[1])
            if np.max(data[1]) > ymax:
                ymax = np.max(data[1])

        count_plot += 1

        # Last plot in this subplot
        if count_plot == pformat[subplot-1]:            
            if xranges is None:
                xrange = [xmin*0.9, xmax*1.1]
            else:
                xrange = xranges[subplot-1]

            if yranges is None:
                yrange = [ymin*0.9, ymax*1.1]
            else:
                yrange = yranges[subplot-1]

            # Overlay vertical or horizontal lines
            show_legend = (labels[0] is not None)
            if vert_lines is not None:
                if len(vert_lines) > 0 and vert_lines_many_colors is None:
                    #print("Vert lines length is > 0 len this one {}".format(len(vert_lines[subplot-1])))
                    for vert in vert_lines[subplot-1]:
                        ax[ind_y][ind_x].axvline(x=vert, ymin=0, ymax=1, linewidth=2, color="red")
                elif len(vert_lines) > 0 and vert_lines_many_colors is not None and vert_labels is not None:
                    for vert_set, vert_col, vert_label in zip(vert_lines[subplot-1],
                                                              vert_lines_many_colors[subplot-1],
                                                              vert_labels[subplot-1]):
                        if len(vert_set) > 0:
                            ax[ind_y][ind_x].plot([xrange[0]], [yrange[0]], c=vert_col, marker="",
                                                  linestyle="-", label=vert_label)
                        for vert in vert_set:
                            show_legend = True
                            ax[ind_y][ind_x].axvline(x=vert, ymin=0, ymax=1, linewidth=2, color=vert_col)

            if horz_lines is not None:
                if len(horz_lines) > 0:
                    for horz in horz_lines[subplot-1]:
                        plt.axhline(y=horz, xmin=0, xmax=1, linewidth=2, color="red")

            # Set axes ranges, legends etc
            plt.xlim(xrange[0], xrange[1])
            plt.ylim(yrange[0], yrange[1])

            if xtitles is not None:
                ax[ind_y][ind_x].set_xlabel(xtitles[subplot-1], fontsize=12)
            if ytitles is not None:
                ax[ind_y][ind_x].set_ylabel(ytitles[subplot-1], fontsize=12)

            if show_legend:
#                ax[ind_y][ind_x].legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, prop={'size':20})
#                ax[ind_y][ind_x].legend(loc="upper right", bbox_to_anchor=[1, 1], ncol=2, prop={'size':18})
                ax[ind_y][ind_x].legend(loc="upper right", bbox_to_anchor=[1, 1], prop={'size':12})

            for tick in (ax[ind_y][ind_x].get_xticklabels() + ax[ind_y][ind_x].get_yticklabels()):
                #tick.set_fontsize(17)
                tick.set_fontsize(12)
            ax[ind_y][ind_x].grid()

            count_plot = 0
            subplot += 1
            xmin = 9e30
            xmax = -9e30
            ymin = 9e30
            ymax = -9e30

    if title != "":
        plt.suptitle(title)

    # plt.tight_layout()
    f.set_tight_layout(True)
    plt.subplots_adjust(hspace=.2)
#    plt.subplots_adjust(top=0.90)

    if show:
        plt.show()
        return

    if save_name != "":
        owner = os.getenv('USR')
        # homefold = os.path.join(os.sep, 'u', owner)
        homefold = os.curdir
        # print(owner)
        # print(homefold)
        # print(homefold + os.sep + 'figures/')
        pathlib.Path(homefold + os.sep + 'figures/').mkdir(parents=True,
                                                       exist_ok=True)
        path=homefold + os.sep + 'figures/'
        plt.savefig(path+save_name)
