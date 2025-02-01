<script lang="ts">
    import { onMount } from 'svelte';
    import '../css/crop-health.css';

    let cropData = null;
    let loading = false;
    let error = null;
    let selectedFile = null;

    async function analyzeCropHealth(file) {
        loading = true;
        error = null;
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/assess-crop-health/', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });
            if (!response.ok) throw new Error('Failed to analyze crop health');
            cropData = await response.json();
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    function calculateCirclePosition(value, index, total) {
        const radius = 120;
        const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
        return {
            x: 150 + radius * Math.cos(angle),
            y: 150 + radius * Math.sin(angle)
        };
    }

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            selectedFile = file;
            analyzeCropHealth(file);
        } else {
            error = 'Please select a valid image file';
        }
    }
</script>

<div class="crop-health-container">
    <h1>Crop Health Analysis Dashboard</h1>

    <div class="upload-section">
        <input
            type="file"
            accept="image/*"
            on:change={handleFileSelect}
            class="file-input"
            id="cropImage"
        >
        <label for="cropImage" class="file-label">
            Choose Image
        </label>
    </div>

    {#if loading}
        <div class="loading">Analyzing crop health...</div>
    {/if}

    {#if error}
        <div class="error">{error}</div>
    {/if}

    {#if cropData}
        <div class="dashboard-grid">
            <div class="card health-status">
                <h2>Health Status</h2>
                <div class="status-badge {cropData.health_status.toLowerCase()}">
                    {cropData.health_status}
                </div>
                <div class="confidence">
                    Confidence: {(cropData.confidence_score * 100).toFixed(1)}%
                </div>
                <div class="severity">
                    Severity: {cropData.severity_level}
                </div>
            </div>

            <div class="card metrics">
                <h2>Disease Analysis</h2>
                <div class="metric-item">
                    <span>Disease Probability:</span>
                    <div class="progress-bar">
                        <div class="progress" style="width: {cropData.disease_probability * 100}%"></div>
                    </div>
                    <span>{(cropData.disease_probability * 100).toFixed(1)}%</span>
                </div>
                {#if cropData.affected_areas.length > 0}
                    <div class="affected-areas">
                        <h3>Affected Areas:</h3>
                        <ul>
                            {#each cropData.affected_areas as area}
                                <li>{area}</li>
                            {/each}
                        </ul>
                    </div>
                {/if}
            </div>

            <div class="card environmental-factors">
                <h2>Environmental Factors</h2>
                {#each Object.entries(cropData.environmental_factors) as [factor, value]}
                    <div class="factor-item">
                        <span>{factor.replace('_', ' ')}:</span>
                        <div class="progress-bar">
                            <div class="progress" style="width: {(Number(value) * 100).toFixed(1)}%"></div>
                        </div>
                        <span>{(Number(value) * 100).toFixed(1)}%</span>
                    </div>
                {/each}
            </div>

            <div class="card visualization">
                <h2>Health Metrics</h2>
                <div class="metrics-visualization">
                    <svg viewBox="0 0 300 300" class="metrics-svg">
                        {#if cropData?.metrics}
                            <!-- Center circle -->
                            <circle cx="150" cy="150" r="50" class="center-circle" />
                            
                            <!-- Metric circles -->
                            {#each ['Leaf Color', 'Texture Uniformity', 'Growth Rate', 'Stress Indicators'] as metric, i}
                                {@const pos = calculateCirclePosition(cropData.metrics[metric.toLowerCase().replace(' ', '_')] || 0, i, 4)}
                                {@const value = cropData.metrics[metric.toLowerCase().replace(' ', '_')] || 0}
                                
                                <g class="metric-group">
                                    <!-- Connection line -->
                                    <line 
                                        x1="150" 
                                        y1="150" 
                                        x2={pos.x} 
                                        y2={pos.y} 
                                        class="connection-line"
                                    />
                                    
                                    <!-- Metric circle -->
                                    <circle 
                                        cx={pos.x} 
                                        cy={pos.y} 
                                        r="40" 
                                        class="metric-circle"
                                        style="--value: {value}%"
                                    />
                                    
                                    <!-- Metric value -->
                                    <text 
                                        x={pos.x} 
                                        y={pos.y} 
                                        class="metric-value"
                                        text-anchor="middle" 
                                        dominant-baseline="middle"
                                    >
                                        {value}%
                                    </text>
                                    
                                    <!-- Metric label -->
                                    <text 
                                        x={pos.x} 
                                        y={pos.y + 55} 
                                        class="metric-label"
                                        text-anchor="middle"
                                    >
                                        {metric}
                                    </text>
                                </g>
                            {/each}
                        {/if}
                    </svg>
                </div>
            </div>

            <div class="card recommendations">
                <h2>Recommendations</h2>
                <ul class="recommendation-list">
                    {#each cropData.recommendations as recommendation}
                        <li>{recommendation}</li>
                    {/each}
                </ul>
            </div>

            <div class="card follow-up">
                <h2>Follow-up Actions</h2>
                <ul class="action-list">
                    {#each cropData.follow_up_actions as action}
                        <li>{action}</li>
                    {/each}
                </ul>
            </div>
        </div>
    {/if}
</div>