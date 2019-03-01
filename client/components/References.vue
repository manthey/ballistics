<template>
  <el-table ref="referenceTable" class="reference-table" :data="sortedReferenceList" :default-sort="{prop: 'ref'}" height="80%" @sort-change="sortTable" :row-class-name="rowClass">
    <el-table-column type="expand">
      <template slot-scope="props">
        <p class="references-expanded" v-if="props.row.details" v-html="props.row.details"/>
        <p class="expanded" v-if="props.row.link">
          <a href="props.row.link">{{ props.row.link }}</a>
        </p>
      </template>
    </el-table-column>
    <el-table-column prop="ref" sortable label="Short Reference" min-width="4" class-name="references-cell" :sort-method="sortMethod"/>
    <el-table-column prop="cms" sortable label="CMS Reference" min-width="13" class-name="references-cell" :sort-method="sortMethod">
      <template slot-scope="props">
        <span v-html="props.row.cms"/>
      </template>
    </el-table-column>
    <el-table-column prop="summary" sortable label="Summary" min-width="13" class-name="references-cell" :sort-method="sortMethod"/>
    <el-table-column prop="key" label="Data" min-width="2" class-name="references-cell">
      <template v-if="props.row._hasData" slot-scope="props">
        <router-link :to="{path: '/plot', query: {filter: 'd.key===\'' + props.row.key + '\''}}" class="reference-link">Plot</router-link>
        {{" "}}
        <router-link :to="{path: '/table', query: {filter: 'd.key===\'' + props.row.key + '\''}}" class="reference-link">Table</router-link>
      </template>
    </el-table-column>
  </el-table>
</template>

<style>
.references-cell .cell, .references-expanded {
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

export default {
  name: 'References',
  props: {
    parameters: Object,
    references: Object,
    refkey: String
  },
  data() {
    return {
      scrolled: false,
      sortOrder: [{prop: 'ref'}],
    }
  },
  computed: {
    referenceList() {
      let list = [];
      Object.keys(this.references).forEach(key => {
        let newref = Object.assign({}, this.references[key]);
        if (this.parameters.key.values && this.parameters.key.values[key]) {
          newref._hasData = true;
        }
        list.push(newref);
      });
      return list;
    },
    sortedReferenceList() {
      return utils.sortObjectList(this.referenceList, this.sortOrder);
    }
  },
  methods: {
    rowClass(spec) {
      return spec.row.key === this.refkey ? 'current-row' : '';
    },
    sortMethod(a, b) {
      if (this.sortOrder[this.sortOrder.length - 1].order !== 'descending') {
        return a.idx - b.idx;
      }
      return b.idx - a.idx;
    },
    sortTable(spec) {
      if (spec.column === null) {
        this.sortOrder = [{prop: 'ref'}];
      } else {
        this.sortOrder = this.sortOrder.filter(record => record.prop !== spec.prop);
        this.sortOrder.push({prop: spec.prop, order: spec.order});
      }
    }
  },
  updated: function () {
    if (this.refkey && this.scrolled !== Object.keys(this.references).length) {
      let row = document.querySelector('.reference-table .current-row');
      if (row) {
        row.scrollIntoView();
        this.scrolled = Object.keys(this.references).length;
      }
    }
  }
}
</script>
