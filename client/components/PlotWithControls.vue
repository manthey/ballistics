<template>
  <div id="plotwithcontrols">
    <PlotControls :filter="currentFilter" @filterupdate="filterUpdate"/>
    <div id="display">
      <BallisticsPlot :plotdata="plotdata" :filter="currentFilter" :datapoint="currentPoint" @pickPoint="pickPoint"/>
      <DataTable v-if="currentPoint" :datapoint="currentPoint" :references="references" @closetable="pickPoint"/>
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
    references: Object
  },
  data() {
    return {
      currentFilter: this.filter,
      currentPoint: null,
    };
  },
  methods: {
    filterUpdate(value) {
      this.currentFilter = value.filter;
      this.$emit('filterupdate', value);
    },
    pickPoint(point) {
      this.currentPoint = point;
    }
  }
}
</script>
