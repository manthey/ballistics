<template>
  <div class="chartwrapper">
    <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true" @click="processClick" @relayout="adjustLegend" :key="pointkey ? 'chartwdp' : 'chart'"/>
    <div id="controls">
      <select v-model="regressionselected">
        <option v-for="option in regressionoptions" v-bind:value="option.value" :key="'regressionoption:' + option.value">{{ option.text }}</option>
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
import d3 from 'd3';
import regression from 'regression';
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
      },
      regressionselected: 'none',
      regressionoptions: [{
        value: 'none', text: 'None',
      }, {
        value: 'o0', text: 'Linear Regression Order 0'
      }, {
        value: 'o1', text: 'Linear Regression Order 1'
      }, {
        value: 'o2', text: 'Linear Regression Order 2'
      }, {
        value: 'o3', text: 'Linear Regression Order 3'
      }, {
        value: 'o4', text: 'Linear Regression Order 4'
      }, {
        value: 'o5', text: 'Linear Regression Order 5'
      }, {
        value: 'l0', text: 'Log Regression Order 0'
      }, {
        value: 'l1', text: 'Log Regression Order 1'
      }, {
        value: 'l2', text: 'Log Regression Order 2'
      }, {
        value: 'l3', text: 'Log Regression Order 3'
      }, {
        value: 'l4', text: 'Log Regression Order 4'
      }, {
        value: 'l5', text: 'Log Regression Order 5'
      }]
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

      if (plotdata.length >= 5 && this.regressionselected !== 'none') {
        let uselog = this.regressionselected.substr(0, 1) === 'l',
            order = parseInt(this.regressionselected.substr(1), 10);
        let minx, maxx;
        let regdata = plotdata.map(d => {
          let x = new Date(d.date_filled).getTime();
          if (minx === undefined || x < minx) { minx = x; }
          if (maxx === undefined || x > maxx) { maxx = x; }
          return [x, uselog ? Math.log10(d.power_factor) : d.power_factor];
        });
        let reg = regression.polynomial(regdata, {order: order, precision: 100});
        let regx = [], regy = [], steps = 100;
        for (let i = 0; i <= steps; i += 1) {
          let x = (maxx - minx) * i / steps + minx;
          regx.push(new Date(x).toISOString().substr(0, 10));
          regy.push(uselog ? Math.pow(10, reg.predict(x)[1]) : reg.predict(x)[1]);
        }
        traces.push({
          x: regx,
          y: regy,
          type: 'scatter',
          mode: 'line',
          name: 'regression'
        });
      }

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
