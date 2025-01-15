<script>
  let file;

  async function handleUpload() {
    if (!file || !file.files[0]) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file.files[0]);

    const response = await fetch('http://localhost:8000/ndvi/', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();
    console.log(result);
  }
</script>

<div>
  <input type="file" bind:this={file} />
  <button on:click={handleUpload}>Upload and Analyze</button>
</div>
