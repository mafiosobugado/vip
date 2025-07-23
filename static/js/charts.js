// static/js/charts.js

// Pega as cores das variáveis CSS
function getRiskColors() {
    const root = getComputedStyle(document.documentElement);
    return [
        root.getPropertyValue('--risk-nenhum').trim(),
        root.getPropertyValue('--risk-baixo').trim(), 
        root.getPropertyValue('--risk-medio').trim(),
        root.getPropertyValue('--risk-alto').trim(),
        root.getPropertyValue('--risk-critico').trim()
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
    if (window.dashboardData && window.dashboardData.riskDistribution && window.dashboardData.itemsTrend) {
        createRiskLevelChart(window.dashboardData.riskDistribution);
        createItemsTrendChart(window.dashboardData.itemsTrend);
    } else {
        console.warn("Dados do dashboard não encontrados. Gráficos não serão renderizados.");
    }
});

function createRiskLevelChart(data) {
    const ctx = document.getElementById('riskLevelChart');
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Mapear cores específicas para cada nível de risco
    const colorMap = {
        'NENHUM': getComputedStyle(document.documentElement).getPropertyValue('--risk-nenhum').trim(),
        'BAIXO': getComputedStyle(document.documentElement).getPropertyValue('--risk-baixo').trim(),
        'MÉDIO': getComputedStyle(document.documentElement).getPropertyValue('--risk-medio').trim(),
        'ALTO': getComputedStyle(document.documentElement).getPropertyValue('--risk-alto').trim(),
        'CRÍTICO': getComputedStyle(document.documentElement).getPropertyValue('--risk-critico').trim()
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