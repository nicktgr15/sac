import numpy as np


def find_peaks(series_data, sliding_window_size=20, percentage_of_sliding_window_votes=0.7):

    ranking = np.zeros(len(series_data))

    for i in range(len(series_data)):
        window_data = series_data[i:i+sliding_window_size]

        ranking[i + np.argmax(window_data)] += 1

    ranking = ranking > percentage_of_sliding_window_votes * sliding_window_size

    peaks = np.where(ranking >= 1)[0].tolist()
    return peaks
