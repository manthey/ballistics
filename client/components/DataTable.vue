<template>
  <div class="table_wrapper">
    <div class="table_scroll">
      <div v-html="this.references[params.key].cms"></div>
      <table>
        <tr v-for="param in Object.keys(params)" :key="param">
          <td>{{ param }}</td>
          <td>{{ params[param] }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<style scoped>
.table_wrapper {
  height: 100%;
  max-width: 300px;
  flex: 1;
  overflow-x: hidden;
  overflow-y: auto;
}
.table_scroll {
  font-family: sans-serif;
  font-size: 12px;
}
</style>

<script>
export default {
  name: 'DataTable',
  props: {
    datapoint: Object,
    references: Object
  },
  computed: {
    params() {
      let params = Object.assign({}, this.datapoint),
          fullkeys = Object.keys(params),
          keys,
          result = {};
      keys = fullkeys.filter(key => {
        return ['ax', 'ay', 'computation_time', 'max_height', 'time', 'vx', 'vy', 'x', 'y', 'year'].indexOf(key) === -1 && !key.startsWith('final_') && !key.startsWith('initial_');
      }).sort();
      fullkeys = fullkeys.sort();
      // disable to remove keys we don't care about
      /*
      fullkeys.map(key => {
        if (keys.indexOf(key) < 0) {
          keys.push(key);
        }
      });
      */
      keys.map(key => {
        result[key] = params[key];
      });
      return result;
    }
  }
}
</script>
