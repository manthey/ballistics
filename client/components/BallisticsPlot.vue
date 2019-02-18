<template>
  <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true" @click="processClick" @hover="processClick"/>
</template>

<style scoped>
.chart {
  flex: 1;
}
</style>

<script>
import VuePlotly from '@statnett/vue-plotly';

export default {
  name: 'BallisticsPlot',
  components: {
    VuePlotly
  },
  props: {
    plotdata: Array,
    filter: String
  },
  data() {
    return {
      data: this.computeTraces(),
      layout: {
        xaxis: {
          type: 'date',
          autorange: true
        },
        yaxis: {
          type: 'log',
          autorange: true
        },
        hovermode: 'closest'
      },
      options: {},
      xoptions: {
        autosizable: true /*,
        responsive: true,
        scrollZoom: true */,
        staticPlot: false
      }
    }
  },
  watch: {
    filter() {
      this.data = this.computeTraces();
    },
    plotdata() {
      this.data = this.computeTraces();
    }
  },
  methods: {
    processClick(event) {
      console.log(event);
    },
    computeTraces() {
      let technique = {};
      let plotdata  = this.plotdata || [];
      plotdata.forEach((d) => technique[d.technique] = (technique[d.technique] || 0) + 1);
      let techlist = Object.keys(technique).sort((a, b) => technique[b] - technique[a]);
      if (this.filter) {
        // eslint-disable-next-line
        plotdata = plotdata.filter((d) => { return eval(this.filter); });
      }
      let traces = techlist.map((technique) => {
        let tidx = techlist.indexOf(technique),
            tdata = plotdata.filter((d) => { return d.technique == technique; });
        return {
          x: tdata.map((d) => d.date_filled),
          y: tdata.map((d) => d.power_factor),
          text: tdata.map((d) => d.power_factor),
          marker: {
            symbol: tidx,
            size: 10,
            opacity: 0.5
          },
          type: 'scattergl',
          mode: 'markers',
          hoverinfo: 'text',
          showlegend: true,
          name: technique + ' (' + tdata.length + ')'
        };
      });
      return traces;
    }
  }
}
</script>
