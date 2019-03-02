<template>
  <div id="computation">
    <vue-markdown>
# Ballistics Computation

## Program

There is a Python program to calculate the trajectory of a sphere, taking into account atmospheric and wave drag.  Given a set of known factors, this calculates an unknown parameter, usually the power density of the gunpowder used.

See the [GitHub repository](https://github.com/manthey/ballistics) for the source code and requirements for the program.

## Basic Algorithm
    </vue-markdown>
    <figure>
      <img src="/accelfig.gif"/>
      <figcaption>Acceleration on a Projectile</figcaption>
    </figure>
    <vue-markdown>
The basic premise is simple: knowing the mass of the powder charge and the power density of the powder, we know how much energy is imparted to a projectile of a known mass and diameter.  This starts the projectile moving at a specific initial velocity and at a specified elevation angle.

The program then steps through time in small increments, and, for each point calculates the atmospheric and wave drag and the acceleration of gravity (see figure [Stone, 1758, p. 148](/references?refkey=stone1758)).  This changes the projectiles velocity.  The calculation steps continue until the projectile reaches an expected destination (usually hitting the ground).

The process by which the projectile gains the initial velocity is called interior ballistics, and is not covered by this program.  This means that all of the factors of friction, windage, wadding, powder chamber shape, touch-hole size, bore length, and other gun tube parameters are lumped into a single "power factor" fr the gunpowder.

Each of the major points within the calculation is discussed below:

## Numerical Methods

To calculate the trajectory, used the [Runge-Kutta method](http://mathworld.wolfram.com/Runge-KuttaMethod.html).  It would be simpler to calculate the acceleration at each point and just adjust the velocity based on this acceleration, and then the position based on the velocity.  By using the Runge-Kutta method, changes in acceleration are handled more accurately.  While each computation step is slower than the simple method, many fewer steps are necessary to get the same accuracy of results.

For any given position, the acceleration is calculated based on the position, velocity, atmospheric conditions, and other factors (see below for details).  This can be expressed as a function yielding the ordered pair:

$\left(a_{x_i}, a_{y_i}\right) = f\left(x_i, y_i, v_{x_i}, v_{y_i}\right)$

The simple method calculates each step using the equations:

$x_{i+1} = x_i + v_{x_i} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $y_{i+1} = y_i + v_{y_i} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $v_{x_{i+1}} = v_{x_i} + a_{x_i} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $v_{y_{i+1}} = v_{y_i} + a_{y_i} \Delta t$

where $\Delta t$ is the time step, $x_i$ and $y_i$ are the current position, $v_{x_i}$ and $v_{y_i}$ are the current velocity, and $a_{x_i}$ and $a_{y_i}$ are the current acceleration.

The Runge-Kutta method can be expressed many different ways.  The program uses the following set of equations:

$\Delta x_{i_1} = v_{x_i} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta y_{i_1} = v_{y_i} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{x_{i_1}} = a_{x_i} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{y_{i_1}} = a_{y_i} \Delta t$
$\left(a_{x_{i_1}}, a_{y_{i_1}}\right) = f\left(x_i+\dfrac{\Delta x_{i_1}}{2}, y_i+\dfrac{\Delta y_{i_1}}{2}, v_{x_i}+\dfrac{\Delta v_{x_{i_1}}}{2}, v_{y_i}+\dfrac{\Delta v_{y_{i_1}}}{2}\right)$
$\Delta x_{i_2} = \left(v_{x_i}+\dfrac{\Delta v_{x_{i_1}}}{2}\right) \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta y_{i_2} = \left(v_{y_i}+\dfrac{\Delta v_{y_{i_1}}}{2}\right) \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{x_{i_2}} = a_{x_{i_1}} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{y_{i_2}} = a_{y_{i_1}} \Delta t$
$\left(a_{x_{i_2}}, a_{y_{i_2}}\right) = f\left(x_i+\dfrac{\Delta x_{i_2}}{2}, y_i+\dfrac{\Delta y_{i_2}}{2}, v_{x_i}+\dfrac{\Delta v_{x_{i_2}}}{2}, v_{y_i}+\dfrac{\Delta v_{y_{i_2}}}{2}\right)$
$\Delta x_{i_3} = \left(v_{x_i}+\dfrac{\Delta v_{x_{i_2}}}{2}\right) \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta y_{i_3} = \left(v_{y_i}+\dfrac{\Delta v_{y_{i_2}}}{2}\right) \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{x_{i_3}} = a_{x_{i_2}} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{y_{i_3}} = a_{y_{i_2}} \Delta t$
$\left(a_{x_{i_3}}, a_{y_{i_3}}\right) = f\left(x_i+\Delta x_{i_3}, y_i+\Delta y_{i_3}, v_{x_i}+\Delta v_{x_{i_3}}, v_{y_i}+\Delta v_{y_{i_3}}\right)$
$\Delta x_{i_4} = \left(v_{x_i}+\Delta v_{x_{i_3}}\right) \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta y_{i_4} = \left(v_{y_i}+\Delta v_{y_{i_3}}\right) \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{x_{i_4}} = a_{x_{i_3}} \Delta t$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $\Delta v_{y_{i_4}} = a_{y_{i_4}} \Delta t$
$x_{i+1} = x_i + \dfrac{\Delta x_{i_1} + 2\Delta x_{i_2} + 2\Delta x_{i_3} + \Delta x_{i_4}}{6}$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $v_{x_{i+1}} = v_{x_i} + \dfrac{\Delta v_{x_{i_1}} + 2\Delta v_{x_{i_2}} + 2\Delta v_{x_{i_3}} + \Delta v_{x_{i_4}}}{6}$
$y_{i+1} = y_i + \dfrac{\Delta y_{i_1} + 2\Delta y_{i_2} + 2\Delta y_{i_3} + \Delta y_{i_4}}{6}$ &#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0;&#x00a0; $v_{y_{i+1}} = v_{y_i} + \dfrac{\Delta v_{y_{i_1}} + 2\Delta v_{y_{i_2}} + 2\Delta v_{y_{i_3}} + \Delta v_{y_{i_4}}}{6}$

In general, a time step of 10 to 50 milliseconds was used for most results.  Here is a calculation using some data from [1742](/references?refkey=report1742).  The power density of the powder is computed using both the Runge-Kutta and the simple method, each using a time step ranging from 1 s down to 0.1 ms for the Runge-Kutta method and down to 0.002 ms for the simple method.

The following table shows the power density that was calculated, along with the time it took for a computer to make the calculations.

Numerical Method | Time Step (s) | Power per Mass (J/kg) | Computation Time (s)
--- | --- | --- | ---
Runge-Kutta | 1 | 407884.610 | 11.6
Runge-Kutta | 0.5 | 407885.507 | 22.2
Runge-Kutta | 0.2 | 407879.215 | 5.4
Runge-Kutta | 0.1 | 407884.610 | 10.2
Runge-Kutta | 0.05 | 407885.507 | 20.0
Runge-Kutta | 0.02 | 407885.587 | 50.9
Runge-Kutta | 0.01 | 407885.593 | 101.2
Runge-Kutta | 0.005 | 407885.593 | 200.4
Runge-Kutta | 0.002 | 407885.594 | 499.8
Runge-Kutta | 0.001 | 407885.594 | 1009.5
Runge-Kutta | 0.0005 | 407885.594 | 1917.8
Runge-Kutta | 0.0002 | 407885.594 | 3710.2
Runge-Kutta | 0.0001 | 407885.594 | 5070.4
Simple | 1 | 401947.038 | 2.9
Simple | 0.5 | 404905.932 | 5.9
Simple | 0.2 | 396087.585 | 1.3
Simple | 0.1 | 401947.038 | 2.6
Simple | 0.05 | 404905.932 | 5.4
Simple | 0.02 | 406691.212 | 13.1
Simple | 0.01 | 407287.984 | 26.5
Simple | 0.005 | 407586.683 | 52.2
Simple | 0.002 | 407766.004 | 132.7
Simple | 0.001 | 407825.795 | 255.7
Simple | 0.0005 | 407855.693 | 519.2
Simple | 0.0002 | 407873.633 | 1297.1
Simple | 0.0001 | 407879.613 | 2270.5
Simple | 5e-05 | 407882.603 | 3678.8
Simple | 2e-05 | 407884.398 | 5654.9
Simple | 1e-05 | 407884.996 | 7940.7
Simple | 5e-06 | 407885.295 | 11496.1
Simple | 2e-06 | 407885.474 | 19759.8
Simple | 1e-06 | 407885.534 | 25950.3


As can be seen, even though the Runge-Kutta technique takes around 4 times as long as the simple technique to make the same number of calculations, it converges on the answer with a much smaller time step.  With the precision of the original data sources and the variation based on environmental assumptions and drag calculations, anything more than a few decimal places is irrelevant.  A time step of 20 ms is more than sufficient to get a stable answer using Runge-Kutta, whereas a time step of 0.005 ms was required with the simple technique.  The Runge-Kutta technique is some 1000 times faster than the simple technique for this particular case.

A time step of 50 ms was sufficient for six digits of precision with this sample.

## Determining Different Unknowns

Mostly, historical data is used to calculate the power density of gunpowder.  The program is capable of solving for a variety of unknown values.  For example, if the power factor is known, the range can be determined.  For most values, the program works by using an initial very-low estimate and an initial very-high estimate.  This produces results that fall short and go long of some expected result.

For instance, we often know the powder charge, projectile weight, projectile diameter, angle of shot, and range of the shot.  By estimating a low power density, the calculated range will fall short, and with a high power density, the range will be too great.  A weighted binary search is used to determine the power density that produces the actual range that was given in the original data.

For some unknowns, such as elevation angle, there may be more than one solution.  In this case, instead of just using a low and high initial value, a set of initial values is stepped through, until two values are found that bracket the expected result.  From that point, the same weighted binary search is used to find the precise answer.

## Forces

At each point, the calculation of the trajectory is dependent on the force on the projectile.  Rather than use force directly, the acceleration is calculated.  This is divided into two main factors: the acceleration due to gravity and the acceleration due to atmospheric drag including wave effects.

### Acceleration from Gravity

The program uses a very simple model of gravity.  Taking the NIST value for the standard acceleration of gravity, this acceleration is adjusted by the altitude above sea level.  The radius of the earth is taken as the mean radius as defined in WGS-84.  This is a simplification; one could know the surface gravity at the location of interest, and the resultant vector isnÎé÷ecessarily straight down.  Similarly, the mean radius of the earth is not the same as the actual distance from its center.

It is felt that these assumptions are small in comparison to other errors in the calculations.

It is also noted that no correction has been made for the curvature of the earth.

The equation used is:

$a_g = g_0 \left(\dfrac{r_\text{earth}}{r_\text{earth}+y}\right)^2$

where $g_0 = -9.80655 \text{ m}/\text{s}^2$, $r_\text{earth} = 6371009 \text{ m}$, and $y$ is the altitude in meters above mean sea level.

### Acceleration from Drag

The acceleration from drag is expressed as $a_D = \dfrac{\frac{1}{2} C_D \rho v^2 A}{m}$, where $C_D$ is the coefficient of drag, $\rho$ is the atmospheric density, $v$ is the magnitude of velocity of the projectile, $A$ is the cross-section area of the projectile, and $m$ is the mass of the projectile.  The velocity and mass are straightforward.  The area is simply $A = \pi r^2$ or $A = \frac{1}{4}\pi d^2$ where $r$ is the radius of the projectile and $d$ is the diameter.  The coefficient of drag and the density of the atmosphere are more complicated, and are detailed below.

The acceleration always acts contrary to the direction of motion.

#### Coefficient of Drag

One of the factors in the ballistics analysis is the aerodynamic drag on a cannonball or bullet. In the modern formulation of drag, this factor is treated as a function of the Reynolds Number, the Mach Number, and the surface roughness of the projectile.

Somewhat surprisingly, despite an early focus on drag on spherical projectiles, there doesn't appear to be a succinct summary of these factors and the expected accuracy. Rather, many fluid dynamics text books present a beautifully smooth curve that are solely based on the Reynolds Number.  Others show alternate curves for different surface roughness, or for different Mach numbers.  No single source that combines all three factors has been located.
    </vue-markdown>
    <figure>
      <img src="/coefofdrag.gif"/>
      <figcaption>
        <vue-markdown>
Various graphs used for the Coefficient of Drag as a function of the Reynolds and Mach Numbers. The two one the left are from [Munson](/references?refkey=munson1988). The two on the right are from [Miller and Bailey](/references?refkey=miller1979).
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
Furthermore, most graphs only show data for different Mach numbers for a very limited range of Reynolds numbers.  Sometimes formulas are given to try to separated air resistance based on the Reynolds number from wave drag based on the Mach number.

There is one reference that has data for both Reynolds number and Mach number in the range that is of primary interest in.  This is a paper by [Miller and Bailey](/references?refkey=miller1979) from 1979.  Their graphs cover the range from a Reynolds number of 1e4 to 1e7 and Mach numbers from 0 to 3.0.  While this includes most of the range of actual data, when projectiles are travelling slowly, the Reynolds Number is less than 1e4, and, for some cases, the initial velocity is greater than Mach 3.  This data was supplemented with data from a standard text on fluid mechanics ([Munson, 1998, pp. 600, 709](/references?refkey=munson1988)).

Selected points were digitized from each of these graphs.  From these points, the ballistic program interpolates the coefficient of drag.  Several interpolation methods were tried, such a natural cubic splines.  However, due to the nature of the drag curve (specifically, the sharp 'hook' in the graph), a tensioned hermitic spline yielded the best results for interpolating based on Reynolds number along a Mach number curve.  A linear interpolation is used between Mach number curves.

Because the available data on the effect of surface roughness is very poor, no attempt has been made to model it.  In general, the projectiles used are relatively smooth.  Any roughness they have tends to be irregular.  Often the roughness is not reported, though sometimes adjectives such as "smooth" are used.  It is probably that excluding roughness effects introduces less error than trying to include them.

#### Reynolds Number

The Reynolds number is a unitless factor computed as $Re = \dfrac{\rho v L}{\mu}$, where $\rho$ is the density of the fluid the projectile is travelling through, $v$ is the magnitude of the velocity of the projectile, $L$ is the characteristic length, and $\mu$ is the dynamic viscosity of the fluid.  For a sphere, $L$ is the diameter of the sphere, $d$.  The density is the same as the atmospheric density used in computing the acceleration based on the coefficient of drag.

Formulae are used to take into account the effect of relative humidity on both atmospheric density and atmospheric viscosity.

For atmospheric density, the formulas are taken from Picard, et al. in [CIPM-2007](/references?refkey=cipm2007).  This formula is dependent on temperature, relative humidity, and atmospheric pressure.  Unless explicitly specified, atmospheric pressure is computed based on the elevation above sea level using the formula presented in [Munson, 1998, p. 51](/references?refkey=munson1988).

For atmospheric viscosity, the viscosity of dry air is combined with the viscosity of water vapor using a simple equation presented in [Melling, et al., p. 1115](/references?refkey=melling1997).  The equations in [Kayoda, Matsunaga, and Nagashima, p. 956](/references?refkey=kayoda1985) are used to compute the viscosity of dry air at the current temperature and density.  The equations in [Sengers and Kamgar-Parsi, pp. 186-187](/references?refkey=sengers1984) are used to compute the viscosity of water vapor at the current temperature and density .  The atmospheric viscosity is a function of just temperature, density, and relative humidity.

#### Mach Number

The Mach Number is the magnitude of the velocity of the projectile divided by the speed of sound in the local atmosphere.  As with the atmospheric viscosity and atmospheric density, the speed of sound is affected by the relative humidity and the temperature.  The equations presented by [Bohn](/references?refkey=bogn1988) are used, but the molar masses listed in [CIPM-2007, pp. 150-151](/references?refkey=cipm2007) are preferred since they appear to be more authoritative.
    </vue-markdown>
  </div>
</template>

<style scoped>
#computation {
  padding: 10px;
  max-width: 1000px;
  margin: 0 auto;
}
figure {
  float: right;
  margin: 10px 0 10px 10px;
}
figcaption {
  text-align: center;
  max-width: 600px;
  font-size: 0.9em;
}
figure img {
  max-width: 600px;
}
</style>
<style>
[aria-hidden] {
  display: none;
}
#computation table, #computation th, #computation td {
  border: 1px solid #eee;
  padding: 2px;
  font-size: 12px;
}
#computation table {
  border-collapse: collapse;
}
</style>

<script>
export default {
  name: 'Computation'
}
</script>
