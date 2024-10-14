# Calibration Considerations

| Approach | Description | Used in Current Implementation | Pros | Cons | How to Implement/Revert |
|----------|-------------|--------------------------------|------|------|-------------------------|
| Linear Interpolation | Simple linear mapping between screen coordinates | No | - Simple to implement<br>- Fast computation | - May not handle non-linear distortions well | Implement: Use `numpy.interp` for x and y separately<br>Revert: Remove interpolation, use direct mapping |
| Bilinear Interpolation | Interpolation using a 2D surface | Yes | - Handles 2D space well<br>- Good balance of accuracy and simplicity<br>- Works well with different aspect ratios | - May not capture complex non-linear distortions | Implement: Use `scipy.interpolate.interp2d`<br>Revert: Replace with simpler method like linear interpolation |
| Cubic Spline Interpolation | Piecewise cubic polynomial interpolation | Previously Tried | - Smooth interpolation<br>- Handles non-linear distortions well | - May introduce oscillations with non-monotonic data<br>- Complexity in handling 2D space | Implement: Use `scipy.interpolate.interp2d` with `kind='cubic'`<br>Revert: Change to bilinear or remove interpolation |
| Thin Plate Spline | Interpolation method that minimizes bending energy | No | - Handles complex non-linear distortions<br>- Works well with irregular point distributions | - Computationally expensive<br>- May introduce artifacts with sparse data | Implement: Use `scipy.interpolate.Rbf` with thin plate spline<br>Revert: Remove TPS implementation |
| Polynomial Regression | Fits a polynomial function to the calibration points | No | - Can capture non-linear distortions<br>- Flexible degree of polynomial | - May overfit with high degree polynomials<br>- Requires more calibration points for higher degrees | Implement: Use `numpy.polyfit` and `numpy.poly1d`<br>Revert: Remove polynomial fitting |
| Radial Basis Function | Interpolation using radially symmetric functions | No | - Handles multi-dimensional data well<br>- Can capture complex patterns | - Can be sensitive to parameter choices<br>- May be computationally expensive | Implement: Use `scipy.interpolate.Rbf`<br>Revert: Remove RBF implementation |
| Machine Learning (e.g., Neural Network) | Learn the mapping using a neural network | No | - Can capture very complex patterns<br>- Potentially most accurate for large datasets | - Requires large amount of training data<br>- Complex to implement and tune<br>- Computationally expensive | Implement: Use a library like TensorFlow or PyTorch<br>Revert: Remove ML model and related code |

## Current Approach: Bilinear Interpolation

We chose bilinear interpolation for its balance of accuracy and computational efficiency. It handles different aspect ratios well, which is particularly important for 16:10 monitors. This method provides a good compromise between the simplicity of linear interpolation and the complexity of higher-order methods.

## Previously Tried: Cubic Spline Interpolation

We previously attempted to use cubic spline interpolation, which offered smooth interpolation and handled non-linear distortions well. However, it introduced complexities in handling 2D space and potential issues with non-monotonic data.

## Next Steps:

1. Thoroughly test the current bilinear interpolation implementation across different browsers and screen sizes.
2. If issues persist, consider implementing a more sophisticated method like Thin Plate Spline interpolation, which might handle complex distortions better.
3. Implement a calibration quality check to ensure the accuracy of the calibration process.
4. Consider adaptive calibration techniques that adjust based on the detected level of distortion.

## Testing Plan:

1. Perform calibration in multiple browsers (Chrome, Firefox, Edge) on different screen sizes and aspect ratios.
2. Record a routine in one browser and attempt to play it back in another.
3. Test with both 16:9 and 16:10 aspect ratios to ensure compatibility.
4. Implement visual feedback during playback to show both the intended and actual click locations.
5. Develop a quantitative measure of calibration accuracy and use it to compare different methods.
