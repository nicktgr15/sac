
def transition_points_precision_recall_fs(ground_truth_segments, detected_segments, tolerance):
    print "Ground truth segments: %s" % len(ground_truth_segments)
    print "Detected segments: %s" % len(detected_segments)

    correctly_detected_transition_points = 0

    for i in range(0, len(ground_truth_segments) - 1):
        ground_segment = ground_truth_segments[i]
        for detected_segment in detected_segments:
            if abs(detected_segment.start_seconds - ground_segment.end_seconds) <= tolerance:
                correctly_detected_transition_points += 1
                break

    print "Correctly detected transition points: %s" % correctly_detected_transition_points

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
    print "SEGMENT LEVEL EVALUATION => Precision: %s Recall: %s F1 Score: %s" % (precision, recall, fs)

    return precision, recall, fs

