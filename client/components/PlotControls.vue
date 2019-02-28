<template>
  <div id="controls">
    Filter:
    <input id="filter" @change="updateFilter" :value="filter"
     title="A javsacript expresion that will evaluate to true for each data point that should be plotted.  The data point is referenced as 'd', e.g., &quot;d.technique == 'range'&quot;"
     placeholder="An expression like &quot;d.technique == 'range'&quot;"/>
    Point:
    <input id="pointkey" @change="updatePointKey" :value="pointkey"/>
    <button id="plottable" @click="plotOrTable">{{ this.isTable ? 'Plot' : 'Table' }}</button>
  </div>
</template>

<style scoped>
#controls {
  display: flex;
  margin: 2px;
}
#filter {
  flex: 1;
  margin-left: 5px;
}
</style>

<script>
export default {
  name: 'PlotControls',
  props: {
    filter: String,
    isTable: Boolean,
    pointkey: String
  },
  methods: {
    plotOrTable() {
      //DWM::
    },
    updateFilter() {
      this.$emit('filterupdate', {
        filter: document.querySelector('#filter').value
      });
    },
    updatePointKey() {
      console.log(this.$router);
      this.$emit('pointkeyupdate', {
        pointkey: document.querySelector('#pointkey').value
      });
    }
  }
}
</script>
