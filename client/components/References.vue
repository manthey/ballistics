<template>
  <el-table :data="sortedReferenceList" :default-sort="{prop: 'ref'}" height="80%" @sort-change="sortTable">
    <el-table-column type="expand">
      <template slot-scope="props">
        <p class="references-expanded" v-if="props.row.details" v-html="props.row.details"/>
        <p class="expanded" v-if="props.row.link">
          <a href="props.row.link">{{ props.row.link }}</a>
        </p>
      </template>
    </el-table-column>
    <el-table-column prop="ref" sortable label="Short Reference" min-width="1" class-name="references-cell" :sort-method="sortMethod"/>
    <el-table-column prop="cms" sortable label="CMS Reference" min-width="3" class-name="references-cell" :sort-method="sortMethod">
      <template slot-scope="props">
        <span v-html="props.row.cms"/>
      </template>
    </el-table-column>
    <el-table-column prop="summary" sortable label="Summary" min-width="3" class-name="references-cell" :sort-method="sortMethod"/>
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
export default {
  name: 'References',
  props: {
    references: Object
  },
  data() {
    return {
      sortOrder: [{prop: 'ref'}]
    }
  },
  computed: {
    referenceList() {
      let list = [];
      Object.keys(this.references).forEach(key => {
        list.push(this.references[key]);
      });
      return list;
    },
    sortedReferenceList() {
      let sortedList = this.referenceList.slice().sort((a, b) => {
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
          o = a[key].localeCompare(b[key], undefined, {ignorePunctuation: true});
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
  }
}
</script>
