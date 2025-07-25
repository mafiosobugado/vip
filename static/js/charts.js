// static/js/charts.js

// Pega as cores das variáveis CSS para severidade
function getSeverityColors() {
    const root = getComputedStyle(document.documentElement);
    return [
        root.getPropertyValue('--risk-baixo').trim(),   // BAIXA
        root.getPropertyValue('--risk-medio').trim(),   // MEDIA
        root.getPropertyValue('--risk-alto').trim(),    // ALTA
        root.getPropertyValue('--risk-critico').trim()  // CRITICA
    ];
}

function getPrimaryColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
}

function getDarkBg3() {
    return getComputedStyle(document.documentElement).getPropertyValue('--dark-bg-3').trim();
}

function getTextColorLight() {
    return getComputedStyle(document.documentElement).getPropertyValue('--text-color-light').trim();
}

function getTextColorLight2() {
    return getComputedStyle(document.documentElement).getPropertyValue('--text-color-light-2').trim();
}

document.addEventListener('DOMContentLoaded', function() {
    // Verificar se os dados existem
    if (window.dashboardData) {
        console.log('Dashboard data:', window.dashboardData);
        
        if (window.dashboardData.severityDistribution) {
            createSeverityDistributionChart(window.dashboardData.severityDistribution);
        } else {
            console.warn("Dados de distribuição de severidade não encontrados.");
        }
        
        if (window.dashboardData.itemsTrend) {
            createItemsTrendChart(window.dashboardData.itemsTrend);
        } else {
            console.warn("Dados de tendência de itens não encontrados.");
        }
    } else {
        console.warn("Dados do dashboard não encontrados. Gráficos não serão renderizados.");
    }
});

function createSeverityDistributionChart(data) {
    const ctx = document.getElementById('severityDistributionChart');
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Mapear cores específicas para cada nível de severidade
    const colorMap = {
        'BAIXA': getComputedStyle(document.documentElement).getPropertyValue('--risk-baixo').trim(),
        'MEDIA': getComputedStyle(document.documentElement).getPropertyValue('--risk-medio').trim(),
        'ALTA': getComputedStyle(document.documentElement).getPropertyValue('--risk-alto').trim(),
        'CRITICA': getComputedStyle(document.documentElement).getPropertyValue('--risk-critico').trim()
    };
    
    const backgroundColors = labels.map(label => colorMap[label.toUpperCase()] || '#6c757d');

    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
                borderColor: getDarkBg3(),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getTextColorLight(),
                        padding: 20,
                        usePointStyle: true
                    }
                },
                title: {
                    display: false,
                }
            }
        }
    });
}

function createItemsTrendChart(data) {
    const ctx = document.getElementById('itemsTrendChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Itens Identificados',
                data: data.counts,
                borderColor: getPrimaryColor(),
                backgroundColor: 'rgba(162, 89, 255, 0.15)',
                tension: 0.3,
                fill: true,
                pointBackgroundColor: getPrimaryColor(),
                pointBorderColor: getPrimaryColor(),
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderColor: getPrimaryColor()
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: getTextColorLight2()
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: getTextColorLight2(),
                        precision: 0
                    }
                }
            }
        }
    });
}