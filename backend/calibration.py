import numpy as np
from scipy.interpolate import interp2d
import logging

logger = logging.getLogger(__name__)

class Calibrator:
    def __init__(self, browser_calibration=None, recorder_calibration=None, player_calibration=None):
        self.browser_calibration = np.array(browser_calibration or [])
        self.recorder_calibration = np.array(recorder_calibration or [])
        self.player_calibration = np.array(player_calibration or [])
        self.expected_points = np.array([
            (0, 0), (0.5, 0), (1, 0),
            (0, 0.5), (0.5, 0.5), (1, 0.5),
            (0, 1), (0.5, 1), (1, 1)
        ])
        self.browser_interp_x = self.browser_interp_y = None
        self.recorder_interp_x = self.recorder_interp_y = None
        self.player_interp_x = self.player_interp_y = None

    def is_calibrated(self):
        return (len(self.browser_calibration) == len(self.expected_points) and
                len(self.recorder_calibration) == len(self.expected_points) and
                len(self.player_calibration) == len(self.expected_points))

    def calibrate(self):
        if not self.is_calibrated():
            logger.warning("Not all calibration data is available")
        self.browser_interp_x, self.browser_interp_y = self._create_interpolators(self.browser_calibration)
        self.recorder_interp_x, self.recorder_interp_y = self._create_interpolators(self.recorder_calibration)
        self.player_interp_x, self.player_interp_y = self._create_interpolators(self.player_calibration)

    def transform_coordinate(self, x, y, mode='record'):
        if not self.is_calibrated():
            logger.info(f"No calibration applied: ({x}, {y})")
            return x, y

        # First, transform through browser calibration
        x_browser, y_browser = self._apply_interpolation(x, y, self.browser_interp_x, self.browser_interp_y)
        
        if mode == 'record':
            x_final, y_final = self._apply_interpolation(x_browser, y_browser, self.recorder_interp_x, self.recorder_interp_y)
        elif mode == 'play':
            x_final, y_final = self._apply_interpolation(x_browser, y_browser, self.player_interp_x, self.player_interp_y)
        else:
            raise ValueError("Mode must be 'record' or 'play'")

        logger.info(f"Calibration applied: ({x}, {y}) -> ({x_final}, {y_final})")
        return x_final, y_final

    def _create_interpolators(self, calibration_points):
        if len(calibration_points) < len(self.expected_points):
            logger.warning(f"Insufficient calibration points: {len(calibration_points)}")
            return None, None
        x = calibration_points[:, 0]
        y = calibration_points[:, 1]
        zx = self.expected_points[:, 0]
        zy = self.expected_points[:, 1]
        return interp2d(x, y, zx, kind='linear'), interp2d(x, y, zy, kind='linear')

    def _apply_interpolation(self, x, y, interp_x, interp_y):
        if interp_x is None or interp_y is None:
            return x, y
        return float(interp_x(x, y)), float(interp_y(x, y))

    def to_dict(self):
        return {
            'browser_calibration_points': self.browser_calibration.tolist(),
            'recorder_calibration_points': self.recorder_calibration.tolist(),
            'player_calibration_points': self.player_calibration.tolist(),
            'expected_points': self.expected_points.tolist()
        }

    @classmethod
    def from_dict(cls, data):
        calibrator = cls()
        calibrator.browser_calibration = np.array(data['browser_calibration_points'])
        calibrator.recorder_calibration = np.array(data['recorder_calibration_points'])
        calibrator.player_calibration = np.array(data['player_calibration_points'])
        calibrator.expected_points = np.array(data['expected_points'])
        if calibrator.is_calibrated():
            calibrator.calibrate()
        return calibrator
