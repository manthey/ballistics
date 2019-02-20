<template>
  <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true" @click="processClick" :key="datapoint ? 'chartwdp' : 'chart'"/>
</template>

<style scoped>
.chart {
  flex: 1;
}
</style>

<script>
import d3 from 'd3';
import math from 'mathjs';
import VuePlotly from '@statnett/vue-plotly';

export default {
  name: 'BallisticsPlot',
  components: {
    VuePlotly
  },
  props: {
    plotdata: Array,
    filter: String,
    datapoint: Object
  },
  data() {
    return {
      colors: d3.scale.category10().range().concat(d3.scale.category20b().range()).concat(d3.scale.category20c().range()),
      layout: {
        margin: {
          l: 65,
          t: 25,
          r: 0,
          b: 65,
          pad: 4
        },
        xaxis: {
          type: 'date',
          title: 'Date',
          autorange: true
        },
        yaxis: {
          type: 'log',
          title: 'Power Factor (J/kg)',
          autorange: true
        },
        hovermode: 'closest'
      },
      options: {
        autosizable: true,
        doubleClick: 'reset',
        responsive: true,
        scrollZoom: true
      }
    }
  },
  computed: {
    data() {
      let technique = {};
      let plotdata  = this.plotdata || [];
      plotdata.forEach((d) => technique[d.technique] = (technique[d.technique] || 0) + 1);
      let techlist = Object.keys(technique).sort((a, b) => technique[b] - technique[a]);
      if (this.filter) {
        try {
          let filterFunc = Function('d', '"use strict";return(' + this.filter + ')')
          // eslint-disable-next-line
          plotdata = plotdata.filter(filterFunc);
        } catch (err) {
          console.error('Filter failed: ' + this.filter);
          console.error(err);
        }
      }
      let traces = techlist.map((technique) => {
        let tidx = techlist.indexOf(technique),
            tdata = plotdata.filter((d) => { return d.technique == technique; }),
            color = this.colors[tidx % this.colors.length];
        return {
          data: tdata,
          x: tdata.map((d) => d.date_filled),
          y: tdata.map((d) => d.power_factor),
          text: tdata.map((d) => math.unit(+d.power_factor, 'J/kg').format({precision: 6, lowerExp: -6, upperExp: 9})),
          marker: {
            symbol: tidx,
            size: 10,
            color: tdata.map(d => d === this.datapoint ? '#000000' : color),
            opacity: tdata.map(d => d === this.datapoint ? 1 : 0.5)
          },
          type: tdata.length > 100 ? 'scatter' : 'scatter',
          // when plotly is fixed
          // type: tdata.length > 100 ? 'scattergl' : 'scatter',
          mode: 'markers',
          hoverinfo: 'text',
          showlegend: true,
          name: technique + ' (' + tdata.length + ')'
        };
      });
      return traces;
    }
  },
  methods: {
    processClick(event) {
      let point = event.points[0].data.data[event.points[0].pointIndex];
      this.$emit('pickPoint', point);
    }
  }
}
</script>
