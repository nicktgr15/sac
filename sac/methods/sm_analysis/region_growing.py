import numpy
from matplotlib.patches import Rectangle
from sac.model.audacity_label import AudacityLabel
from mpmath import e
import peakutils
from scipy.ndimage import uniform_filter
from sympy import Symbol

import matplotlib

matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

STEP = 1
REGION_MAX_SIZE = 35
PEAK_THRESHOLD = 0.5


def _boost(input_x):
    x = Symbol('x')
    expr = 0.01 + e ** (-x / 6 + 3)
    return expr.subs(x, input_x)


def calculate_region_sums_and_boundaries(start_position, sm, region_max_size=REGION_MAX_SIZE):
    """

    With the same starting point scan multiple growing regions(up to REGION_MAX_SIZE, calculate the sums and the
    region boundaries

    :param start_position:
    :param sm:
    :param region_max_size:
    :return:
    """

    region_sums = []
    region_stds = []
    region_means = []
    region_boundaries = []

    for i in range(1, region_max_size):
        start_row = start_position
        end_row = start_position + i * STEP + 1

        start_col = start_position
        end_col = start_position + i * STEP + 1

        region_boundaries.append([start_row, end_row, start_col, end_col])

        # print "%s:%s, %s:%s" % (start_row, end_row, start_col, end_col)

        subarray = sm[start_row: end_row, start_col: end_col]
        region_sums.append(numpy.sum(subarray))
        region_stds.append(numpy.std(subarray))
        region_means.append(numpy.mean(subarray))

        if end_row == sm.shape[0]:
            break

    return region_sums, region_stds, region_means, region_boundaries


def identify_homogeneous_region(region_sums, region_stds, region_means, region_boundaries, debug=False,
                                peak_threshold=PEAK_THRESHOLD):
    """

    :param region_sums:
    :param region_boundaries:
    :param peak_threshold:
    :param debug:
    :return: detected boundaries [start_row, end_row, start_col, end_col]
    """

    # # calculate first and second derivatives
    diff1 = numpy.diff(region_stds)
    #
    # rate_of_change = []
    # rate_of_change2 = []
    #
    # for i in range(0, len(region_sums)-4):
    #     rate_of_change.append((region_sums[i+4] - region_sums[i])/4)
    #
    # for i in range(0, len(rate_of_change)-4):
    #     rate_of_change2.append((rate_of_change[i+4] - rate_of_change[i])/4)
    #
    # diff2 = numpy.diff(diff1)
    #
    # peaks = peakutils.indexes(rate_of_change2, thres=peak_threshold)
    #
    # if len(peaks) > 0:
    #     # print peaks
    #     # print [diff2[peak_position] for peak_position in peaks]
    #     peak_values = [rate_of_change2[peak_position] for peak_position in peaks]
    #
    #     # print peak_values
    #     argmax = numpy.argmax(peak_values)
    #     boundaries = region_boundaries[peaks[argmax]]
    # else:
    #     boundaries = region_boundaries[-1]
    #

    if len(diff1) > 3:
        max_index = numpy.argmax(diff1[3:]) + 2
        boundaries = region_boundaries[max_index]

        if debug:
            plt.figure()
            # plt.plot(peaks, [rate_of_change2[p] for p in peaks], 'o')
            plt.plot(region_stds)
            plt.plot(diff1, label="diff1")
            plt.plot(max_index, diff1[max_index], 'x')
            # plt.plot(diff2, label="diff2")
            # plt.plot(rate_of_change)
            # plt.plot(rate_of_change2)
            plt.show()

    else:
        boundaries = region_boundaries[-1]



    segment = [boundaries[0], boundaries[1]]

    return boundaries, segment


def get_segments(timestamps, sm, thresh=PEAK_THRESHOLD, draw=False, debug=False):
    if draw:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    segments = []
    audacity_labels = []

    x = 0
    while x < sm.shape[0]:

        region_sums, region_stds, region_means, region_boundaries = calculate_region_sums_and_boundaries(x, sm)
        b, segment = identify_homogeneous_region(region_sums, region_stds, region_means, region_boundaries, debug, thresh)

        if draw:
            ax.add_patch(Rectangle((b[0], b[2]), b[1] - b[0], b[1] - b[0], fill=False, edgecolor='b'))

        segments.append(segment)
        # use as a new starting point the end of the detected segment
        x = b[1]

    if draw:
        ax.imshow(sm, cmap=plt.cm.gray)
        plt.show()

    segments[-1] = [segments[-1][0], segments[-1][1] - 1]
    for segment in segments:
        audacity_labels.append(AudacityLabel(timestamps[segment[0]], timestamps[segment[1]], "-"))

    return audacity_labels
