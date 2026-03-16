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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface GenderChartProps {
  data: ResidentRecord[];
}

export function GenderChart({ data }: GenderChartProps) {
  const deptGenderCounts: Record<string, { male: number; female: number }> = {};

  data.forEach((r) => {
    const dept = r.専門科正規化 || "不明";
    if (!deptGenderCounts[dept]) {
      deptGenderCounts[dept] = { male: 0, female: 0 };
    }
    if (r.性別 === "男") {
      deptGenderCounts[dept].male += 1;
    } else if (r.性別 === "女") {
      deptGenderCounts[dept].female += 1;
    }
  });

  const sortedDepts = Object.entries(deptGenderCounts)
    .map(([name, counts]) => ({
      name,
      total: counts.male + counts.female,
      male: counts.male,
      female: counts.female,
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 10);

  const chartData = {
    labels: sortedDepts.map((d) => d.name),
    datasets: [
      {
        label: "男性",
        data: sortedDepts.map((d) => d.male),
        backgroundColor: "rgba(59, 130, 246, 0.8)",
        borderColor: "#3B82F6",
        borderWidth: 1,
      },
      {
        label: "女性",
        data: sortedDepts.map((d) => d.female),
        backgroundColor: "rgba(236, 72, 153, 0.8)",
        borderColor: "#EC4899",
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
        position: "top" as const,
      },
    },
    scales: {
      x: {
        stacked: true,
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
      y: {
        stacked: true,
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h3 className="font-semibold text-gray-700 mb-4">専門科別 男女比</h3>
      <div style={{ height: 300 }}>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
}
