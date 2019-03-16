<template>
  <div id="techniques" class="textblock">
    <vue-markdown>
# Experimental Techniques

The project uses historical data from a variety of techniques that result in measurements from which the power per mass factor of gunpowder can be determined.
    </vue-markdown>
    <figure>
      <img src="tech_range.jpg"/>
      <figcaption>
        <vue-markdown>
Range measures the distance a projectile is thrown by an actual gun.  Figure from [Blondel, 1683](#/reference?refkey=blondel1683)
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
## Range

[Plot](#/plot?filter=d.technique%3D%3D'range') [Table](#/table?filter=d.technique%3D%3D'range')

Range is a straight-forward measurement.  An actual cannon, howitzer, mortar, or musket is fired, noting the angle angle of elevation, the size and mass of the projectile, and the mass of the powder charge.  The distance that the ball travels is measured.

It must be noted if the ball lands at a different elevation than it started.

There is quite a variety of experiments using range.  There are proof tests where a mortar is used where a minimum range is required for a standardized angle, ball, and powder charge.  There are simple down-range observations where observers measure the landing point.  More careful tests note temperature, humidity, and pressure.  A wide selection of ball diameters and materials and of initial angles have been examined.

## Time of Flight

[Plot](#/plot?filter=d.technique%3D%3D'time') [Table](#/table?filter=d.technique%3D%3D'time')

This is a variation of the range test, except instead of noting the distance that the ball travels, the time between when it was fired and when it lands is recorded.

Time of flight measurements are usually very inaccurate.  Often a projectile is only aloft for 10 seconds.  A long shot might last nearly half a minute.  Observers rarely record times with accuracies of greater than a quarter second, and often these can be a second in error.  This produces unreliable results.

## Impact Angle

[Plot](#/plot?filter=d.technique%3D%3D'final_angle') [Table](#/table?filter=d.technique%3D%3D'final_angle')

This is another variation of the range test, except that the angle of impact (also called the angle of fall) is noted.  This can be done, for instance, by sighting the ball just before impact along with the landing spot.  Observations don't seem particularly accurate.
    </vue-markdown>
    <figure>
      <img src="tech_pendulum_robins.jpg"/>
      <figcaption>
        <vue-markdown>
The original ballistics pendulum recorded the initial swing via the length of the extended chord.  [Robins, 1761, Vol. I](#/references?refkey=robins1761v1)
        </vue-markdown>
      </figcaption>
      <img src="tech_double_pendulum.jpg"/>
      <figcaption>
        <vue-markdown>
Ballistic pendulums can be more sophisticated and well-constructed than the original.  Alfred Mordecai used a large receiving chamber filled with sandbags to catch up to 64 lb cannon balls.  [Mordecai, 1845](#/references?refkey=mordecai1845)
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
## Pendulum

[Plot](#/plot?filter=['pendulum','double_pendulum'].indexOf(d.technique)>%3D0) [Table](#/table?filter=['pendulum','double_pendulum'].indexOf(d.technique)>%3D0)

The concept of the ballistics pendulum is straightforward -- fire a projectile into a heavy pendulum and measure how far the pendulum swings.  Based on conservation of energy, the height that the pendulum rises is based on the velocity of the projectile that struck it.

### Single Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'pendulum') [Table](#/table?filter=d.technique%3D%3D'pendulum')

In the original ballistics pendulum, as invented by Benjamin Robins and introduced in the 1742 book _New Principles of Gunnery_, the gun is fixed so that it cannot move, and the pendulum has a block of wood to receive the projectile.  As subsequent measurements are made, the mass of the pendulum has to be adjusted for the embedded projectiles.

For computation of initial power of the gunpowder used, it is necessary to know the distance from the gun to the pendulum, the pendulum's mass, center of gravity, period of small-angle oscillation, location of the index tape.

A slight improvement is to record the angle of swing directly rather than using an index tape.

Most authors after Robins compute the projectile velocity and report that rather than just reporting the pendulum information.
    </vue-markdown>
    <figure class="left">
      <img src="tech_gun_pendulum.jpg"/>
      <figcaption>
        <vue-markdown>
The gun can be mounted on a pendulum to measure its recoil.  [Mordecai, 1845](#/references?refkey=mordecai1845)
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
### Gun Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'gun_pendulum') [Table](#/table?filter=d.technique%3D%3D'gun_pendulum')

If the gun is also mounted on a pendulum, then it recoils freely and that recoil can be used to measure the force of the fired gunpowder.  [Hutton, 1812, Vol. III, p. 24](#/references?refkey=hutton1812v3) performed some experiments to show that whether the gun was prevented or allowed to recoil, the resultant projectile velocity was not changed.

Measuring the force of the gunpowder by the velocity imparted to the gun gives an additional data point.  If this is done in conjuction with measuring the speed of the projectile, these two measurements can be used as a check against recording errors.

### Double Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'double_pendulum') [Table](#/table?filter=d.technique%3D%3D'double_pendulum')

In cases where the gun was mounted on a pendulum, the measurement of the projectile using a pendulum is marked as a "Double Pendulum".  This allows data from guns allowed to recoil fully to be separated from data where the gun is more constrained and measured by a single pendulum only.
    </vue-markdown>
    <div style="clear: both"/>
    <figure>
      <img src="tech_pressure.jpg"/>
      <figcaption>
        <vue-markdown>
The pressure energy of gunpowder can be measured by determining the weight that a quantity of powder can just lift. [Rumford, 1797](#/references?refkey=rumford1797)
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
## Pressure Chamber

[Plot](#/plot?filter=d.technique%3D%3D'pressure') [Table](#/table?filter=d.technique%3D%3D'pressure')

If gunpowder is exploded in a confined chamber, and the pressure on the outside of the chamber is measured, the energy expended can be calculated from that pressure.

To use pressure chamber information, it is necessary to know the volume of the chamber and the pressure developed.  The pressure can be determined from a force measured over a known area.
    </vue-markdown>
    <div style="clear: both"/>
    <vue-markdown>
## Given Velocity

[Plot](#/plot?filter=d.technique%3D%3D'given_velocity') [Table](#/table?filter=d.technique%3D%3D'given_velocity')

Some authors report a velocity that was directly measured or has already been calculated based on available data.  When this is done, the velocity, along with the mass of the projectile, can be used to directly calculate the power factor of the gunpowder.

## Trajectory

[Plot](#/plot?filter=d.technique%3D%3D'trajectory') [Table](#/table?filter=d.technique%3D%3D'trajectory')

Trajectory measures the height during the travel of the projectile without stopping it.  This has been done with, for instance, a paper screen that is placed at a fixed distance from the muzzle of the gun.  The perforation of the paper shows the deviation from the desired flight path to the side as well as the altitude of the projectile at that point.

## Chronograph

[Plot](#/plot?filter=['chronograph','wheel_chronograph'].indexOf(d.technique)>%3D0) [Table](#/table?filter=['chronograph','wheel_chronograph'].indexOf(d.technique)>%3D0)

Chronographs measure the time of flight between two or more points using any of a variety of techniques.  The average projectile velocity can be determined by knowing the distance and time between the measurement points.

Since the projectile's velocity is always changing, if the baseline is long, rather than use this average velocity, the trajectory can be solved for at both the near and far distance such that the time of flight increases by the measured time.
    </vue-markdown>
    <figure>
      <img src="tech_wheel_chronograph.jpg"/>
      <figcaption>
        <vue-markdown>
A wheel chronograph.  [d'Antoni, 1765](#/references?refkey=dantoni1765)
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
### Wheel Chronograph

[Plot](#/plot?filter=d.technique%3D%3D'wheel_chronograph') [Table](#/table?filter=d.technique%3D%3D'wheel_chronograph')

A wheel chronograph is a horizontal wheel that can be spun at a known speed.  A paper strip is attached to the rim of the wheel so that it sticks upwards.  A projectile is fired directly across the diameter of the wheel so that it cuts the paper on the near and far side.  The amount that these cuts differ from 180&deg; apart indicate the time to cross the diameter of the wheel.
    </vue-markdown>
    <figure class="left">
      <img src="https://s3-eu-west-1.amazonaws.com/smgco-images/images/61/686/medium_B000098.jpg"/>
      <figcaption>
        <vue-markdown>
The Bashforth Chronograph.  [collection.sciencemuseum.org.uk](https://s3-eu-west-1.amazonaws.com/smgco-images/images/61/686/medium_B000098.jpg)
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
### Other Chronographs

[Plot](#/plot?filter=d.technique%3D%3D'chronograph') [Table](#/table?filter=d.technique%3D%3D'chronograph')

More modern chronographs generally have very high precision through some sort of electrical timing.

#### Bashforth Chronograph

The Bashforth Chronograph used a series of frames with hanging wires.  When the projectile passes by these wires, an electric circuit was completed that was used to make a mark on a moving paper record.  A clock also generated marks at regular intervals.  The location of the marks from the frames could be referenced from the clock marks to measure the time it took a projectile to travel between frames to an accuracy of 0.1 ms.

In Bashforth's own tests, he used 10 screens spaced 150 ft apart each.

#### Modern Chronograph

Many modern chronographs use two or more light sensors to detect when a projectile passes through a small region.  Often these have a short baseline of one to four feet, and rely on a high precision clock to make an accurate determination of velocity.

Modern units are relatively inexpensive, but are also somewhat limited in the size of projectile that they can accommodate.  It would be infeasible to use most of them with cannons, for instance.  These chronographs are expected to be relatively near to the muzzle of the gun, and it would risk destroying the chronograph or its sensor screen if it were substantially down range.
    </vue-markdown>
    <div style="clear: both"/>
    <vue-markdown>
## Maximum Height

[Plot](#/plot?filter=d.technique%3D%3D'height') [Table](#/table?filter=d.technique%3D%3D'height')

## Calorimeter

[Plot](#/plot?filter=d.technique%3D%3D'calorimeter') [Table](#/table?filter=d.technique%3D%3D'calorimeter')

## Theory

[Plot](#/plot?filter=d.technique%3D%3D'theory') [Table](#/table?filter=d.technique%3D%3D'theory')
    </vue-markdown>
  </div>
</template>

<style src="./textblock.css" scoped/>

<script>
export default {
  name: 'Techniques'
}
</script>
