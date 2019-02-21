<template>
  <div id="controls">
    Filter:
    <input id="filter" @change="update" :value="query.filter"
     title="A javsacript expresion that will evaluate to true for each data point that should be plotted.  The data point is referenced as 'd', e.g., &quot;d.technique == 'range'&quot;"
     placeholder="An expression like &quot;d.technique == 'range'&quot;"/>
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
    query: Object
  },
  methods: {
    update() {
      this.$emit('queryupdate', {
        filter: document.querySelector('#filter').value
      });
    }
  }
}
</script>
