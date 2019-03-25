<template>
  <div id="controls">
    Filter:
    <input id="filter" @change="updateFilter" :value="filter"
     title="A javsacript expression that will evaluate to true for each data point that should be plotted.  The data point is referenced as 'd', e.g., &quot;d.technique == 'range'&quot;"
     placeholder="An expression like &quot;d.technique == 'range'&quot;"/>
    <span v-if="binwidth">
      Width:
      <input id="binwidth" @change="updateBinWidth" :value="binwidth"
      placeholder="Bin width in years"
      title="Aggregate data in bins consisting of the specified number of years"/>
    </span>
    <span v-if="!nopoint">
      Point:
      <input id="pointkey" @change="updatePointKey" :value="pointkey"/>
    </span>
    <button id="plottable" @click="plotOrTable">{{ this.isTable ? 'Plot' : 'Table' }}</button>
  </div>
</template>

<style scoped>
#controls {
  display: flex;
  margin: 2px 5px;
}
#filter {
  flex: 1;
  margin-left: 5px;
  margin-right: 10px;
}
#pointkey {
  margin-left: 5px;
  margin-right: 10px;
}
</style>

<script>
export default {
  name: 'PlotControls',
  props: {
    binwidth: Number,
    filter: String,
    isTable: Boolean,
    nopoint: Boolean,
    pointkey: String
  },
  methods: {
    plotOrTable() {
      this.$emit('toggleplottable', {});
    },
    updateBinWidth() {
      this.$emit('binwidthupdate', {
        binwidth: document.querySelector('#binwidth').value
      });
    },
    updateFilter() {
      this.$emit('filterupdate', {
        filter: document.querySelector('#filter').value
      });
    },
    updatePointKey() {
      this.$emit('pointkeyupdate', {
        pointkey: document.querySelector('#pointkey').value
      });
    }
  }
}
</script>
