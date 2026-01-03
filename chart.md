# Chart Implementation

The project uses **Chart.js** to create interactive and visually appealing charts for data visualization. Charts are implemented across the dashboard and portfolio sections to display analytics like equity curves, trade distributions, and balance history.

The implementation process involves three main steps:

1.  **Include Library**: The Chart.js library is included via a CDN in the relevant templates.
2.  **Add Canvas**: An HTML `<canvas>` element is added to the template to serve as the rendering target for the chart.
3.  **Initialize Chart**: JavaScript is used to initialize the chart, configure its appearance, and populate it with data passed from the Django backend.

## Example: Equity Curve Chart

This example from `templates/core/dashboard.html` shows how the equity curve is rendered.

### 1. HTML Canvas

A `<canvas>` element with a unique ID is placed in the template.

```html
<div class="chart-container">
    <canvas id="equityChart"></canvas>
</div>
```

### 2. Chart.js Library

The library is included at the end of the template.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### 3. JavaScript Initialization

A `<script>` block contains the logic to create the chart. Data is injected from the Django view into the `labels` and `data` properties using template variables. The `|safe` filter is used to ensure the JSON data is correctly interpreted by the browser.

```javascript
<script>
    document.addEventListener('DOMContentLoaded', function () {
        const equityCtx = document.getElementById('equityChart').getContext('2d');
        
        new Chart(equityCtx, {
            type: 'line',
            data: {
                labels: {{ chart_labels|safe }},
                datasets: [{
                    label: 'Cumulative P&L',
                    data: {{ chart_data|safe }},
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.3)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                // Additional customization options...
            }
        });
    });
</script>
```

This pattern is consistently used for all charts throughout the application, with different chart types (`line`, `doughnut`, `bar`) and data sources as needed.
