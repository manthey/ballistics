<template>
  <div class="chartwrapper">
    <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true"/>
    <div id="controls">
      <select v-model="meanselected">
        <option v-for="option in meanoptions" v-bind:value="option.value" :key="'meanoption:' + option.value">{{ option.text }}</option>
      </select>
    </div>
  </div>
</template>

<style>
.plot-container.plotly {
  width: 100%;
  height: 100%;
}
</style>

<style scoped>
.chartwrapper {
  flex: 1;
}
.chart {
  width: 100%;
  height: 100%;
}
#controls {
  position: absolute;
  left: 2px;
  bottom: 2px;
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
      },
      meanselected: 'nomean',
      meanoptions: [{
        value: 'nomean', text: 'No Mean Line'
      }, {
        value: 'mean', text: 'Mean Line'
      }, {
        value: 'sd', text: 'Mean & Std.Dev.'
      }, {
        value: 'violin', text: 'Violin'
      }]
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
            color: 'black',
          },
          meanline: {
            visible: true,  // false or true for violin plot
          },
          boxmean: this.meanselected === 'mean' ? true : this.meanselected === 'sd' ? 'sd' : false,  // false, true, or 'sd', for box plot
          // 'violin' works but is strange due to the log scale
          type: this.meanselected === 'violin' ? 'violin' : 'box',
          name: '' + (minyear + bin * binwidth)
        });
      }
      return traces;
    }
  }
}
</script>
