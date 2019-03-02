<template>
  <div class="table_wrapper">
    <div class="table_scroll">
      <table ref="dataTable" class="data-table">
        <thead>
          <tr>
            <th v-for="param in columns" :key="'datacol-' + param.key" :class="param.key === sortOrder[sortOrder.length - 1].prop ? (sortOrder[sortOrder.length - 1].order === 'descending' ? 'descending' : 'ascending') : ''" :column="param.key" @click="sortTable">
              <span>{{ param.key.replace(/_/g, ' ') }}</span>
              <span class="caret-wrapper">
                <i class="sort-caret descending"></i>
                <i class="sort-caret ascending"></i>
              </span>
            </th>
          </tr>
        </thead>
        <tbody v-html="rowHtml()" @click="clickRow"/>
      </table>
    </div>
  </div>
</template>

<style src="./table.css" scoped/>
<style scoped>
table th {
  min-width: 150px;
}
</style>
<style>
.data-table tr.current-row {
  background-color: #D8EAFF;
}
.data-table td {
  border-top: #eee 1px solid;
}
</style>

<script>
import * as utils from '../utils.js';
import { escape } from 'html-escaper';

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
      return utils.sortObjectList(this.dataList, this.sortOrder);
    }
  },
  methods: {
    clickRow(event) {
      let row = event.target.closest('tr'),
          pointkey = row.getAttribute('pointkey');
      this.$emit('pointkeyupdate', {
        pointkey: pointkey
      });
    },
    rowHtml() {
      /* Because
        <tr v-for="row in sortedDataList" :key="'datarow-' + row.pointkey">
          <td v-for="param in columns" :key="'datacell-' + row.pointkey + '-' + param.key">{{ row['_' + param.key] || row[param.key] }}</td>
        </tr>
       * is too slow. */
      let columns = this.columns, pointkey = this.pointkey;
      let result = this.sortedDataList.map(row => {
        return '<tr pointkey="' + row.pointkey + '"' + (row.pointkey === pointkey ? ' class="current-row"' : '') + '>' + columns.map(param => {
          let value = row['_' + param.key] || row[param.key];
          if (value === undefined) {
            value = '';
          } else if (typeof value === 'string') {
            value = escape(value);
          } else {
            value = '' + value;
          }
          return '<td>' + value  + '</td>';
        }).join('') + '</tr>';
      }).join('');
      return result;
    },
    scrollIfNeeded() {
      if (this.pointkey && this.scrolled !== this.plotdata.length) {
        let row = document.querySelector('.data-table .current-row');
        if (row) {
          row.scrollIntoView();
          row.closest('.table_wrapper').scrollTop -= (row.closest('.table_wrapper').clientHeight - row.clientHeight) / 2;
          this.scrolled = this.plotdata.length;
        }
      }
    },
    sortTable(event) {
      let column = event.target.closest('[column]').getAttribute('column'),
          last = this.sortOrder[this.sortOrder.length - 1],
          order = 'ascending';
      if (last.prop === column) {
        if (last.order === 'descending') {
          column = null;
        } else {
          order = 'descending';
        }
      }
      if (column === null) {
        this.sortOrder = [{prop: 'pointkey'}];
      } else {
        this.sortOrder = this.sortOrder.filter(record => record.prop !== column);
        this.sortOrder.push({prop: column, order: order});
      }
    }
  },
  mounted: function () {
    this.$nextTick(this.scrollIfNeeded);
  },
  updated: function () {
    this.scrollIfNeeded();
  }
}
</script>
