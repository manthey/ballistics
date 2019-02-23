<template>
  <div id="app">
    <router-view class="view" :plotdata="plotdata" :references="references" :parameters="parameters"></router-view>
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
import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

export default {
  name: 'app',
  router: new VueRouter({
    mode: 'history',
    base: __dirname,
    routes: [{
      path: '/plot',
      component: PlotWithControls,
      props: (route) => ({
        filter: route.query.filter
      })
    }, {
      path: '*',
      redirect: '/plot'
    }]
  }),
  data() {
    return {
      plotdata: [],
      references: {},
      parameters: utils.Parameters
    };
  },
  methods: {
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
