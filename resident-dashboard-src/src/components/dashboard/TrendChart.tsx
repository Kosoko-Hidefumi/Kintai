import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { ResidentRecord } from "../../types";
import { getDeptColor } from "../../utils/colors";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TrendChartProps {
  data: ResidentRecord[];
}

export function TrendChart({ data }: TrendChartProps) {
  const yearSet = new Set<string>();
  const deptCounts: Record<string, Record<string, number>> = {};

  data.forEach((r) => {
    if (!r.年度) return;
    yearSet.add(r.年度);
    const dept = r.専門科正規化 || "不明";
    if (!deptCounts[dept]) deptCounts[dept] = {};
    deptCounts[dept][r.年度] = (deptCounts[dept][r.年度] || 0) + 1;
  });

  const years = Array.from(yearSet).sort();

  const deptTotals: { name: string; total: number }[] = Object.entries(
    deptCounts
  ).map(([name, counts]) => ({
    name,
    total: Object.values(counts).reduce((sum, c) => sum + c, 0),
  }));

  const topDepts = deptTotals
    .sort((a, b) => b.total - a.total)
    .slice(0, 6)
    .map((d) => d.name);

  const datasets = topDepts.map((dept) => ({
    label: dept,
    data: years.map((y) => deptCounts[dept]?.[y] || 0),
    borderColor: getDeptColor(dept),
    backgroundColor: getDeptColor(dept),
    tension: 0.4,
    pointRadius: 4,
    pointHoverRadius: 6,
  }));

  const chartData = {
    labels: years.map((y) => `${y}年度`),
    datasets,
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index" as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h3 className="font-semibold text-gray-700 mb-4">専門科別 年度推移</h3>
      <div style={{ height: 300 }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}
