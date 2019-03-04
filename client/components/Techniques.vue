<template>
  <div id="techniques">
    <vue-markdown>
# Experimental Techniques

The project uses historical data from a variety of techniques that result in measurements from which the power per mass factor of gunpowder can be determined.

## Range

[Plot](#/plot?filter=d.technique%3D%3D'range') [Table](#/table?filter=d.technique%3D%3D'range')

## Pendulum

[Plot](#/plot?filter=['pendulum','double_pendulum'].indexOf(d.technique)>%3D0) [Table](#/table?filter=['pendulum','double_pendulum'].indexOf(d.technique)>%3D0)

### Single Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'pendulum') [Table](#/table?filter=d.technique%3D%3D'pendulum')

### Double Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'double_pendulum') [Table](#/table?filter=d.technique%3D%3D'double_pendulum')

### Gun Pendulum

[Plot](#/plot?filter=d.technique%3D%3D'gun_pendulum') [Table](#/table?filter=d.technique%3D%3D'gun_pendulum')

## Time of Flight

[Plot](#/plot?filter=d.technique%3D%3D'time') [Table](#/table?filter=d.technique%3D%3D'time')

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
  padding: 10px;
  max-width: 1000px;
  margin: 0 auto;
}
</style>

<script>
export default {
  name: 'Techniques'
}
</script>
