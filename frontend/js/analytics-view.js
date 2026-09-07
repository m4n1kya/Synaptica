class AnalyticsView {
    constructor() {
        this.container = document.getElementById('analytics-view');
        this.timelineChart = null;
        this.distributionChart = null;
        this.densityChart = null;
        this.initialized = false;
        
        // Colors from our bright blue semantic palette
        this.colors = {
            primary: '#2196F3',
            secondary: '#90CAF9',
            tertiary: '#E3F2FD',
            quaternary: '#1565C0', // Replaced 0D47A1
            background: '#0a0a0a',
            surface: 'rgba(25, 55, 109, 0.25)',
            border: 'rgba(255, 255, 255, 0.06)',
            text: '#f1f5f9',
            textMuted: '#64748b'
        };

        // Shared chart options for Bklit UI aesthetic
        this.commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 10, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true,
                    boxPadding: 6,
                    usePointStyle: true,
                    titleFont: {
                        family: "'Inter', sans-serif",
                        size: 13,
                        weight: '600'
                    },
                    bodyFont: {
                        family: "'Inter', sans-serif",
                        size: 13
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false,
            }
        };

        this.gridOptions = {
            color: 'rgba(255, 255, 255, 0.05)',
            drawBorder: false,
            tickLength: 0,
            borderDash: [5, 5]
        };

        this.scaleOptions = {
            x: {
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    color: this.colors.textMuted,
                    font: {
                        family: "'Inter', sans-serif",
                        size: 11
                    },
                    padding: 10
                }
            },
            y: {
                grid: this.gridOptions,
                border: {
                    display: false
                },
                ticks: {
                    color: this.colors.textMuted,
                    font: {
                        family: "'Inter', sans-serif",
                        size: 11
                    },
                    padding: 10
                }
            }
        };
    }

    init(data) {
        if (!this.initialized) {
            this.renderKPIs(data);
            this.initTimelineChart(data);
            this.initDistributionChart(data);
            this.initDensityChart(data);
            this.initialized = true;
        } else {
            this.updateCharts(data);
        }
    }

    renderKPIs(data) {
        const kpiContainer = document.getElementById('analytics-kpis');
        
        let totalDocs = data.documents ? data.documents.length : 3;
        let totalFacts = data.facts ? data.facts.length : 1245;
        let totalRels = data.relationships ? data.relationships.length : 382;
        let cases = data.cases ? data.cases.length : 42;

        kpiContainer.innerHTML = `
            <div class="glass-card" style="padding: var(--space-5);">
                <div class="text-sm text-muted mb-2 font-medium uppercase tracking-wider">Total Documents</div>
                <div class="text-3xl font-bold" style="color: var(--text-primary); font-family: var(--font-mono);">${totalDocs}</div>
            </div>
            <div class="glass-card" style="padding: var(--space-5);">
                <div class="text-sm text-muted mb-2 font-medium uppercase tracking-wider">Facts Extracted</div>
                <div class="text-3xl font-bold" style="color: var(--text-primary); font-family: var(--font-mono);">${totalFacts}</div>
            </div>
            <div class="glass-card" style="padding: var(--space-5);">
                <div class="text-sm text-muted mb-2 font-medium uppercase tracking-wider">Relationships</div>
                <div class="text-3xl font-bold" style="color: var(--text-primary); font-family: var(--font-mono);">${totalRels}</div>
            </div>
            <div class="glass-card" style="padding: var(--space-5);">
                <div class="text-sm text-muted mb-2 font-medium uppercase tracking-wider">Active Cases</div>
                <div class="text-3xl font-bold" style="color: var(--text-primary); font-family: var(--font-mono);">${cases}</div>
            </div>
        `;
    }

    initTimelineChart(data) {
        const ctx = document.getElementById('timeline-chart').getContext('2d');
        
        // Mock data for timeline
        const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const values = [120, 190, 150, 280, 220, 340, 310, 420, 380, 490, 450, 560];

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 350);
        gradient.addColorStop(0, 'rgba(144, 202, 249, 0.4)'); // secondary color with opacity
        gradient.addColorStop(1, 'rgba(144, 202, 249, 0.0)');

        this.timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Facts Extracted',
                    data: values,
                    borderColor: this.colors.secondary,
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointBackgroundColor: this.colors.secondary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4 // Smooth curves like Bklit
                }]
            },
            options: {
                ...this.commonOptions,
                scales: this.scaleOptions
            }
        });
    }

    initDistributionChart(data) {
        const ctx = document.getElementById('distribution-chart').getContext('2d');
        
        // Count relationships by type
        let corr = 0, contra = 0, ctxDiff = 0, fail = 0;
        if (data.relationships) {
            data.relationships.forEach(r => {
                if(r.type === 'corroborates') corr++;
                else if(r.type === 'contradicts') contra++;
                else if(r.type === 'contextual_difference') ctxDiff++;
                else if(r.type === 'extraction_failure') fail++;
            });
        } else {
            // Mock data
            corr = 210;
            contra = 85;
            ctxDiff = 120;
            fail = 15;
        }

        const total = corr + contra + ctxDiff + fail;

        // Custom plugin for center text (Bklit PieCenter equivalent)
        const centerTextPlugin = {
            id: 'centerText',
            beforeDraw: function(chart) {
                if (chart.config.type !== 'doughnut') return;
                
                const ctx = chart.ctx;
                const width = chart.width;
                const height = chart.height;
                
                // Get active element to show dynamic center text
                const activeElements = chart.getActiveElements();
                
                let text = "Total";
                let val = total.toString();
                let color = "#f1f5f9"; // var(--text-primary)
                
                if (activeElements.length > 0) {
                    const index = activeElements[0].index;
                    text = chart.data.labels[index];
                    val = chart.data.datasets[0].data[index].toString();
                    color = chart.data.datasets[0].backgroundColor[index];
                }

                ctx.restore();
                
                // Draw Value
                ctx.font = "bold 32px 'Inter', monospace";
                ctx.textBaseline = "middle";
                ctx.fillStyle = color;
                const valX = Math.round((width - ctx.measureText(val).width) / 2);
                const valY = height / 2 - 10;
                ctx.fillText(val, valX, valY);
                
                // Draw Label
                ctx.font = "13px 'Inter', sans-serif";
                ctx.fillStyle = "#94a3b8"; // textMuted
                const textX = Math.round((width - ctx.measureText(text).width) / 2);
                const textY = height / 2 + 20;
                ctx.fillText(text, textX, textY);
                
                ctx.save();
            }
        };

        this.distributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Agreements', 'Discrepancies', 'Variations', 'Processing Errors'],
                datasets: [{
                    data: [corr, contra, ctxDiff, fail],
                    backgroundColor: [
                        '#90CAF9', // Corroborate
                        '#2196F3', // Contradict
                        '#E3F2FD', // Contextual
                        '#1565C0'  // Failure
                    ],
                    borderWidth: 2,
                    borderColor: this.colors.background,
                    hoverBorderColor: '#ffffff',
                    hoverBorderWidth: 2,
                    hoverOffset: 12 // Bklit style "grow on hover"
                }]
            },
            options: {
                ...this.commonOptions,
                cutout: '78%', // Slightly thinner donut
                plugins: {
                    ...this.commonOptions.plugins,
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: this.colors.textMuted,
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                family: "'Inter', sans-serif",
                                size: 12
                            }
                        }
                    }
                },
                onHover: (event, elements, chart) => {
                    // Force re-render to update center text on hover
                    chart.update();
                    
                    // Bklit "fade non-hovered slices" effect
                    const dataset = chart.data.datasets[0];
                    if (elements.length > 0) {
                        const activeIndex = elements[0].index;
                        dataset.backgroundColor = dataset.data.map((_, i) => 
                            i === activeIndex 
                                ? dataset.backgroundColor[i].replace(/[^,]+(?=\))/, '1') // Ensure full opacity
                                : [
                                    'rgba(144, 202, 249, 0.4)', // Faded Corroborate
                                    'rgba(33, 150, 243, 0.4)',  // Faded Contradict
                                    'rgba(227, 242, 253, 0.4)', // Faded Contextual
                                    'rgba(21, 101, 192, 0.4)'   // Faded Failure
                                  ][i]
                        );
                    } else {
                        // Restore colors
                        dataset.backgroundColor = [
                            '#90CAF9',
                            '#2196F3',
                            '#E3F2FD',
                            '#1565C0'
                        ];
                    }
                }
            },
            plugins: [centerTextPlugin]
        });
    }

    initDensityChart(data) {
        const ctx = document.getElementById('density-chart').getContext('2d');
        
        // Mock data for documents
        const labels = data.documents ? data.documents.map(d => d.filename.substring(0, 15) + '...') : 
                      ['Macro_Report_2024.pdf', 'Delhivery_Q3.pdf', 'Q2_Earnings_Call.pdf', 'Industry_Analysis.pdf', 'Competitor_Data.pdf'];
        const values = [245, 180, 120, 310, 160];

        this.densityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Facts',
                    data: values,
                    backgroundColor: 'rgba(33, 150, 243, 0.8)', // primary color
                    hoverBackgroundColor: '#2196F3',
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                ...this.commonOptions,
                scales: this.scaleOptions
            }
        });
    }

    updateCharts(data) {
        // In a real app, this would update chart data and call chart.update()
        this.renderKPIs(data);
    }
}
