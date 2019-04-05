<template>
  <div class="chartwrapper">
    <vue-plotly class="chart" :data="data" :layout="layout" :options="options" :autoResize="true"/>
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
</style>

<script>
import VuePlotly from '@statnett/vue-plotly';

export default {
  name: 'MnRePlot',
  components: {
    VuePlotly
  },
  props: {
    trajectories: Object
  },
  data() {
    return {
      layout: {
        hovermode: 'closest',
        margin: {
          l: 65,
          t: 25,
          r: 0,
          b: 65,
          pad: 4
        },
        xaxis: {
          // type: 'log',
          // title: 'Reynolds Number',
          title: 'log10(Reynolds Number)',
          autorange: true
        },
        yaxis: {
          type: 'linear',
          title: 'Mach Number',
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
      let x = [], y = [], z = [], maxMn = 3;
      Object.keys(this.trajectories).forEach(pointkey => {
        let w = 1./this.trajectories[pointkey].Re.length;
        for (let i = 0; i < this.trajectories[pointkey].Re.length; i += 1) {
          let x1 = this.trajectories[pointkey].Re[i],
              y1 = this.trajectories[pointkey].Mn[i];
          if (y1 > maxMn) {
            continue;
          }
          x.push(Math.log10(x1));  //DWM:: should just be x1
          y.push(y1);
          z.push(w);
        }
      });
      let traces = [{
        x: x,
        y: y,
        z: z,
        histfunc: 'max', // could be 'sum'
        nbinsx: 25,
        ybins: {
          start: 0,
          end: maxMn,
          size: 0.1,
        },
        showscale: false,
        colorscale: 'Greys',
        reversescale: true,
        type: 'histogram2d',
      }];
      return traces;
    }
  }
}
</script>
