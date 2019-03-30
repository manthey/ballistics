<template>
  <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true" @click="processClick" @relayout="adjustLegend" :key="pointkey ? 'chartwdp' : 'chart'"/>
</template>

<style>
.plot-container.plotly {
  width: 100%;
  height: 100%;
}
</style>

<style scoped>
.chart {
  flex: 1;
}
</style>

<script>
import * as utils from '../utils.js';
import d3 from 'd3';
import VuePlotly from '@statnett/vue-plotly';

export default {
  name: 'BallisticsPlot',
  components: {
    VuePlotly
  },
  props: {
    plotdata: Array,
    filter: String,
    pointkey: String
  },
  data() {
    return {
      colors: d3.scale.category10().range().concat(d3.scale.category20b().range()).concat(d3.scale.category20c().range()),
      layout: {
        hovermode: 'closest',
        showlegend: true,
        legend: {
          orientation: 'v'
        },
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
        }
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
      plotdata.forEach(d => technique[d.technique] = (technique[d.technique] || 0) + 1);
      let techlist = Object.keys(technique).sort((a, b) => technique[b] - technique[a]);
      if (this.filter) {
        plotdata = utils.filterData(plotdata, this.filter);
      }
      let traces = techlist.map((technique) => {
        let tidx = techlist.indexOf(technique),
            tdata = plotdata.filter(d => { return d.technique == technique; }),
            color = this.colors[tidx % this.colors.length];
        return {
          data: tdata,
          x: tdata.map(d => d.date_filled),
          y: tdata.map(d => d.power_factor),
          hovertext: tdata.map(d => {
            return `${d._power_factor || d.power_factor}<br>${d.ref}`;
          }),
          marker: {
            symbol: tidx,
            size: 10,
            color: tdata.map(d => d.pointkey === this.pointkey ? '#000000' : color),
            opacity: tdata.map(d => d.pointkey === this.pointkey ? 1 : 0.5)
          },
          type: tdata.length > 100 ? 'scattergl' : 'scatter',
          mode: 'markers',
          hoverinfo: 'text',
          // showlegend: true,
          name: technique + ' (' + tdata.length + ')'
        };
      });
      this.$nextTick(this.adjustLegend);
      return traces;
    }
  },
  methods: {
    adjustLegend() {
      this.layout.showlegend = this.$el.clientWidth >= 500;
    },
    processClick(event) {
      let point = event.points[0].data.data[event.points[0].pointIndex];
      this.$emit('pickPoint', point);
    }
  }
}
</script>
