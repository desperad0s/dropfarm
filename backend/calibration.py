import numpy as np
from scipy.interpolate import griddata

class Calibrator:
    def __init__(self, calibration_data=None):
        self.expected_points = [
            (0, 0), (1280, 0), (0, 720), (1280, 720), (640, 360)
        ]
        self.calibration_points = calibration_data or []

    def add_calibration_point(self, x, y):
        self.calibration_points.append((x, y))

    def is_calibrated(self):
        return len(self.calibration_points) == len(self.expected_points)

    def transform_coordinate(self, x, y):
        if not self.is_calibrated():
            return x, y  # Return original coordinates if not calibrated

        points = np.array(self.calibration_points)
        values = np.array(self.expected_points)

        transformed_x = griddata(points, values[:, 0], (x, y), method='linear')
        transformed_y = griddata(points, values[:, 1], (x, y), method='linear')

        return transformed_x[0], transformed_y[0]

    def to_dict(self):
        return {
            'calibration_points': self.calibration_points,
            'expected_points': self.expected_points
        }

    @classmethod
    def from_dict(cls, data):
        calibrator = cls()
        calibrator.calibration_points = data['calibration_points']
        calibrator.expected_points = data['expected_points']
        return calibrator