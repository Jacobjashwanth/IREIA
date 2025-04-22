import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const PriceHistoryChart = ({ predictedSalePrice }) => {
  // --- Assumptions ---
  const yearsToShow = 5;
  const annualAppreciationRate = 0.05; // 5% annual appreciation
  // ---

  // Generate historical data (simulated)
  const currentYear = new Date().getFullYear();
  const labels = [];
  const priceData = [];

  if (predictedSalePrice > 0) {
    let lastPrice = predictedSalePrice;
    // Add current year prediction
    labels.push(currentYear);
    priceData.push(lastPrice);

    // Calculate previous years' hypothetical prices
    for (let i = 1; i <= yearsToShow; i++) {
      const year = currentYear - i;
      // Price in year Y = Price in year Y+1 / (1 + appreciation rate)
      const historicalPrice = lastPrice / (1 + annualAppreciationRate);
      labels.push(year);
      priceData.push(historicalPrice);
      lastPrice = historicalPrice; // Update for the next iteration
    }
    // Reverse arrays to show oldest year first
    labels.reverse();
    priceData.reverse();
  }

  const data = {
    labels,
    datasets: [
      {
        label: 'Hypothetical Price Trend (Est.)',
        data: priceData,
        borderColor: 'rgb(75, 192, 192)', // Teal color
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1 // Adds slight curve to the line
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: { size: 11 }
        }
      },
      title: {
        display: true,
        text: `Hypothetical ${yearsToShow}-Year Price Trend`,
        font: { size: 14 }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
             let label = context.dataset.label || '';
             if (label) {
               label += ': ';
             }
             if (context.parsed.y !== null) {
               label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(context.parsed.y);
             }
             return label;
           }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false, // Don't necessarily start Y axis at 0 for price trends
        title: {
          display: true,
          text: 'Estimated Price ($)',
        },
         ticks: {
           callback: function(value) {
             return '$' + (value / 1000).toFixed(0) + 'k'; // Format as $XXXk
           }
        }
      },
      x: {
        title: {
          display: true,
          text: 'Year'
        }
      }
    },
  };
  
   // Check if data is valid before rendering
   if (!priceData || priceData.length === 0) {
    return <div className="chart-placeholder">Cannot generate price history trend.</div>;
  }

  return (
    <div className="small-chart-container">
      <Line options={options} data={data} />
    </div>
  );
};

export default PriceHistoryChart; 