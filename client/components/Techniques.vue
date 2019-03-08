<template>
  <div id="techniques">
    <vue-markdown>
# Experimental Techniques

The project uses historical data from a variety of techniques that result in measurements from which the power per mass factor of gunpowder can be determined.

## Range
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
[Plot](#/plot?filter=d.technique%3D%3D'range') [Table](#/table?filter=d.technique%3D%3D'range')

Range is a straight-forward measurement.  An actual cannon, howitzer, mortar, or musket is fired, noting the angle angle of elevation, the size and mass of the projectile, and the mass of the powder charge.  The distance that the ball travels is measured.

It must be noted if the ball lands at a different elevation than it started.

There is quite a variety of experiments using range.  There are proof tests where a mortar is used where a minimum range is required for a standardized angle, ball, and powder charge.  There are simple down-range observations where observers measure the landing point.  More careful tests note temperature, humidity, and pressure.  A wide selection of ball diameters and materials and of initial angles have been examined.

## Time of Flight

[Plot](#/plot?filter=d.technique%3D%3D'time') [Table](#/table?filter=d.technique%3D%3D'time')

This is a variation of the range test, except instead of noting the distance that the ball travels, the time between when it was fired and when it lands is recorded.

Time of flight measurements are usually very inaccurate.  Often a projectile is only aloft for 10 seconds.  A long shot might last nearly half a minute.  Observers rarely record times with accuracies of greater than a quarter second, and often these can be a second in error.  This produces unreliable results.

## Pendulum

[Plot](#/plot?filter=['pendulum','double_pendulum'].indexOf(d.technique)>%3D0) [Table](#/table?filter=['pendulum','double_pendulum'].indexOf(d.technique)>%3D0)

### Single Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'pendulum') [Table](#/table?filter=d.technique%3D%3D'pendulum')

### Double Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'double_pendulum') [Table](#/table?filter=d.technique%3D%3D'double_pendulum')

### Gun Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'gun_pendulum') [Table](#/table?filter=d.technique%3D%3D'gun_pendulum')

## Given Velocity

[Plot](#/plot?filter=d.technique%3D%3D'given_velocity') [Table](#/table?filter=d.technique%3D%3D'given_velocity')

## Trajectory

[Plot](#/plot?filter=d.technique%3D%3D'trajectory') [Table](#/table?filter=d.technique%3D%3D'trajectory')

## Chronograph

[Plot](#/plot?filter=['chronograph','wheel_chronograph'].indexOf(d.technique)>%3D0) [Table](#/table?filter=['chronograph','wheel_chronograph'].indexOf(d.technique)>%3D0)

### Wheel Chronograph

[Plot](#/plot?filter=d.technique%3D%3D'wheel_chronograph') [Table](#/table?filter=d.technique%3D%3D'wheel_chronograph')

### Modern Chronograph

[Plot](#/plot?filter=d.technique%3D%3D'chronograph') [Table](#/table?filter=d.technique%3D%3D'chronograph')

## Impact Angle

[Plot](#/plot?filter=d.technique%3D%3D'final_angle') [Table](#/table?filter=d.technique%3D%3D'final_angle')

## Maximum Height

[Plot](#/plot?filter=d.technique%3D%3D'height') [Table](#/table?filter=d.technique%3D%3D'height')

## Calorimeter

[Plot](#/plot?filter=d.technique%3D%3D'calorimeter') [Table](#/table?filter=d.technique%3D%3D'calorimeter')

## Theory

[Plot](#/plot?filter=d.technique%3D%3D'theory') [Table](#/table?filter=d.technique%3D%3D'theory')
    </vue-markdown>
  </div>
</template>

<style scoped>
#techniques {
  padding: 10px calc(50% - 500px);
  margin: 0 0 0 10px;
  overflow: auto;
}
figure {
  float: right;
  margin: 10px 0 10px 10px;
  margin: 10px calc(500px - 50% - 20px) 10px 10px;
}
figure+div::after {
  content: "";
  clear: both;
  display: block;
}
figcaption {
  text-align: center;
  max-width: 400px;
  font-size: 0.9em;
}
figure img {
  max-width: 400px;
}
</style>

<script>
export default {
  name: 'Techniques'
}
</script>
