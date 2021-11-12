# SimplePendulumParametersMeasurement_Cameras
This project come from question D of 2021 NUEDC (2021 National Undergraduate Electronics Design Contest).

<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/SystemDiagram.png" width="400" height="300" alt="System Diagram"/></div>


Updating ... ...

## Requirements
* python3
* OpenCV4
* module "math"
* module "numpy"
* module "urllib"
* module "time"

* module "peakutils"
* module "scipy"
* module "matplotlib"

* module "threading"


## Result Preview


## Introduction


## Methods
The key of this measurement method is using the sin function to fit scatters.
Let's do a simple derivation.
$$T = 2 \times \pi \times \sqrt(\frac{L}{g}) \quad\Rightarrow\quad  L = g  \times (\frac{T}{2 \times \pi })^2$$

* $T$ is the period of the simple pendulum, $L$ is the line length of the simple pendulum, $g$ is the acceleration of gravity (All units are in the International System of Units).

To touch the question's goal ( $L_{error} \leq 2cm$ ), the period error should less than 0.0163s (It's easy to prove that longer line length means smaller period error, otherwise the length error will not meet the requirement.)
$$T = 2 \times \pi \times \sqrt(\frac{L}{g})$$
$$=2 \times \pi \times \sqrt(\frac{1.5\pm0.02}{9.8}) \quad\approx\quad 2.458\pm0.016s$$

Actually, it's hard to achieve this frame rate (We need to get a 62.5fps(1/0.016) image, otherwise we may miss the key frame and get inaccurate peak positions). So we must to use an sin function to fit this group of scatters. All of us learn that the change of the horizontal position of a simple pendulum can be regarded as a simple harmonic vibration, that is to say, x is a sin function with respect to time t

<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/FitFunction.png" width="400" height="300" alt="Fit Function"/></div>

## Attentions


## Conclusion


## Reference

