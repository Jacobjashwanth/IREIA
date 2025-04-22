import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Helper function to calculate monthly mortgage payment (Principal & Interest)
const calculateMonthlyPI = (principal, annualRate, years) => {
  if (principal <= 0) return 0;
  const monthlyRate = annualRate / 12 / 100;
  const numberOfPayments = years * 12;
  if (monthlyRate === 0) return principal / numberOfPayments; // Handle 0% interest case
  return (
    principal *
    (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) /
    (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
  );
};

const ComparisonChart = ({ predictedRent, predictedSalePrice }) => {
  // --- Calculation Assumptions ---
  const interestRateAnnual = 7.0; // Example annual interest rate %
  const loanTermYears = 30;
  const downPaymentPercentage = 20; // %
  const propertyTaxRateAnnual = 1.2; // Example annual property tax rate %
  const homeInsuranceRateAnnual = 0.5; // Example annual home insurance rate %
  // --- End Assumptions ---

  // Calculate estimated ownership costs
  const downPayment = predictedSalePrice * (downPaymentPercentage / 100);
  const loanAmount = predictedSalePrice - downPayment;
  
  const monthlyPI = calculateMonthlyPI(loanAmount, interestRateAnnual, loanTermYears);
  const monthlyTaxes = (predictedSalePrice * (propertyTaxRateAnnual / 100)) / 12;
  const monthlyInsurance = (predictedSalePrice * (homeInsuranceRateAnnual / 100)) / 12;
  
  const estimatedMonthlyOwnershipCost = monthlyPI + monthlyTaxes + monthlyInsurance;

  // Chart Data
  const data = {
    labels: ['Monthly Cost Comparison'],
    datasets: [
      {
        label: 'Predicted Monthly Rent',
        data: [predictedRent],
        backgroundColor: 'rgba(40, 167, 69, 0.6)', // Green color for rent
        borderColor: 'rgba(40, 167, 69, 1)',
        borderWidth: 1,
      },
      {
        label: 'Estimated Monthly Ownership Cost',
        data: [estimatedMonthlyOwnershipCost],
        backgroundColor: 'rgba(0, 123, 255, 0.6)', // Blue color for ownership
        borderColor: 'rgba(0, 123, 255, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Chart Options
  const options = {
    responsive: true,
    maintainAspectRatio: false, // Allow chart height to be controlled by container
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Rent vs. Estimated Buy Monthly Cost',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Monthly Cost ($)',
        },
        ticks: {
           callback: function(value) {
             return '$' + value.toLocaleString();
           }
        }
      },
    },
  };

  return (
    <div className="comparison-chart-container">
      <Bar options={options} data={data} />
    </div>
  );
};

export default ComparisonChart; 