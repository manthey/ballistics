<template>
  <table>
    <tr v-for="param in params" :key="param">
      <td>{{ param }}</td>
      <td>{{ params[param] }}</td>
    </tr>
  </table>
</template>

<style scoped>
table {
  height: 100%;
  max-width: 300px;
}
</style>

<script>
export default {
  name: 'DataTable',
  props: {
    datapoint: Object,
  },
  methods: {
    params() {
      return this.datapoint;
    }
  }
}
</script>
