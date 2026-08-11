# imp.py
# Convert a raw point difference to IMPs using the standard WBF table.

IMP_BREAKPOINTS = [
    (10, 0),
    (40, 1),
    (80, 2),
    (120, 3),
    (160, 4),
    (210, 5),
    (260, 6),
    (310, 7),
    (360, 8),
    (420, 9),
    (490, 10),
    (590, 11),
    (740, 12),
    (890, 13),
    (1090, 14),
    (1290, 15),
    (1490, 16),
    (1740, 17),
    (1990, 18),
    (2240, 19),
    (2490, 20),
    (2990, 21),
    (3490, 22),
    (3990, 23),
    (float('inf'), 24),
]

def points_to_imps(point_diff: int) -> int:
    """
    Convert an absolute point difference to IMPs based on the standard table.
    """
    if point_diff < 0:
        point_diff = abs(point_diff)
    for max_points, imps in IMP_BREAKPOINTS:
        if point_diff <= max_points:
            return imps
    return 24  # fallback
