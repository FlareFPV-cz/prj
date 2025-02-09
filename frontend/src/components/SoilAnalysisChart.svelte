<script>
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  export let soilData;
  let chartCanvas;
  let chart;

  $: if (soilData && chartCanvas) {
    createChart();
  }

  function createChart() {
    if (chart) {
      chart.destroy();
    }

    const layers = soilData.properties.layers;
    const datasets = layers.map(layer => {
      const depthValues = layer.depths.map(depth => depth.values.mean || 0);
      const depthLabels = layer.depths.map(depth => depth.label);
      
      return {
        label: layer.name,
        data: depthValues,
        borderColor: getRandomColor(),
        fill: false,
        tension: 0.4
      };
    });

    const depthLabels = layers[0].depths.map(depth => depth.label);

    chart = new Chart(chartCanvas, {
      type: 'line',
      data: {
        labels: depthLabels,
        datasets: datasets
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Soil Properties by Depth'
          },
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Value'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Depth'
            }
          }
        }
      }
    });
  }

  function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  onMount(() => {
    if (soilData) {
      createChart();
    }
  });
</script>

<div class="chart-container">
  <canvas bind:this={chartCanvas}></canvas>
</div>

<style>
  .chart-container {
    width: 100%;
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
</style>