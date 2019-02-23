<template>
  <div id="app">
    <v-toolbar flat dense dark height="32px">
      <v-toolbar-items>
        <v-btn flat to="/">Ballistics</v-btn>
        <v-btn flat to="/plot">Plot</v-btn>
        <v-spacer></v-spacer>
      </v-toolbar-items>
    </v-toolbar>
    <router-view class="view" :plotdata="plotdata" :references="references" :parameters="parameters"></router-view>
  </div>
</template>

<style>
html,body,#app {
  width: 100%;
  height: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  font-family: sans-serif;
}
.view {
  flex: 1;
}
</style>

<script>
import 'vuetify/dist/vuetify.min.css';

import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuetify from 'vuetify'

import * as utils from './utils.js';
import MainPage from './components/MainPage.vue';
import PlotWithControls from './components/PlotWithControls.vue';

Vue.use(VueRouter);
Vue.use(Vuetify);

export default {
  name: 'app',
  router: new VueRouter({
    mode: 'history',
    base: __dirname,
    routes: [{
      path: '/',
      component: MainPage
    }, {
      path: '/plot',
      component: PlotWithControls,
      props: (route) => ({
        filter: route.query.filter
      })
    }, {
      path: '*',
      redirect: '/'
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

main (needs improvement)
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
  vuetify
*/
</script>
