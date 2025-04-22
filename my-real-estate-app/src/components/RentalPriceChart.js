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

const RentalPriceChart = ({ predictedRent }) => {
  // Generate monthly data points for rental trends
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const currentMonth = new Date().getMonth();
  
  // Create labels for the last 12 months
  const labels = [];
  for (let i = 11; i >= 0; i--) {
    const monthIndex = (currentMonth - i + 12) % 12;
    labels.push(months[monthIndex]);
  }

  // Generate rental data with seasonal variations
  const seasonalFactors = {
    'Dec': 0.95, 'Jan': 0.93, 'Feb': 0.94, // Winter: Lower demand
    'Mar': 1.02, 'Apr': 1.05, 'May': 1.08, // Spring: Higher demand
    'Jun': 1.10, 'Jul': 1.08, 'Aug': 1.05, // Summer: Peak demand
    'Sep': 1.00, 'Oct': 0.98, 'Nov': 0.96  // Fall: Moderate demand
  };

  const rentalData = labels.map(month => {
    const seasonalFactor = seasonalFactors[month];
    return predictedRent * seasonalFactor;
  });

  const data = {
    labels,
    datasets: [
      {
        label: 'Monthly Rental Price Trend',
        data: rentalData,
        borderColor: 'rgb(40, 167, 69)', // Green color for rent
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        tension: 0.3,
        fill: true
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
        text: 'Seasonal Rental Price Trends',
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
              label += new Intl.NumberFormat('en-US', { 
                style: 'currency', 
                currency: 'USD',
                maximumFractionDigits: 0 
              }).format(context.parsed.y);
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Monthly Rent ($)',
        },
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      },
      x: {
        title: {
          display: true,
          text: 'Month'
        }
      }
    },
  };
  
  if (!predictedRent || predictedRent <= 0) {
    return <div className="chart-placeholder">Cannot generate rental price trends.</div>;
  }

  return (
    <div className="small-chart-container">
      <Line options={options} data={data} />
    </div>
  );
};

export default RentalPriceChart; 