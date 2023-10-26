document.addEventListener("DOMContentLoaded", function () {
  const chartCanvas = document.getElementById("chartCanvas");
  const pieChartButton = document.getElementById("pieChartButton");
  const barChartButton = document.getElementById("barChartButton");
  const last6MonthsButton = document.getElementById("last6MonthsButton");
  const last3MonthsButton = document.getElementById("last3MonthsButton");
  const lastMonthButton = document.getElementById("lastMonthButton");

  let currentChart = null; // To keep track of the current chart instance

  // Function to render the pie chart
  const renderPieChart = (data, labels) => {
    if (currentChart) {
      currentChart.destroy(); // Destroy the current chart instance if it exists
    }

    currentChart = new Chart(chartCanvas, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Expenses per category",
            data: data,
            backgroundColor: [
              "rgba(255, 99, 132, 0.2)",
              "rgba(54, 162, 235, 0.2)",
              "rgba(255, 206, 86, 0.2)",
              "rgba(75, 192, 192, 0.2)",
              "rgba(153, 102, 255, 0.2)",
              "rgba(255, 159, 64, 0.2)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
              "rgba(255, 159, 64, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // Allow canvas to be resized
        title: {
          display: true,
          text: "Expenses per category (Pie Chart)",
        },
      },
    });
  };

  // Function to render the bar chart
  const renderBarChart = (data, labels) => {
    if (currentChart) {
      currentChart.destroy(); // Destroy the current chart instance if it exists
    }

    currentChart = new Chart(chartCanvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Last 6 months expenses",
            data: data,
            backgroundColor: [
              "rgba(255, 99, 132, 0.2)",
              "rgba(54, 162, 235, 0.2)",
              "rgba(255, 206, 86, 0.2)",
              "rgba(75, 192, 192, 0.2)",
              "rgba(153, 102, 255, 0.2)",
              "rgba(255, 159, 64, 0.2)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
              "rgba(255, 159, 64, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // Allow canvas to be resized
        title: {
          display: true,
          text: "Expenses per category (Bar Chart)",
        },
      },
    });
  };

  const getChartData = (timeframe) => {
    console.log("fetching");
    fetch(`/expense_category_summary?timeframe=${timeframe}`)
      .then((res) => res.json())
      .then((results) => {
        console.log("results", results);
        const category_data = results.expense_category_data;
        const [labels, data] = [
          Object.keys(category_data),
          Object.values(category_data),
        ];
  
        // Add event listeners to the buttons to switch between chart types
        pieChartButton.addEventListener("click", () => {
          renderPieChart(data, labels);
        });
  
        barChartButton.addEventListener("click", () => {
          renderBarChart(data, labels, timeframe); // Pass the timeframe to the bar chart renderer
        });
      });
  };
  
  // Call the function to fetch and render the data with the default timeframe (last 6 months)
  getChartData("last6months");
  
  last6MonthsButton.addEventListener("click", () => {
    getChartData("last6months");
  });
  
  last3MonthsButton.addEventListener("click", () => {
    getChartData("last3months");
  });
  
  lastMonthButton.addEventListener("click", () => {
    getChartData("lastmonth");
  });
  
});
