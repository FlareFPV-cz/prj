<script>
    let condition = '';
    let recommendation = '';
    let loading = false;
    let error = '';
  
    async function fetchPrediction() {
      loading = true;
      error = '';
      try {
        const response = await fetch('http://localhost:8000/predict');
        if (!response.ok) {
          throw new Error('Failed to fetch prediction');
        }
        const data = await response.json();
        condition = data.condition;
        recommendation = data.recommendation;
      } catch (err) {
        error = err.message;
      } finally {
        loading = false;
      }
    }
</script>
  
  <main class="p-6 max-w-lg mx-auto bg-white shadow-lg rounded-lg">
    <h1 class="text-xl font-bold mb-4">Soil Condition Prediction</h1>
    <button class="px-4 py-2 bg-blue-500 text-white rounded" on:click={fetchPrediction} disabled={loading}>
      {loading ? 'Loading...' : 'Get Prediction'}
    </button>
  
    {#if error}
      <p class="text-red-500 mt-4">Error: {error}</p>
    {/if}
  
    {#if condition}
      <div class="mt-4 p-4 border rounded bg-gray-100">
        <p class="font-semibold">Condition: {condition}</p>
        <p class="mt-2">{recommendation}</p>
      </div>
    {/if}
  </main>  