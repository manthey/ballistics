<template>
  <div id="computation" class="textblock">
    <vue-markdown>
# Drag Model

The ballistic computations are dependent on calculating aerodynamic drag correctly.  Many of the original data sources were collected to determine the effects of drag (for instance, [Bashforth, 1870](#/references?refkey=bashforth1870), [H&#x00e9;lie, 1865](#/references?refkey=helie1865), [Hutton, 1812, Vol. II](#/references?refkey=hutton1812v2), [Robins, 1761, Vol. I](#/references?refkey=robins1761v1)).  The effects of drag obviously vary based on velocity and projectile size, but increasing either doesn't always produce a uniform increase in drag.

Early experiments produced a wide range of drag formulas based on the cross-sectional area of the projectile and a disjoint set of equations depending on the velocity.  For instance, some of the equations vary by the square of the velocity at low speed, the cube at higher speed, then a higher factor, then back to the cube, and back to the square, with each velocity range having difference constants to adjust the formula.  Additionally, the drag is adjusted based on atmospheric density.
    </vue-markdown>
    <figure>
      <MnRePlot class="generic" :trajectories="trajectories"/>
      <figcaption>
        <vue-markdown>
Reynolds and Mach Numbers used when computing power factors with available data.  Darker values indictate where projectiles spent a larger portion of their flight.
        </vue-markdown>
      </figcaption>
    </figure>
    <vue-markdown>
In the modern concept, the coefficient of drag is based on the Reynolds number and Mach number.  The Reynolds number is based on the atmospheric density and viscosity, the projectile characteristic length, and the velocity.  The Mach number is the velocity scaled by the speed of sound in the surrounding atmosphere.  The force due to drag is this coefficient of drag scaled by the atmospheric density, the square of the velocity, and the projectile cross-sectional area.  The Reynolds number allows the variations due to scale to abstracted to a single quantity.  The Mach number is used to take into account shock wave effects.

[Miller, 1979](#/references?refkey=miller1979) provides most comprehensive coefficients of drag for different Reynolds and Mach numbers.  Even this paper doesn't cover all of the values needed for the available data sets, so it has been supplemented with some values for Mach 0 and very high Mach values from [Munson, 1998](#/references?refkey=munson1998).

- TODO: Show miller graph (from matplotlib)

- TODO: Discuss verification, link to graph of bashforth showing spread of different groups

- TODO: Discuss adjusting values
    </vue-markdown>
  </div>
</template>

<style src="./textblock.css" scoped/>

<script>
import MnRePlot from './MnRePlot.vue';

export default {
  name: 'DragModel',
  components: {
    MnRePlot
  },
  props: {
    trajectories: Object
  }
}
</script>
