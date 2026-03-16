import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  TooltipItem,
  ChartOptions,
} from "chart.js";
import { Doughnut } from "react-chartjs-2";
import { getDeptColor, hexToRgba } from "../../utils/colors";

ChartJS.register(ArcElement, Tooltip, Legend);

interface DeptStat {
  name: string;
  count: number;
  percentage: number;
}

interface DoughnutChartProps {
  deptStats: DeptStat[];
}

export function DoughnutChart({ deptStats }: DoughnutChartProps) {
  const sortedStats = [...deptStats].sort((a, b) => b.count - a.count);
  const total = sortedStats.reduce((sum, s) => sum + s.count, 0);

  const data = {
    labels: sortedStats.map((s) => s.name),
    datasets: [
      {
        data: sortedStats.map((s) => s.count),
        backgroundColor: sortedStats.map((s) =>
          hexToRgba(getDeptColor(s.name), 0.8)
        ),
        borderColor: sortedStats.map((s) => getDeptColor(s.name)),
        borderWidth: 2,
      },
    ],
  };

  const options: ChartOptions<"doughnut"> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "60%",
    plugins: {
      legend: {
        position: "right" as const,
        labels: {
          boxWidth: 12,
          padding: 8,
          font: {
            size: 11,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (ctx: TooltipItem<"doughnut">) => {
            const percentage = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : "0";
            return `${ctx.label}: ${ctx.parsed}名 (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h3 className="font-semibold text-gray-700 mb-4">専門科別 構成比</h3>
      <div style={{ height: 300 }}>
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
}
