<template>
  <div id="controls">
    Filter:
    <input id="filter" @change="update" :value="query.filter"/>
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
