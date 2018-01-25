
from scipy.ndimage import uniform_filter
from scipy.signal import find_peaks_cwt
from scipy.spatial.distance import pdist, squareform, cdist
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['xtick.labelsize'] = 8


def calculate_similarity_matrix(feature_vectors, metric="cosine", subarray_size=None):

    if subarray_size is None:
        subarray_size = feature_vectors.shape[0]

    size = feature_vectors.shape[0]
    sm = np.zeros((size, size))

    for i in range(0, feature_vectors.shape[0]):
        distances_forward = cdist([feature_vectors[i]], feature_vectors[i:i + subarray_size, :], metric=metric)
        distances_forward = np.squeeze(distances_forward)

        back_start = i-subarray_size
        if back_start < 0:
            back_start = 0

        distances_backward = cdist([feature_vectors[i]], feature_vectors[back_start:i, :], metric=metric)
        distances_backward = np.squeeze(distances_backward)

        if len(distances_forward.shape) != 0:
            sm[i, i:i+distances_forward.shape[0]] = distances_forward
        else:
            sm[i, i:i+1] = distances_forward

        if len(distances_backward.shape) != 0:
            sm[i, i-distances_backward.shape[0]:i] = distances_backward
        else:
            sm[i, i-1:i] = distances_backward

    return sm

    #
    # if subarray_size is None:
    #     subarray_size = feature_vectors.shape[0]
    #
    # size = feature_vectors.shape[0]
    # sm = np.zeros((size, size))
    #
    # for i in range(0, size, subarray_size):
    #     subarray_distances = pdist(feature_vectors[i:i + subarray_size * 2], metric=metric)
    #     subarray_distances = squareform(subarray_distances)
    #     sm[i:i + subarray_distances.shape[0], i:i + subarray_distances.shape[0]] = subarray_distances
    # return sm


def get_checkerboard_matrix(kernel_width):

    """
    example matrix for width = 2

    -1  -1    1   1
    -1  -1    1   1
     1   1   -1  -1
     1   1   -1  -1

    :param kernel_width:
    :return:
    """

    return np.vstack((
        np.hstack((
            -1 * np.ones((kernel_width, kernel_width)), np.ones((kernel_width, kernel_width))
        )),
        np.hstack((
            np.ones((kernel_width, kernel_width)), -1 * np.ones((kernel_width, kernel_width))
        ))
    ))


def checkerboard_matrix_filtering(similarity_matrix, kernel_width, peak_range):
    """
    Moving the checkerboard matrix over the main diagonal of the similarity matrix one sample at a time.

    :param similarity_matrix:
    :param peak_range: the number of samples in which the peak detection algorithms finds a peak (TODO:clarify)
    :param kernel_width: the size of one quarter of the checkerboard matrix
    :return: peaks and convolution values
    """

    checkerboard_matrix = get_checkerboard_matrix(kernel_width)

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

    peaks = find_peaks_cwt(convolution_values, np.arange(1, peak_range))
    peaks = [0] + peaks + [len(convolution_values)-1]
    return peaks, convolution_values


def calculate_segment_start_end_times_from_peak_positions(peaks, timestamps):
    window_in_seconds = get_window_in_seconds(timestamps)
    segments = []
    for i in range(0, len(peaks) - 1):
        segments.append([peaks[i] * window_in_seconds, peaks[i + 1] * window_in_seconds])

    return segments


def get_window_in_seconds(timestamps):
    return timestamps[1] - timestamps[0]


def draw_similarity_matrix(similarity_matrix, peaks, convolution_values, image_filename, timestamps):
    plt.figure()
    ax1 = plt.subplot2grid((9, 1), (0, 0), rowspan=8)
    plt.imshow(similarity_matrix, cmap=plt.cm.gray)

    ax2 = plt.subplot2grid((9, 1), (8, 0), sharex=ax1)
    plt.plot(convolution_values)
    plt.plot(peaks, [convolution_values[p] for p in peaks], 'x')

    ticks = [i for i in range(0, len(convolution_values), int(len(convolution_values) / 7))]

    plt.xticks(ticks, ["%.0f" % timestamps[t] for t in ticks])
    plt.savefig(image_filename, bbox_inches='tight')


def get_segments(feature_vectors, timestamps, kernel_width, peak_range, filter_width, save_image=False,
                 image_filename="similarity_matrix.png", subarray_size=None):

    sm = calculate_similarity_matrix(feature_vectors, subarray_size=subarray_size)

    sm = uniform_filter(sm, filter_width)

    peaks, convolution_values = checkerboard_matrix_filtering(sm, kernel_width, peak_range)

    if save_image:
        draw_similarity_matrix(sm, peaks, convolution_values, image_filename, timestamps)

    return calculate_segment_start_end_times_from_peak_positions(peaks, timestamps)



