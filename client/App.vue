<template>
  <div id="app">
    <PlotWithControls :filter="query.filter" :plotdata="plotdata" :references="references" @filterupdate="queryUpdate"/>
  </div>
</template>

<style>
html,body,#app {
  width: 100%;
  height: 100%;
  margin: 0;
}
</style>

<script>
import * as utils from './utils.js';
import PlotWithControls from './components/PlotWithControls.vue';

export default {
  name: 'app',
  components: {
    PlotWithControls
  },
  data() {
    return {
      plotdata: [],
      query: utils.getUrlQuery(),
      references: {}
    };
  },
  methods: {
    queryUpdate(updates) {
      this.query = Object.assign({}, this.query, updates);
    },
    fetchData() {
      fetch('totallist.json').then(resp => resp.json()).then(data => {
        this.plotdata = data;
      }).catch(err => { throw err; });
    },
    fetchReferences() {
      fetch('references.json').then(resp => resp.json()).then(data => {
        this.references = data;
      }).catch(err => { throw err; });
    },
    fetchParameters() {
      fetch('parameters.json').then(resp => resp.json()).then(data => {
        this.parameters = utils.updateParameters(data);
      }).catch(err => { throw err; });
    }
  },
  watch: {
    query(newval) {
      utils.setUrlQuery(newval, true);
    }
  },
  mounted: function () {
    this.fetchData();
    this.fetchReferences();
    this.fetchParameters();
  }
}
/*
Notes:

main
references
  table view / list view
fulldata
  table view
fulldata w/o theoretical (with a filter specified)
  table view
specific graphs with commentary
  small diam
  medium
  large
table: full / close / traj.graph

possible table components:
  vue-good-table
  vue-table-2
  vuejs.org/v2/examples/grid-component.html

origin  https://github.com/pangloss/vim-javascript.git (fetch)
origin  git://github.com/digitaltoad/vim-pug.git (fetch)
origin  https://github.com/posva/vim-vue.git (fetch)

*/
</script>
