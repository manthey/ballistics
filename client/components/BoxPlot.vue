<template>
  <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true"/>
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
import VuePlotly from '@statnett/vue-plotly';

export default {
  name: 'BoxPlot',
  components: {
    VuePlotly
  },
  props: {
    plotdata: Array,
    binwidth: Number,
    filter: String
  },
  data() {
    return {
      layout: {
        hovermode: 'closest',
        showlegend: false,
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
      let plotdata  = this.plotdata || [];
      let minyear = 0, maxyear = 0, binwidth = this.binwidth || 25, bins;
      let traces = [];
      plotdata.forEach(d => {
        let year = +d.year;
        if (!minyear || year < minyear) {
          minyear = year;
        }
        if (!maxyear || year > maxyear) {
          maxyear = year;
        }
      });
      minyear = Math.floor(minyear / binwidth) * binwidth;
      maxyear = Math.ceil((maxyear + binwidth - 1) / binwidth) * binwidth;
      bins = (maxyear - minyear) / binwidth;
      if (this.filter) {
        plotdata = utils.filterData(plotdata, this.filter);
      }
      for (var bin = 0; bin < bins; bin += 1) {
        let tdata = plotdata.filter(d => Math.floor((+d.year - minyear) / binwidth) === bin);
        traces.push({
          y: tdata.map(d => d.power_factor),
          hovertext: tdata.map(d => {
            return `${d._power_factor || d.power_factor}<br>${d.ref}`;
          }),
          hoverinfo: 'text',
          points: 'none',
          box: {
            visible: true
          },
          line: {
            color: 'blue',
          },
          meanline: {
            visible: true
          },
          // 'violin' works but is strange due to the log scale
          type: 'box',
          name: '' + (minyear + bin * binwidth)
        });
      }
      return traces;
    }
  }
}
</script>
