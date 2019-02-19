<template>
  <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true" @click="processClick" :key="datapoint ? 'chartwdp' : 'chart'"/>
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
    filter: String,
    datapoint: Object
  },
  data() {
    return {
      data: this.computeTraces(),
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
          title: 'Power Factor (J/g)',
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
  watch: {
    datapoint(newval, oldval) {
      if ((!oldval && newval) || (!newval && oldval)) {
        this.$forceUpdate();
      }
    },
    filter() {
      this.data = this.computeTraces();
    },
    plotdata() {
      this.data = this.computeTraces();
    }
  },
  methods: {
    processClick(event) {
      let point = event.points[0].data.data[event.points[0].pointIndex];
      this.$emit('pickPoint', point);
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
          data: tdata,
          x: tdata.map((d) => d.date_filled),
          y: tdata.map((d) => d.power_factor),
          text: tdata.map((d) => d.power_factor),
          marker: {
            symbol: tidx,
            size: 10,
            opacity: 0.5
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
  }
}
</script>
