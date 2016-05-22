import numpy
from matplotlib.patches import Rectangle
from sac.model.audacity_label import AudacityLabel
from mpmath import e
import peakutils
import matplotlib
from sympy import Symbol

matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

STEP = 1
REGION_MAX_SIZE = 35
PEAK_THRESHOLD = 0.1


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
    region_boundaries = []

    for i in range(1, region_max_size):
        start_row = start_position
        end_row = start_position + i * STEP + 1

        start_col = start_position
        end_col = start_position + i * STEP + 1

        region_boundaries.append([start_row, end_row, start_col, end_col])

        # print "%s:%s, %s:%s" % (start_row, end_row, start_col, end_col)

        subarray = sm[start_row: end_row, start_col: end_col]
        subarray_sum = numpy.sum(subarray)
        region_sums.append(subarray_sum)

        if end_row == sm.shape[0]:
            break

    return region_sums, region_boundaries


def identify_homogeneous_region(region_sums, region_boundaries, peak_threshold = PEAK_THRESHOLD, debug=False):
    """

    :param region_sums:
    :param region_boundaries:
    :param peak_threshold:
    :param debug:
    :return: detected boundaries [start_row, end_row, start_col, end_col]
    """
    # calculate first and second derivatives
    diff1 = numpy.diff(region_sums)
    diff2 = numpy.diff(diff1)

    peaks = peakutils.indexes(diff2, thres=peak_threshold)

    if len(peaks) > 0:
        # print peaks
        # print [diff2[peak_position] for peak_position in peaks]
        peak_values = [_boost(peak_position) * diff2[peak_position] for peak_position in peaks]
        # print peak_values
        argmax = numpy.argmax(peak_values)
        boundaries = region_boundaries[peaks[argmax]]
    else:
        boundaries = region_boundaries[-1]

    if debug:
        plt.figure()
        plt.plot(region_sums)
        plt.plot(diff1)
        plt.plot(diff2)
        plt.show()

    segment = [boundaries[0], boundaries[1]]

    return boundaries, segment


def get_regions(timestamps, sm, draw=False, debug=False):

    if draw:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    segments = []
    audacity_labels = []

    x = 0
    while x < sm.shape[0]:

        region_sums, region_boundaries = calculate_region_sums_and_boundaries(x, sm)
        b, segment = identify_homogeneous_region(region_sums, region_boundaries, debug)

        if draw:
            ax.add_patch(Rectangle((b[0], b[2]), b[1] - b[0], b[1] - b[0], fill=False, edgecolor='b'))

        segments.append(segment)
        # use as a new starting point the end of the detected segment
        x = b[1]

    if draw:
        ax.imshow(sm, cmap=plt.cm.gray)
        plt.show()

    segments[-1] = [segments[-1][0], segments[-1][1]-1]
    for segment in segments:
        audacity_labels.append(AudacityLabel(timestamps[segment[0]], timestamps[segment[1]], "-"))

    return audacity_labels
