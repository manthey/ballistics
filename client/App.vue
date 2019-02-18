<template>
  <div id="app">
    <PlotControls :query="query" @queryupdate="queryUpdate"/>
    <div id="display">
      <BallisticsPlot :plotdata="plotdata" :filter="query.filter"/>
      <DataTable v-if="currentPoint" :datapoint="currentPoint"/>
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
}
</style>

<script>
import BallisticsPlot from './components/BallisticsPlot.vue';
import PlotControls from './components/PlotControls.vue';
import DataTable from './components/DataTable.vue';

export default {
  name: 'app',
  components: {
    BallisticsPlot,
    PlotControls,
    DataTable
  },
  data() {
    return {
      currentPoint: null,
      plotdata: [],
      query: this.currentUrlQuery(),
      references: {}
    };
  },
  methods: {
    currentUrlQuery() {
      let query = {}
      document.location.search.replace(/(^\?)/, '').split('&')
        .filter(n => n)
        .forEach(n => {
          n = n.replace(/\+/g, '%20').split('=').map(n => decodeURIComponent(n));
          query[n[0]] = n[1];
        });
      return query;
    },
    queryUpdate(updates) {
      this.query = Object.assign({}, this.query, updates);
    },
    fetchData() {
      fetch('data/totallist.json').then(resp => resp.json()).then(data => {
        this.plotdata = data;
      }).catch(err => { throw err; });
    },
    fetchReferences() {
      fetch('data/references.json').then(resp => resp.json()).then(data => {
        this.references = data;
      }).catch(err => { throw err; });
    }
  },
  watch: {
    query(newval) {
      let newurl = window.location.protocol + '//' + window.location.host +
        window.location.pathname + '?' + Object.keys(newval).map(k => encodeURIComponent(k) + '=' + encodeURIComponent(newval[k])).join('&');
      // to update history
      window.history.pushState(newval, '', newurl);
      // to change the url without changing history
      // window.history.replaceState(newval, '', newurl);
    }
  },
  mounted: function () {
    this.fetchData();
    this.fetchReferences();
  }
}
</script>
