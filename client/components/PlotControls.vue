<template>
  <div id="controls">
    Filter:
    <input id="filter" @change="update" :value="filter"
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
input {
  border: 1px inset rgb(227, 227, 277);
}
</style>

<script>
export default {
  name: 'PlotControls',
  props: {
    filter: String
  },
  methods: {
    update() {
      this.$emit('filterupdate', {
        filter: document.querySelector('#filter').value
      });
    }
  }
}
</script>
