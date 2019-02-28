<template>
  <div id="tablewithcontrols">
    <PlotControls :filter="currentFilter" :pointkey="currentPoint" @filterupdate="filterUpdate" :isTable="true" @pointkeyupdate="pointkeyUpdate"/>
    <BallisticsTable id="display" :plotdata="plotdata" :filter="currentFilter" :pointkey="currentPoint"/>
  </div>
</template>

<style scoped>
#tablewithcontrols {
  width: 100%;
  height: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#display {
  flex: 1;
  overflow: hidden;
}
</style>

<script>
import BallisticsTable from './BallisticsTable.vue';
import PlotControls from './PlotControls.vue';

export default {
  name: 'TableWithControls',
  components: {
    BallisticsTable,
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
    pointkeyUpdate(value) {
      let pointkey = value.pointkey;
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
