<template>
  <div id="app">
    <el-menu router mode="horizontal" background-color="#444" text-color="#EEE" active-text-color="#EE0">
      <el-menu-item index="home" :route="{path: '/'}">Home</el-menu-item>
      <el-submenu index="plot">
        <template slot="title">Plot</template>
        <el-menu-item v-for="(item, i) in plots" :key="'plotmenu' + i" :index="item.index" :route="{path: item.path, query: item.query}" :title="item.tooltip">{{ item.text }}</el-menu-item>
      </el-submenu>
      <el-menu-item index="references" :route="{path: '/references'}">References</el-menu-item>
    </el-menu>
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
.el-menu--horizontal>.el-menu-item, .el-menu--horizontal>.el-submenu .el-submenu__title {
  height: 40px;
  line-height: 40px;
}
</style>

<script>
import 'element-ui/lib/theme-chalk/index.css';

import Vue from 'vue';
import VueRouter from 'vue-router';
import ElementUI from 'element-ui';

import * as utils from './utils.js';
import MainPage from './components/MainPage.vue';
import PlotWithControls from './components/PlotWithControls.vue';
import References from './components/References.vue';

Vue.use(VueRouter);
Vue.use(ElementUI, {size: 'small'});

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
        filter: route.query.filter,
        pointkey: route.query.pointkey
      })
    }, {
      path: '/references',
      component: References
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
        index: 'plot-full',
        text: 'Full Data',
        path: '/plot',
      }, {
        index: 'plot-preferred',
        text: 'Preferred Experiments',
        tooltip: "Exclude theory, calorimeter, calculated, final_angle, and time techniques",
        path: '/plot',
        query: {filter: "['time','theory','calorimeter','calculated','final_angle'].indexOf(d.technique)<0"}
      }]
    };
  },
  methods: {
    fetchData() {
      fetch('totallist.json').then(resp => resp.json()).then(data => {
        this.plotdata = data;
        utils.updatePointKeys(data);
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
table view
specific graphs with commentary
  small diam
  medium
  large
techniques
  computation methods
  accuracy
*/
</script>
