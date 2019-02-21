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
import * as utils from '../utils.js';

export default {
  name: 'DataTable',
  props: {
    datapoint: Object,
    references: Object
  },
  data() {
    return {
      numberFormat: utils.numberFormat,
      showfull: false
    };
  },
  computed: {
    params() {
      let params = Object.assign({}, this.datapoint),
          fullkeys = Object.keys(params),
          result = {};
      utils.keyTable.map(entry => {
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
