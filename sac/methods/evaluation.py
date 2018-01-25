
def get_classification_based_on_time_range(start_time, end_time, labels):
    for label in labels:
        if start_time >= label.start_seconds and end_time < label.end_seconds:
            return label.label
    raise Exception("can't find label matching start %s and end time %s" % (start_time, end_time))


def frame_level_evaluation(ground_truth_labels, detected_labels, frame_sec=0.01, verbose=False):

    correctly_classified = 0
    total_frames = 0
    incorrectly_classified = 0

    for ground_truth_label in ground_truth_labels:
        current = ground_truth_label.start_seconds
        while current < ground_truth_label.end_seconds - frame_sec:
            total_frames += 1
            try:
                if ground_truth_label.label == get_classification_based_on_time_range(current, current+frame_sec,
                                                                                      detected_labels):
                    correctly_classified += 1
                else:
                    incorrectly_classified += 1

            except Exception as e:
                pass

            current += frame_sec

    if verbose:
        print(correctly_classified)
        print(incorrectly_classified)
        print(total_frames)

    precision = correctly_classified / float(correctly_classified + incorrectly_classified)
    recall = correctly_classified / float(total_frames)
    fs = (2 * precision * recall) / (precision + recall)

    if verbose:
        print("FRAME LEVEL EVALUATION => Precision: %s Recall: %s F1 Score: %s" % (precision, recall, fs))

    return precision, recall, fs


def segments_precision_recall_fs(ground_truth_segments, detected_segments, tolerance, verbose=False):
    if verbose:
        print("Ground truth segments: %s" % len(ground_truth_segments))
        print("Detected segments: %s" % len(detected_segments))

    correctly_detected_transition_points = 0

    for i in range(0, len(ground_truth_segments)):
        ground_segment = ground_truth_segments[i]
        for detected_segment in detected_segments:
            if abs(detected_segment.start_seconds - ground_segment.start_seconds) <= tolerance \
                    and abs(detected_segment.end_seconds - ground_segment.end_seconds) <= tolerance \
                    and detected_segment.label == ground_segment.label:
                        correctly_detected_transition_points += 1
                        break

    if verbose:
        print("Correctly detected segments: %s" % correctly_detected_transition_points)

    if len(detected_segments) > 0:
        precision = correctly_detected_transition_points / float(len(detected_segments)-1)
    else:
        precision = 0
    if len(ground_truth_segments) > 0:
        recall = correctly_detected_transition_points / float(len(ground_truth_segments)-1)
    else:
        recall = 0
    if precision + recall != 0:
        fs = (2 * precision * recall) / (precision + recall)
    else:
        fs = 0
    if verbose:
        print("SEGMENT LEVEL EVALUATION => Precision: %s Recall: %s F1 Score: %s" % (precision, recall, fs))

    return precision, recall, fs


def transition_points_precision_recall_fs(ground_truth_segments, detected_segments, tolerance, verbose=False):
    if verbose:
        print("Ground truth segments: %s" % len(ground_truth_segments))
        print("Detected segments: %s" % len(detected_segments))

    correctly_detected_transition_points = 0

    for i in range(0, len(ground_truth_segments)):
        ground_segment = ground_truth_segments[i]
        for detected_segment in detected_segments:
            if abs(detected_segment.start_seconds - ground_segment.end_seconds) <= tolerance:
                correctly_detected_transition_points += 1
                break

    if verbose:
        print("Correctly detected transition points: %s" % correctly_detected_transition_points)

    if len(detected_segments) > 0:
        precision = correctly_detected_transition_points / float(len(detected_segments)-1)
    else:
        precision = 0
    if len(ground_truth_segments) > 0:
        recall = correctly_detected_transition_points / float(len(ground_truth_segments)-1)
    else:
        recall = 0
    if precision + recall != 0:
        fs = (2 * precision * recall) / (precision + recall)
    else:
        fs = 0

    if verbose:
        print("SEGMENT LEVEL EVALUATION => Precision: %s Recall: %s F1 Score: %s" % (precision, recall, fs))

    return precision, recall, fs