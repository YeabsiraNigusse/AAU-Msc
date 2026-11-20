"""Feature names and the derived geometry feature shared by training and serving."""

NUMERIC = [
    "relative_compactness", "surface_area", "wall_area", "roof_area",
    "overall_height", "glazing_area",
]
CATEGORICAL = ["orientation", "glazing_area_distribution"]
FEATURES = NUMERIC + CATEGORICAL
TARGETS = ["heating_load", "cooling_load"]


def add_roof_fraction(frame):
    """Express roof area as a share of the total building surface."""
    return frame.assign(roof_fraction=frame["roof_area"] / frame["surface_area"])
