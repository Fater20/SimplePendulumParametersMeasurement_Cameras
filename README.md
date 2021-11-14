# SimplePendulumParametersMeasurement_Cameras

This project come from question D of 2021 NUEDC (2021 National Undergraduate Electronics Design Contest).

<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/SystemDiagram.png" width="400" height="300" alt="System Diagram"/></div>
<div align=center>Figure 1. System Diagram</div>

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

### Length Measurement

The key of this measurement method is using the sin function to fit scatters.
Let's do a simple derivation.
$$T = 2 \times \pi \times \sqrt(\frac{L}{g}) \quad\Rightarrow\quad  L = g  \times (\frac{T}{2 \times \pi })^2$$

* $T$ is the period of the simple pendulum, $L$ is the line length of the simple pendulum, $g$ is the acceleration of gravity (All units are in the International System of Units).

To touch the question's goal ( $L_{error} \leq 2cm$ ), the period error should less than 0.0163s (It's easy to prove that longer line length means smaller period error, otherwise the length error will not meet the requirement.)
$$T = 2 \times \pi \times \sqrt(\frac{L}{g})$$
$$=2 \times \pi \times \sqrt(\frac{1.5\pm0.02}{10}) \quad\approx\quad 2.458\pm0.016s$$

Actually, it's hard to achieve this frame rate (We need to get a $62.5fps$(1/0.016) image, otherwise we may miss the key frame and get inaccurate peak positions). So we must to use an sin function to fit this group of scatters. All of us learn that the change of the horizontal position of a simple pendulum can be regarded as a simple harmonic vibration, that is to say, horizontal position x is a sin function with respect to time t.

$$ x = A \times sin(\omega \times t + \phi ) + x_0 $$
* $A$ is the amplitude of the horizontal displacement of the simple pendulum, $\omega$ is the angular frequency, $\phi$ is the initial phase, $x_0$ is the difference between the zero point of the image's x coordinate and the midpoint of the harmonic vibration.

After fitting, we can get a graph below(Figure 2). The green line is the fitted function, and scatters are the records of the horizontal position with two cameras.

<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/FitFunction.png" width="400" height="300" alt="Fitted Function"/></div>
<div align=center>Figure 2. Fitted Graph</div>
<br/>

At this point, we can already calculate the period very well. However, let's go back to the formula at the begining.

$$L = g  \times (\frac{T}{2 \times \pi })^2 \quad\Rightarrow\quad  L = g \times (\frac{1}{\omega})^2$$

To calculate the length $L$, we need a key parameter, the acceleration of gravity $g$, for which we use 10 in the calculation above. We can get a more accurate $g$ through analysing the measurement data. (There have a small difference between the end of the line and the centroid of the object. We can also correct it through analysing the measurement data.)
$$ L = g \times (\frac{1}{\omega})^2 + d$$
According to the data we record(Figure 3), we can calculate the real $g$ and difference $d$. Through our calculating, $g$ is about $9.802m/s^2$ and $d$ is about $0.0738m$.

Table 1. Data Analysis Table
<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/DataAnalysis.png" width="600" height="300" alt="data analysis"/></div>

<br/>
<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/Figure3.png" width="400" height="300" alt="g fitted graph"/></div>
<div align=center>Figure 3. 'g' Fitted Graph</div>

Using this method and parameters in subsequent measurements, we will find that we can measure the line length of the simple pendulum extremely accurately. The error may less than $2mm$, even at a fairly low frame rate(below $10fps$). It's amazing!

### Angle Measurement

The measurement of angle $\theta$ uses a simple method.

<div align=center><img src="https://github.com/Fater20/SimplePendulumParametersMeasurement_Cameras/blob/main/image/AngleMeasurementDiagram.png" width="300" height="300" alt="g fitted graph"/></div>
<div align=center>Figure 4. Angle Measurement Diagram</div> 

In the diagram above, $\theta$ is the angle that we need to measure. $A_1$ and $A_2$ are the horizontal displacement of the simple pendulum in the sight of Camera A and Camera B. It's easy to prove that
$$\theta = arctan(\frac{A_1}{A_2})$$
( The horizontal displacement of the simple pendulum is much smaller than the distance ( $1m$ ) between the pendulum and the camera, so we can ignore the difference between two cameras.)
And we can get $A_1$ and $A_2$ from the fitted sin function in the length measurement. 


## Attentions



## Conclusion



## Reference


