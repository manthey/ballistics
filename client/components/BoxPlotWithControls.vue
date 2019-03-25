<template>
  <div id="boxplotwithcontrols">
    <PlotControls :filter="currentFilter" :binwidth="currentBinWidth" @filterupdate="filterUpdate" :nopoint="true" @binwidthupdate="binwidthUpdate" @toggleplottable="showTable"/>
    <BoxPlot :plotdata="plotdata" :filter="currentFilter" :binwidth="currentBinWidth"/>
  </div>
</template>

<style scoped>
#boxplotwithcontrols {
  width: 100%;
  height: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>

<script>
import BoxPlot from './BoxPlot.vue';
import PlotControls from './PlotControls.vue';

export default {
  name: 'BoxPlotWithControls',
  components: {
    PlotControls,
    BoxPlot
  },
  props: {
    filter: String,
    parameters: Object,
    plotdata: Array,
    binwidth: Number,
    references: Object
  },
  data() {
    return {
      currentBinWidth: +(this.binwidth || 25),
      currentFilter: this.filter
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
    binwidthSet(binwidth) {
      this.currentBinWidth = +binwidth;
      var route = this.$router.currentRoute;
      this.$router.push({
        path: route.path,
        query: Object.assign({}, route.query, {binwidth: binwidth})
      });
    },
    binwidthUpdate(value) {
      if (!(+value.binwidth > 0)) {
        return;
      }
      this.binwidthSet(+value.binwidth);
    },
    showTable() {
      let route = this.$router.currentRoute;
      this.$router.push({
        path: 'table',
        query: Object.assign({}, route.query)
      });
    }
  },
  watch: {
    $route (to) {
      this.currentFilter = to.query.filter;
      this.currentBinWidth = to.query.binwidth;
    }
  }
}
</script>
