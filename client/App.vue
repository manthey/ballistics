<template>
  <div id="app">
    <div class="cssmenu">
      <ul>
        <li><router-link :to="{path: '/'}">Home</router-link></li>
        <li><router-link :to="{path: '/plot'}">Plot</router-link>
          <ul>
            <li v-for="(item, i) in plots" :key="'plotmenu' + i"><router-link :to="{path: item.path, query: item.query}" :title="item.tooltip">{{ item.text }}</router-link></li>
          </ul>
        </li>
        <li><router-link :to="{path: '/table'}">Table</router-link>
          <ul>
            <li v-for="(item, i) in tables" :key="'tablemenu' + i"><router-link :to="{path: item.path, query: item.query}" :title="item.tooltip">{{ item.text }}</router-link></li>
          </ul>
        </li>
        <li><router-link :to="{path: '/computation'}">Computation</router-link></li>
        <li><router-link :to="{path: '/references'}">References</router-link></li>
      </ul>
    </div>
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
<style src="./components/cssmenu.css" scoped/>

<script>
import Vue from 'vue';
import VueMarkdown from 'vue-markdown';
import VueRouter from 'vue-router';

import * as utils from './utils.js';
import Computation from './components/Computation.vue';
import MainPage from './components/MainPage.vue';
import PlotWithControls from './components/PlotWithControls.vue';
import References from './components/References.vue';
import TableWithControls from './components/TableWithControls.vue';

Vue.use(VueRouter);
Vue.component('vue-markdown', VueMarkdown);

export default {
  name: 'app',
  router: new VueRouter({
    mode: 'history',
    base: __dirname,
    routes: [{
      path: '/',
      component: MainPage
    }, {
      path: '/computation',
      component: Computation
    }, {
      path: '/plot',
      component: PlotWithControls,
      props: (route) => ({
        filter: route.query.filter,
        pointkey: route.query.pointkey
      })
    }, {
      path: '/references',
      component: References,
      props: (route) => ({
        refkey: route.query.refkey
      })
    }, {
      path: '/table',
      component: TableWithControls,
      props: (route) => ({
        filter: route.query.filter,
        pointkey: route.query.pointkey
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
          index: 'plot-full',
          text: 'Full Data',
          path: '/plot',
        }, {
          index: 'plot-preferred',
          text: 'Preferred Experiments',
          tooltip: "Exclude theory, calorimeter, calculated, final_angle, and time techniques",
          path: '/plot',
          query: {filter: "['time','theory','calorimeter','calculated','final_angle'].indexOf(d.technique)<0"}
        }],
      tables: [{
          index: 'table-full',
          text: 'Full Data',
          path: '/table',
        }, {
          index: 'table-preferred',
          text: 'Preferred Experiments',
          tooltip: "Exclude theory, calorimeter, calculated, final_angle, and time techniques",
          path: '/table',
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
        this.parameters = Object.assign({}, utils.updateParameters(data));
      }).catch(err => { throw err; });
    },
    updateMenu(to) {
      to = to || this.$router.currentRoute;
      let menu = this.$children.filter(child => child.$options._componentTag === 'router-link'),
          best, okay;
      menu.forEach(menu => {
        if (best === undefined && to === menu.to) {
          best = menu;
        }
        if (okay === undefined && to.path === menu.to.path) {
          okay = menu;
        }
      });
      if (best || okay) {
        let oldactive = document.querySelector('.cssmenu .active');
        if (oldactive) {
          oldactive.classList.toggle('active');
        }
        (best || okay).$el.parentElement.classList.toggle('active');
        document.activeElement.blur();
      }
    }
  },
  mounted: function () {
    this.fetchData();
    this.fetchReferences();
    this.fetchParameters();
    this.$nextTick(this.updateMenu);
  },
  watch: {
    $route(to) {
      this.updateMenu(to);
    }
  },
}
/*
Notes:

specific graphs with commentary
  small diam
  medium
  large
techniques
  computation methods
  accuracy
github

switch to own menu component and I can get rid of element-ui.  See luxbar
*/
</script>
