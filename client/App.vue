<template>
  <div id="app">
    <PlotControls :query="query" @queryupdate="queryUpdate"/>
    <div id="display">
      <BallisticsPlot :plotdata="plotdata" :filter="query.filter" :datapoint="currentPoint" @pickPoint="pickPoint"/>
      <DataTable v-if="currentPoint" :datapoint="currentPoint" :references="references"/>
    </div>
  </div>
</template>

<style>
html,body,#app {
  width: 100%;
  height: 100%;
  margin: 0;
}
#app {
  display: flex;
  flex-direction: column;
}
#display {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>

<script>
import * as utils from './utils.js';
import BallisticsPlot from './components/BallisticsPlot.vue';
import DataTable from './components/DataTable.vue';
import PlotControls from './components/PlotControls.vue';

export default {
  name: 'app',
  components: {
    BallisticsPlot,
    DataTable,
    PlotControls
  },
  data() {
    return {
      currentPoint: null,
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
    pickPoint(point) {
      this.currentPoint = point;
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
  }
}
</script>
