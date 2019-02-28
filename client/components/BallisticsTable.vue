<template>
  <el-table ref="dataTable" class="data-table" :data="sortedDataList" :default-sort="{prop: 'pointkey'}" height="80%" width="100%" @sort-change="sortTable" :row-class-name="rowClass">
    <el-table-column v-for="param in columns" :prop="param.key" :key="'datacol-' + param.key" sortable :label="param.key.replace(/_/g, ' ')" class-name="data-cell" :sort-method="sortMethod" width="180">
      <template slot-scope="props">
      {{ formatValue(props.row[param.key], param) }}
      </template>
    </el-table-column>
  </el-table>
</template>

<style>
.data-cell .cell {
  word-break: normal;
  font-size: 1.1em;
  line-height: 1.2em;
  color: black;
}
.el-table .ascending .sort-caret.ascending {
  border-bottom-color: black;
}
.el-table .descending .sort-caret.descending {
  border-top-color: black;
}
</style>

<script>
import * as utils from '../utils.js';
import math from 'mathjs';

export default {
  name: 'BallisticsTable',
  props: {
    plotdata: Array,
    parameters: Object,
    filter: String,
    pointkey: String
  },
  data() {
    return {
      numberFormat: utils.NumberFormat,
      parameterList: utils.ParameterList,
      scrolled: false,
      sortOrder: [{prop: 'pointkey'}],
    }
  },
  computed: {
    dataList() {
      let plotdata  = this.plotdata || [];
      if (this.filter) {
        try {
          let filterFunc = Function('d', '"use strict";return(' + this.filter + ')')
          // eslint-disable-next-line
          plotdata = plotdata.filter(filterFunc);
        } catch (err) {
          console.error('Filter failed: ' + this.filter);
          console.error(err);
        }
      }
      return plotdata;
    },
    columns() {
      let dataList = this.dataList;
      let columns = this.parameterList.filter(param => dataList.some(entry => entry[param.key]));
      return columns;
    },
    sortedDataList() {
      let sortedList = this.dataList.slice().sort((a, b) => {
        let i, o, key, dir;
        for (i = this.sortOrder.length - 1; i >= 0; i--) {
          key = this.sortOrder[i].prop;
          dir = this.sortOrder[i].order !== 'descending';
          if (a[key] === undefined) {
            return dir ? -1 : 1;
          }
          if (b[key] === undefined) {
            return dir ? 1 : -1;
          }
          if (!isNaN(parseFloat(a[key])) && isFinite(a[key]) &&
              !isNaN(parseFloat(b[key])) && isFinite(b[key])) {
            return dir ? +a[key] - +b[key] : +b[key] - a[key];
          }
          o = (''+a[key]).localeCompare(''+b[key], undefined, {ignorePunctuation: true});
          if (o) {
            return dir ? o : -o;
          }
        }
        return 0;
      });
      sortedList.forEach((entry, idx) => { entry.idx = idx; });
      return sortedList;
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
    rowClass(spec) {
      return spec.row.key === this.pointkey ? 'current-row' : '';
    },
    sortMethod(a, b) {
      if (this.sortOrder[this.sortOrder.length - 1].order !== 'descending') {
        return a.idx - b.idx;
      }
      return b.idx - a.idx;
    },
    sortTable(spec) {
      if (spec.column === null) {
        this.sortOrder = [{prop: 'pointkey'}];
      } else {
        this.sortOrder = this.sortOrder.filter(record => record.prop !== spec.prop);
        this.sortOrder.push({prop: spec.prop, order: spec.order});
      }
    }
  },
  updated: function () {
    if (this.pointkey && this.scrolled !== this.plotdata.length) {
      let row = document.querySelector('.data-table .current-row');
      if (row) {
        row.scrollIntoView();
        this.scrolled = this.plotdata.length;
      }
    }
  }
}
</script>
