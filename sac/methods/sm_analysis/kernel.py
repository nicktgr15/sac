import math

from matplotlib.patches import Rectangle
from sac.model.audacity_label import AudacityLabel
from scipy.ndimage import uniform_filter
import numpy as np
from scipy.signal import find_peaks_cwt
import matplotlib.pyplot as plt
import peakutils


def get_segments(timestamps, sm, filter_width, kernel_width, thresh=0.25, draw=False):

    sm = uniform_filter(sm, filter_width)

    peaks, convolution_values = checkerboard_matrix_filtering(sm, kernel_width, thresh=thresh)

    if draw:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(0, len(peaks)-1):
            ax.add_patch(Rectangle((peaks[i], peaks[i]), peaks[i+1] - peaks[i], peaks[i+1] - peaks[i],
                                   fill=False, edgecolor='b'))

    segments = calculate_segment_start_end_times_from_peak_positions(peaks, timestamps)

    if draw:
        ax.imshow(sm, cmap=plt.cm.gray)
        plt.show()

    return segments


def calculate_segment_start_end_times_from_peak_positions(peaks, timestamps):
    window_in_seconds = get_window_in_seconds(timestamps)
    segments = []
    for i in range(0, len(peaks) - 1):
        segments.append(AudacityLabel(peaks[i] * window_in_seconds, peaks[i + 1] * window_in_seconds, "-"))

    return segments


def get_window_in_seconds(timestamps):
    return timestamps[1] - timestamps[0]


def get_gaussian_kernel(kernel_width, gaussian_param):

    quarter = np.ones((kernel_width, kernel_width))

    for i in range(0, quarter.shape[0]):
        for j in range(0, quarter.shape[1]):
            m = max([i, j])
            quarter[i, j] = math.exp(gaussian_param * (-m**2))

    return np.vstack((
        np.hstack((
            -1 * np.flipud(np.fliplr(quarter)), np.flipud(quarter)
        )),
        np.hstack((
            np.fliplr(quarter), -1 * quarter)
        ))
    )


def get_checkerboard_matrix(kernel_width, kernel_type="default", gaussian_param=0.1):

    """
    example matrix for width = 2

    -1  -1    1   1
    -1  -1    1   1
     1   1   -1  -1
     1   1   -1  -1

    :param kernel_type:
    :param kernel_width:
    :return:
    """

    if kernel_type is "gaussian":
        return get_gaussian_kernel(kernel_width, gaussian_param)

    if kernel_type is "default":
        return np.vstack((
            np.hstack((
                -1 * np.ones((kernel_width, kernel_width)), np.ones((kernel_width, kernel_width))
            )),
            np.hstack((
                np.ones((kernel_width, kernel_width)), -1 * np.ones((kernel_width, kernel_width))
            ))
        ))

    elif kernel_type is "bottom_right":
        return np.vstack((
            np.hstack((
                np.ones((kernel_width, kernel_width)), np.ones((kernel_width, kernel_width))
            )),
            np.hstack((
                np.ones((kernel_width, kernel_width)), -1 * np.ones((kernel_width, kernel_width))
            ))
        ))

    elif kernel_type is "top_left":
        return np.vstack((
            np.hstack((
                -1 * np.ones((kernel_width, kernel_width)), np.ones((kernel_width, kernel_width))
            )),
            np.hstack((
                np.ones((kernel_width, kernel_width)), np.ones((kernel_width, kernel_width))
            ))
        ))


def checkerboard_matrix_filtering(similarity_matrix, kernel_width, kernel_type="default", thresh=0.25):

    """
    Moving the checkerboard matrix over the main diagonal of the similarity matrix one sample at a time.

    :param kernel_type:
    :param thresh:
    :param similarity_matrix:
    :param kernel_width: the size of one quarter of the checkerboard matrix
    :return: peaks and convolution values
    """

    checkerboard_matrix = get_checkerboard_matrix(kernel_width, kernel_type)

    # The values calculated in this step are starting from the 'kernel_width' position and ending
    # at length - kernel_width
    d = []
    for i in range(0, similarity_matrix.shape[0] - 2 * kernel_width):
        base = similarity_matrix[i:i + kernel_width * 2, i:i + kernel_width * 2]
        d.append(np.sum(np.multiply(base, checkerboard_matrix)))

    # The missing values from 0 to kernel_width are calculated here
    top_left_d = []
    for i in range(0, kernel_width):
        base = similarity_matrix[0:i + kernel_width, 0:i + kernel_width]
        top_left_d.append(np.sum(np.multiply(base, checkerboard_matrix[kernel_width - i:, kernel_width - i:])))

    # The missing kernel_width values at the bottom right are set to 0
    convolution_values = top_left_d + d + [0 for i in range(0, kernel_width)]

    # peaks = find_peaks_cwt(convolution_values, np.arange(1, peak_range))
    peaks = peakutils.indexes(convolution_values, thres=thresh)

    peaks = [0] + list(peaks) + [len(convolution_values)-1]
    return peaks, convolution_values
