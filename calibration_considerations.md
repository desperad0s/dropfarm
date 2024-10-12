# Calibration Considerations

| Approach | Description | Used in Current Implementation | Pros | Cons | How to Implement/Revert |
|----------|-------------|--------------------------------|------|------|-------------------------|
| Linear Interpolation | Simple linear mapping between screen coordinates | No | - Simple to implement<br>- Fast computation | - May not handle non-linear distortions well | Implement: Use `numpy.interp` for x and y separately<br>Revert: Remove interpolation, use direct mapping |
| Polynomial Regression | Fits a polynomial function to the calibration points | No | - Can capture non-linear distortions<br>- Flexible degree of polynomial | - May overfit with high degree polynomials<br>- Requires more calibration points for higher degrees | Implement: Use `numpy.polyfit` and `numpy.poly1d`<br>Revert: Remove polynomial fitting |
| Thin Plate Spline | Interpolation method that minimizes bending energy | No | - Handles complex non-linear distortions<br>- Works well with irregular point distributions | - Computationally expensive<br>- May introduce artifacts with sparse data | Implement: Use `scipy.interpolate.ThinPlateSpline`<br>Revert: Remove TPS implementation |
| Cubic Spline Interpolation | Piecewise cubic polynomial interpolation | Yes | - Smooth interpolation<br>- Handles non-linear distortions well<br>- Relatively fast computation | - May introduce oscillations with non-monotonic data | Implement: Already implemented<br>Revert: Replace with simpler method like linear interpolation |
| Radial Basis Function | Interpolation using radially symmetric functions | No | - Handles multi-dimensional data well<br>- Can capture complex patterns | - Can be sensitive to parameter choices<br>- May be computationally expensive | Implement: Use `scipy.interpolate.Rbf`<br>Revert: Remove RBF implementation |
| Machine Learning (e.g., Neural Network) | Learn the mapping using a neural network | No | - Can capture very complex patterns<br>- Potentially most accurate for large datasets | - Requires large amount of training data<br>- Complex to implement and tune<br>- Computationally expensive | Implement: Use a library like TensorFlow or PyTorch<br>Revert: Remove ML model and related code |

## Current Approach: Cubic Spline Interpolation

We chose cubic spline interpolation for its balance of accuracy and computational efficiency. It handles non-linear distortions well without introducing excessive complexity.

## Next Steps:

1. Test the current implementation thoroughly across different browsers and screen sizes.
2. If issues persist, consider implementing Thin Plate Spline interpolation for potentially better handling of complex distortions.
3. If accuracy is still insufficient, explore machine learning approaches, starting with a simple neural network.

## Testing Plan:

1. Perform calibration in Chrome (regular session).
2. Record and playback a routine in Chrome.
3. Switch to Edge (or another browser) without recalibrating.
4. Attempt to playback the same routine in Edge.
5. If playback in Edge is inaccurate, perform a new calibration in Edge and test again.
6. Repeat steps 1-5 with incognito/private browsing sessions.
7. Document any discrepancies or issues observed between browsers or between regular and incognito sessions.
