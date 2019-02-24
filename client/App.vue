<template>
  <v-app id="app">
    <v-toolbar flat dense dark height="32px">
      <v-toolbar-items>
        <v-btn flat to="/">Ballistics</v-btn>
        <v-btn flat to="/plot">Plot</v-btn>
        <v-menu bottom left nudge-bottom="32px">
          <v-btn slot="activator" icon class="square-btn">
            <v-icon>arrow_drop_down</v-icon>
          </v-btn>
          <v-list dark dense>
            <v-list-tile dense v-for="(item, i) in plots" :key="'plotmenu' + i" :title="item.tooltip" @click="gotoMenu(item)">
              <v-list-tile-title>{{ item.title }}</v-list-tile-title>
            </v-list-tile>
          </v-list>
        </v-menu>
        <v-spacer></v-spacer>
      </v-toolbar-items>
    </v-toolbar>
    <router-view class="view" :plotdata="plotdata" :references="references" :parameters="parameters"></router-view>
  </v-app>
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
.v-toolbar {
  z-index: 10;
}
.square-btn.v-btn--icon, .square-btn.v-btn--icon:hover, .square-btn.v-btn--icon::before {
  border-radius: 0;
  margin: 0;
}

</style>

<script>
import 'vuetify/dist/vuetify.min.css';
import 'material-design-icons-iconfont/dist/material-design-icons.css';

import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuetify from 'vuetify'

import * as utils from './utils.js';
import MainPage from './components/MainPage.vue';
import PlotWithControls from './components/PlotWithControls.vue';

Vue.use(VueRouter);
Vue.use(Vuetify, {iconfont: 'md'});

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
      parameters: utils.Parameters,
      plots: [{
        title: 'Better Experiments',
        tooltip: "Exclude theory, calorimeter, calculated, final_angle, and time techniques",
        link: '/plot',
        query: {filter: "['time','theory','calorimeter','calculated','final_angle'].indexOf(d.technique)<0"}
      }]
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
    },
    gotoMenu(event) {
      console.log(event);
      this.$router.push({path: event.path, params: event.params, query: event.query});
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
table view
specific graphs with commentary
  small diam
  medium
  large
table: full / close / traj.graph
*/
</script>
