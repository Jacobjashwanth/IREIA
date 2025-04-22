import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title
} from 'chart.js';

ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend,
  Title
);

// Helper function (can be shared in a utils file later)
const calculateMonthlyPI = (principal, annualRate, years) => {
  if (principal <= 0) return 0;
  const monthlyRate = annualRate / 12 / 100;
  const numberOfPayments = years * 12;
  if (monthlyRate === 0) return principal / numberOfPayments;
  return (
    principal *
    (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) /
    (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
  );
};

const OwnershipCostChart = ({ predictedSalePrice }) => {
  // --- Assumptions (should ideally match ComparisonChart or be centralized) ---
  const interestRateAnnual = 7.0; 
  const loanTermYears = 30;
  const downPaymentPercentage = 20; 
  const propertyTaxRateAnnual = 1.2; 
  const homeInsuranceRateAnnual = 0.5;
  // ---

  // Calculate costs
  const downPayment = predictedSalePrice * (downPaymentPercentage / 100);
  const loanAmount = predictedSalePrice - downPayment;
  const monthlyPI = calculateMonthlyPI(loanAmount, interestRateAnnual, loanTermYears);
  const monthlyTaxes = (predictedSalePrice * (propertyTaxRateAnnual / 100)) / 12;
  const monthlyInsurance = (predictedSalePrice * (homeInsuranceRateAnnual / 100)) / 12;

  const data = {
    labels: [
      `Principal & Interest ($${monthlyPI.toFixed(0)})`,
      `Property Taxes ($${monthlyTaxes.toFixed(0)})`,
      `Home Insurance ($${monthlyInsurance.toFixed(0)})`,
    ],
    datasets: [
      {
        label: 'Estimated Monthly Ownership Cost Breakdown',
        data: [monthlyPI, monthlyTaxes, monthlyInsurance],
        backgroundColor: [
          'rgba(0, 123, 255, 0.7)', // Blue
          'rgba(255, 193, 7, 0.7)',  // Yellow
          'rgba(220, 53, 69, 0.7)',  // Red
        ],
        borderColor: [
          'rgba(0, 123, 255, 1)',
          'rgba(255, 193, 7, 1)',
          'rgba(220, 53, 69, 1)',
        ],
        borderWidth: 1,
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
          padding: 15, // Add padding to legend items
          font: { size: 11 }
        }
      },
      title: {
        display: true,
        text: 'Est. Ownership Cost Breakdown',
        font: { size: 14 }
      },
       tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.label || ''; // Use the generated label
            // Extract value from the label if needed or use raw value
            let value = context.parsed;
            if (value !== null) {
               label += ': ' + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
            }
            return label;
          }
        }
      }
    },
  };

  // Ensure valid data for chart rendering
  if (isNaN(monthlyPI) || isNaN(monthlyTaxes) || isNaN(monthlyInsurance) || predictedSalePrice <= 0) {
    return <div className="chart-placeholder">Cannot generate ownership cost breakdown.</div>;
  }

  return (
    <div className="small-chart-container">
      <Doughnut data={data} options={options} />
    </div>
  );
};

export default OwnershipCostChart; 