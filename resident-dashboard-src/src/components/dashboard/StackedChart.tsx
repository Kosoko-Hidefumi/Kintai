import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { ResidentRecord } from "../../types";
import { getDeptColor, hexToRgba } from "../../utils/colors";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface StackedChartProps {
  data: ResidentRecord[];
}

export function StackedChart({ data }: StackedChartProps) {
  const gradeOrder = ["PGY1", "PGY2", "PGY3", "PGY4", "PGY5", "PGY6"];
  const gradeDeptCounts: Record<string, Record<string, number>> = {};
  const deptTotals: Record<string, number> = {};

  gradeOrder.forEach((g) => {
    gradeDeptCounts[g] = {};
  });

  data.forEach((r) => {
    const grade = r.学年;
    const dept = r.専門科正規化 || "不明";
    if (!gradeOrder.includes(grade)) return;
    gradeDeptCounts[grade][dept] = (gradeDeptCounts[grade][dept] || 0) + 1;
    deptTotals[dept] = (deptTotals[dept] || 0) + 1;
  });

  const topDepts = Object.entries(deptTotals)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map((d) => d[0]);

  const datasets = topDepts.map((dept) => ({
    label: dept,
    data: gradeOrder.map((g) => gradeDeptCounts[g][dept] || 0),
    backgroundColor: hexToRgba(getDeptColor(dept), 0.8),
    borderColor: getDeptColor(dept),
    borderWidth: 1,
  }));

  const chartData = {
    labels: gradeOrder,
    datasets,
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h3 className="font-semibold text-gray-700 mb-4">学年別 × 専門科 構成</h3>
      <div style={{ height: 300 }}>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
}
