import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TooltipItem,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { getDeptColor, hexToRgba } from "../../utils/colors";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface DeptStat {
  name: string;
  count: number;
}

interface BarChartProps {
  deptStats: DeptStat[];
}

export function BarChart({ deptStats }: BarChartProps) {
  const sortedStats = [...deptStats].sort((a, b) => b.count - a.count);

  const data = {
    labels: sortedStats.map((s) => s.name),
    datasets: [
      {
        label: "人数",
        data: sortedStats.map((s) => s.count),
        backgroundColor: sortedStats.map((s) =>
          hexToRgba(getDeptColor(s.name), 0.8)
        ),
        borderColor: sortedStats.map((s) => getDeptColor(s.name)),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (ctx: TooltipItem<"bar">) => `${ctx.parsed.x ?? 0} 名`,
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h3 className="font-semibold text-gray-700 mb-4">専門科別 人数</h3>
      <div style={{ height: Math.max(300, sortedStats.length * 30) }}>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}
