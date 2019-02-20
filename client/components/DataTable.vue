<template>
  <div class="table_wrapper">
    <div class="table_scroll">
      <div v-html="this.references[params.key] ? this.references[params.key].cms : ''"></div>
      <div>
        <button id="full" @click="toggleFull">{{ this.showfull ? 'Primary Values' : 'All Values' }}</button>
      </div>
      <table>
        <tr v-for="param in Object.keys(params)" :key="param">
          <td>{{ param }}</td>
          <td>{{ params[param] }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<style scoped>
.table_wrapper {
  height: 100%;
  max-width: 300px;
  flex: 1;
  overflow-x: hidden;
  overflow-y: auto;
}
.table_scroll {
  font-family: sans-serif;
  font-size: 12px;
}
</style>

<script>
import math from 'mathjs';

/*
main
references
fulldata
fulldata w/o theoretical (with a filter specified)
- specific graphs with commentary
  small diam
  medium
  large
table: full / close / traj.graph
*/
//search for missing "p. "
//search for replaced "ref"
let keyTable = [{
  key: 'key',
  primary: true
}, {
  key: 'idx',
  title: '0-based location in the data file',
  primary: true
}, {
  key: 'ref',
  primary: true
}, {
  key: 'desc',
  primary: true
}, {
  key: 'date',
  primary: true
}, {
  key: 'technique',
  primary: true
}, {
  key: 'power_factor',
  units: 'J/kg',
  primary: true
}, {
  key: 'given_date',
  primary: true
}, {
  key: 'given_charge',
  primary: true
}, {
  key: 'given_diameter',
  primary: true
}, {
  key: 'given_angle',
  primary: true
}, {
  key: 'given_range',
  primary: true
}, {
  key: 'given_final_angle',
  primary: true
}, {
  key: 'given_final_height',
  primary: true
}, {
  key: 'given_final_time',
  primary: true
}, {
  key: 'given_final_velocity',
  primary: true
}, {
  key: 'given_atmospheric_density',
  primary: true
}, {
  key: 'given_group',
  primary: true
}, {
  key: 'given_temperature',
  primary: true
}, {
  key: 'given_humidity',
  primary: true
}, {
  key: 'given_wetbulb',
  primary: true
}, {
  key: 'given_initial_height',
  primary: true
}, {
  key: 'given_initial_velocity',
  primary: true
}, {
  key: 'given_mass',
  primary: true
}, {
  key: 'given_material',
  primary: true
}, {
  key: 'given_material_density',
  primary: true
}, {
  key: 'given_maxheight',
  primary: true
}, {
  key: 'given_power',
  primary: true
}, {
  key: 'given_pressure',
  primary: true
}, {
  key: 'given_rising_height',
  primary: true
}, {
  key: 'given_technique',
  primary: true
}, {
  key: 'charge',
  units: 'kg',
  primary: true
}, {
  key: 'diam',
  units: 'm',
  primary: true
}, {
  key: 'range',
  units: 'm',
  primary: true
}, {
  key: 'final_angle',
  units: 'deg',
  primary: true
}, {
  key: 'final_height',
  units: 'm',
  primary: true
}, {
  key: 'final_time',
  units: 's',
  primary: true
}, {
  key: 'final_velocity',
  units: 'm/s',
  primary: true
}, {
  key: 'atmospheric_density',
  units: 'kg/m^3',
  primary: true
}, {
  key: 'rh',
  primary: true
}, {
  key: 'initial_height',
  units: 'm',
  primary: true
}, {
  key: 'initial_velocity',
  units: 'm/s',
  primary: true
}, {
  key: 'mass',
  units: 'kg',
  primary: true
}, {
  key: 'material',
  primary: true
}, {
  key: 'material_density',
  units: 'kg/m^3',
  primary: true
}, {
  key: 'projectile_density',
  units: 'kg/m^3',
  primary: true
}, {
  key: 'max_height',
  units: 'm',
  primary: true
}, {
  key: 'pressure',
  units: 'Pa',
  primary: true
}, {
  key: 'pressure_y0',
  units: 'm',
  primary: true
}, {
  key: 'rising_height',
  units: 'm',
  primary: true
}, {
  key: 'computation_time',
  units: 's'
}, {
  key: 'initial_angle',
  units: 'deg'
}, {
  key: 'T',
  title: 'Air temperature',
  units: 'K'
}, {
  key: 'Twb',
  title: 'Wet-bulb temperature',
  units: 'K'
}, {
  key: 'x',
  units: 'm'
}, {
  key: 'y',
  units: 'm'
}, {
  key: 'vx',
  units: 'm/s'
}, {
  key: 'vy',
  units: 'm/s'
}, {
  key: 'ax',
  units: 'm/s^2'
}, {
  key: 'ay',
  units: 'm/s^2'
}, {
  key: 'final_density_density',
  units: 'kg/m^3'
}, {
  key: 'final_density_h',
  title: 'final density humidity (0-1)'
}, {
  key: 'final_density_pressure',
  units: 'Pa'
}, {
  key: 'final_density_psv',
  title: 'Vapor pressure at saturation',
  units: 'Pa'
}, {
  key: 'final_density_T',
  units: 'K'
}, {
  key: 'final_density_y',
  units: 'm'
}, {
  key: 'final_drag_sos',
  units: 'm/s'
}, {
  key: 'final_viscosity_mua',
  title: 'Viscosity of dry air',
  units: 'kg/m/s'
}, {
  key: 'final_viscosity_muv',
  title: 'Viscosity of water vapor',
  units: 'kg/m/s'
}, {
  key: 'final_viscosity_viscosity',
  title: 'Viscosity',
  units: 'kg/m/s'
}];

export default {
  name: 'DataTable',
  props: {
    datapoint: Object,
    references: Object
  },
  data() {
    return {
      numberFormat: {precision: 6, lowerExp: -6, upperExp: 9},
      showfull: false
    };
  },
  computed: {
    params() {
      let params = Object.assign({}, this.datapoint),
          fullkeys = Object.keys(params),
          result = {};
      keyTable.map(entry => {
        if (params[entry.key] !== undefined && (this.showfull || entry.primary)) {
          result[entry.key] = this.formatValue(params[entry.key], entry);
        }
      });
      if (this.showfull) {
        fullkeys = fullkeys.sort();
        fullkeys.map(key => {
          if (params[key] !== undefined && result[key] === undefined) {
            result[key] = this.formatValue(params[key]);
          }
        });
      }
      return result;
    }
  },
  methods: {
    formatValue(value, params) {
      if (isNaN(parseFloat(value)) || !isFinite(value)) {
        return value;
      }
      if (params && params.units) {
        return math.unit(+value, params.units).format(this.numberFormat);
      }
      return math.format(+value, this.numberFormat);
    },
    toggleFull() {
      this.showfull = !this.showfull;
    }
  }
}
</script>
