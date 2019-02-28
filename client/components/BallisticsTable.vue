<template>
  <div class="table_wrapper">
    <div class="table_scroll">
      <table ref="dataTable" class="data-table">
        <thead>
          <tr>
            <th v-for="param in columns" :key="'datacol-' + param.key" :class="param.key === sortOrder[sortOrder.length - 1].prop ? (sortOrder[sortOrder.length - 1].order === 'descending' ? 'descending' : 'ascending') : ''" :column="param.key" @click="sortTable">
              <span>{{ param.key.replace(/_/g, ' ') }}</span>
              <span class="caret-wrapper">
                <i class="sort-caret ascending"/>
                <i class="sort-caret descending"/>
              </span>
            </th>
          </tr>
        </thead>
        <tbody v-html="rowHtml()"/>
      </table>
    </div>
  </div>
</template>

<style scoped>
.table_wrapper {
  overflow-x: auto;
  overflow-y: auto;
}
.table_scroll {
  font-family: sans-serif;
  font-size: 12px;
  padding: 5px;
}
.data-table th {
  min-width: 150px;
  cursor: pointer;
}
.data-table {
  border-spacing: 0;
}
.caret-wrapper {
  display: inline-flex;
  flex-direction: column;
  height: 34px;
  width: 24px;
  vertical-align: middle;
  overflow: initial;
  position: relative;
}
.sort-caret {
  width: 0;
  height: 0;
  border: 5px solid transparent;
  position: absolute;
  left: 7px;
}
.sort-caret.ascending {
  border-bottom-color: #c0c4cc;
  top: 5px;
}
.sort-caret.descending {
  border-top-color: #c0c4cc;
  bottom: 7px;
}
.ascending .sort-caret.ascending {
  border-bottom-color: black;
}
.descending .sort-caret.descending {
  border-top-color: black;
}
</style>
<style>
.data-table tr.current-row {
  background-color: #ECF5FF;
}
</style>

<script>
import * as utils from '../utils.js';

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
          if (key === 'pointkey') {
            return dir ? (a.key > b.key ? 1 : a.key < b.key ? -1 : a.idx - b.idx) : (a.key > b.key ? -1 : a.key < b.key ? 1 : b.idx - a.idx);
          }
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
      sortedList.forEach((entry, idx) => { entry.rowidx = idx; });
      return sortedList;
    }
  },
  methods: {
    rowHtml() {
      /* Because
        <tr v-for="row in sortedDataList" :key="'datarow-' + row.pointkey">
          <td v-for="param in columns" :key="'datacell-' + row.pointkey + '-' + param.key">{{ row['_' + param.key] || row[param.key] }}</td>
        </tr>
       * is too slow. */
      return this.sortedDataList.map(row => {
        return '<tr' + (row.pointkey === this.pointkey ? ' class="current-row"' : '') + '>' + this.columns.map(param => {
          let value = row['_' + param.key] || row[param.key];
          if (value) {
            value = ('' + value)
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
          } else {
            value = '';
          }
          return '<td>' + value  + '</td>';
        }).join('') + '</tr>';
      }).join('');
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
