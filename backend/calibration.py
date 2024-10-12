import numpy as np
from scipy.interpolate import interp1d
import logging

logger = logging.getLogger(__name__)

class Calibrator:
    def __init__(self, calibration_data=None):
        self.expected_points = np.array([
            (0, 0), (0.25, 0), (0.5, 0), (0.75, 0), (1, 0),
            (0, 0.25), (0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (1, 0.25),
            (0, 0.5), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5), (1, 0.5),
            (0, 0.75), (0.25, 0.75), (0.5, 0.75), (0.75, 0.75), (1, 0.75),
            (0, 1), (0.25, 1), (0.5, 1), (0.75, 1), (1, 1)
        ])
        self.calibration_points = np.array(calibration_data or [], dtype=float)
        self.interp_x = None
        self.interp_y = None

    def add_calibration_point(self, x, y):
        self.calibration_points = np.append(self.calibration_points, [(float(x), float(y))], axis=0)

    def is_calibrated(self):
        return len(self.calibration_points) == len(self.expected_points)

    def calibrate(self):
        if not self.is_calibrated():
            raise ValueError("Not enough calibration points")
        
        # Normalize calibration points
        self.calibration_points[:, 0] /= np.max(self.calibration_points[:, 0])
        self.calibration_points[:, 1] /= np.max(self.calibration_points[:, 1])

        # Sort points and remove duplicates
        sorted_indices = np.lexsort((self.calibration_points[:, 1], self.calibration_points[:, 0]))
        sorted_calibration = self.calibration_points[sorted_indices]
        sorted_expected = self.expected_points[sorted_indices]

        # Remove duplicates while keeping the last occurrence
        _, unique_indices = np.unique(sorted_calibration[:, 0], return_index=True)
        unique_indices = sorted(unique_indices)
        
        unique_calibration = sorted_calibration[unique_indices]
        unique_expected = sorted_expected[unique_indices]

        # Ensure we have at least 4 points for cubic interpolation
        if len(unique_calibration) < 4:
            logger.warning("Not enough unique points for cubic interpolation. Falling back to linear.")
            kind = 'linear'
        else:
            kind = 'cubic'

        # Create interpolation functions
        self.interp_x = interp1d(unique_calibration[:, 0], unique_expected[:, 0], kind=kind, fill_value='extrapolate')
        self.interp_y = interp1d(unique_calibration[:, 1], unique_expected[:, 1], kind=kind, fill_value='extrapolate')

    def transform_coordinate(self, x, y):
        if not self.is_calibrated() or self.interp_x is None or self.interp_y is None:
            logger.info(f"No calibration applied: ({x}, {y})")
            return x, y

        # Normalize input coordinates
        x_norm = x / 1280  # Assuming 1280 is max width
        y_norm = y / 720   # Assuming 720 is max height

        transformed_x = float(self.interp_x(x_norm)) * 1280
        transformed_y = float(self.interp_y(y_norm)) * 720

        logger.info(f"Calibration applied: ({x}, {y}) -> ({transformed_x}, {transformed_y})")
        return transformed_x, transformed_y

    def to_dict(self):
        return {
            'calibration_points': self.calibration_points.tolist(),
            'expected_points': self.expected_points.tolist()
        }

    @classmethod
    def from_dict(cls, data):
        calibrator = cls()
        calibrator.calibration_points = np.array(data['calibration_points'])
        calibrator.expected_points = np.array(data['expected_points'])
        if calibrator.is_calibrated():
            calibrator.calibrate()
        return calibrator
