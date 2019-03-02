<template>
  <div class="table_wrapper">
    <div class="table_scroll">
      <table ref="referenceTable" class="reference-table">
        <thead>
          <tr>
            <th v-for="param in columns" :key="'datacol-' + param.key" :class="param.key === sortOrder[sortOrder.length - 1].prop ? (sortOrder[sortOrder.length - 1].order === 'descending' ? 'descending' : 'ascending') : ''" :column="param.key" @click="sortTable" :width="param.width || ''">
              <span>{{ param.title }}</span>
              <span v-if="param.sort" class="caret-wrapper">
                <i class="sort-caret descending"></i>
                <i class="sort-caret ascending"></i>
              </span>
            </th>
          </tr>
        </thead>
        <tbody @click="clickRow">
          <template v-for="row in sortedReferenceList">
            <tr :key="'refrow-' + row.key" :refkey="row.key" :class="row.key === refkey ? 'current-row' : ''">
              <td :class="row.details || row.link ? 'expand' : ''" @click.stop="toggleExpansion"><span></span></td>
              <td>{{ row.ref }}</td>
              <td v-html="row.cms"></td>
              <td>{{ row.summary || '' }}</td>
              <td>
                <template v-if="row._hasData">
                  <router-link :to="{path: '/plot', query: {filter: 'd.key===\'' + row.key + '\''}}" class="reference-link">Plot</router-link>
                  {{" "}}
                  <router-link :to="{path: '/table', query: {filter: 'd.key===\'' + row.key + '\''}}" class="reference-link">Table</router-link>
                </template>
              </td>
            </tr>
            <tr v-if="row.details || row.link" :key="'refrowexp-' + row.key" class="expansion-row">
              <td colspan="5">
                <p v-if="row.details" v-html="row.details"/>
                <p v-if="row.link">
                  <a href="row.link">{{ row.link }}</a>
                </p>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style src="./table.css" scoped/>
<style scoped>
table {
  font-size: 15px;
}
table td {
  padding: 5px 5px;
}
.expansion-row td {
  padding: 2px 25px 2px 75px;
  font-size: 14px;
}
</style>
<style>
.reference-table tr.current-row {
  background-color: #D8EAFF;
}
.reference-table td {
  border-top: #eee 1px solid;
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
      columns: [{
        key: 'expand',
        title: '',
        width: '50px'
      }, {
        key: 'ref',
        title: 'Short Reference',
        sort: true,
        width: '200px'
      }, {
        key: 'cms',
        title: 'CMS Reference',
        sort: true
      }, {
        key: 'summary',
        title: 'Summary',
        sort: true
      }, {
        key: '_hasData',
        title: 'Data',
        width: '100px'
      }],
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
    clickRow(event) {
      let row = event.target.closest('tr'),
          refkey = row.getAttribute('refkey');
      let route = this.$router.currentRoute;
      this.$router.push({
        path: '/references',
        query: Object.assign({}, route.query, {refkey: refkey})
      });
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
        this.sortOrder = [{prop: 'ref'}];
      } else {
        this.sortOrder = this.sortOrder.filter(record => record.prop !== column);
        this.sortOrder.push({prop: column, order: order});
      }
    },
    scrollIfNeeded() {
      if (this.refkey && this.scrolled !== Object.keys(this.references).length) {
        let row = document.querySelector('.reference-table .current-row');
        if (row) {
          row.scrollIntoView();
          row.closest('.table_wrapper').scrollTop -= (row.closest('.table_wrapper').clientHeight - row.clientHeight) / 2;
          this.scrolled = Object.keys(this.references).length;
        }
      }
    },
    toggleExpansion(event) {
      let row = event.target.closest('tr');
      row.classList.toggle('expanded');
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
