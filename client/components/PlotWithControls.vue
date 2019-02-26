<template>
  <div id="plotwithcontrols">
    <PlotControls :filter="currentFilter" @filterupdate="filterUpdate"/>
    <div id="display">
      <BallisticsPlot :plotdata="plotdata" :filter="currentFilter" :pointkey="currentPoint" @pickPoint="pickPoint"/>
      <DataTable v-if="currentPoint" :plotdata="plotdata" :pointkey="currentPoint" :references="references" @closetable="pickPoint"/>
    </div>
  </div>
</template>

<style scoped>
#plotwithcontrols {
  width: 100%;
  height: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#display {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>

<script>
import BallisticsPlot from './BallisticsPlot.vue';
import DataTable from './DataTable.vue';
import PlotControls from './PlotControls.vue';

export default {
  name: 'PlotWithControls',
  components: {
    BallisticsPlot,
    DataTable,
    PlotControls
  },
  props: {
    filter: String,
    plotdata: Array,
    pointkey: String,
    references: Object
  },
  data() {
    return {
      currentFilter: this.filter,
      currentPoint: this.pointkey
    };
  },
  methods: {
    filterUpdate(value) {
      this.currentFilter = value.filter;
      // the currentRoute is immutable, so we have to send the change as anew
      // object.
      var route = this.$router.currentRoute;
      this.$router.push({
        path: route.path,
        query: Object.assign({}, route.query, {filter: value.filter})
      });
    },
    pickPoint(point) {
      let pointkey = point ? point['key'] + '-' + point['idx'] : '';
      this.currentPoint = pointkey;
      var route = this.$router.currentRoute;
      this.$router.push({
        path: route.path,
        query: Object.assign({}, route.query, {pointkey: pointkey})
      });
    }
  },
  watch: {
    $route (to) {
      this.currentFilter = to.query.filter;
      this.currentPoint = to.query.pointkey;
    }
  }
}
</script>
