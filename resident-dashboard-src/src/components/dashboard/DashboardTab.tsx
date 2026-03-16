import { useState, useMemo } from "react";
import { ResidentRecord } from "../../types";
import { KpiCards } from "./KpiCards";
import { BarChart } from "./BarChart";
import { DoughnutChart } from "./DoughnutChart";
import { TrendChart } from "./TrendChart";
import { StackedChart } from "./StackedChart";
import { GenderChart } from "./GenderChart";
import { RankTable } from "./RankTable";

function getLatestYear(data: ResidentRecord[]): string {
  const yearSet = new Set<string>();
  data.forEach((r) => {
    if (r.年度) yearSet.add(r.年度);
  });
  const years = Array.from(yearSet).sort();
  return years.length > 0 ? years[years.length - 1] : "all";
}

interface DashboardTabProps {
  data: ResidentRecord[];
}

export function DashboardTab({ data }: DashboardTabProps) {
  const [selectedYear, setSelectedYear] = useState(() => getLatestYear(data));
  const [selectedGrade, setSelectedGrade] = useState("all");
  const [selectedGender, setSelectedGender] = useState("all");

  const years = useMemo(() => {
    const yearSet = new Set<string>();
    data.forEach((r) => {
      if (r.年度) yearSet.add(r.年度);
    });
    return Array.from(yearSet).sort();
  }, [data]);

  const grades = useMemo(() => {
    const gradeSet = new Set<string>();
    data.forEach((r) => {
      if (r.学年) gradeSet.add(r.学年);
    });
    const gradeOrder = ["PGY1", "PGY2", "PGY3", "PGY4", "PGY5", "PGY6"];
    return gradeOrder.filter((g) => gradeSet.has(g));
  }, [data]);

  const filteredData = useMemo(() => {
    let result = [...data];

    if (selectedYear !== "all") {
      result = result.filter((r) => r.年度 === selectedYear);
    }
    if (selectedGrade !== "all") {
      result = result.filter((r) => r.学年 === selectedGrade);
    }
    if (selectedGender !== "all") {
      result = result.filter((r) => r.性別 === selectedGender);
    }

    return result;
  }, [data, selectedYear, selectedGrade, selectedGender]);

  const deptStats = useMemo(() => {
    const deptCounts: Record<string, number> = {};
    filteredData.forEach((r) => {
      const dept = r.専門科正規化 || "不明";
      deptCounts[dept] = (deptCounts[dept] || 0) + 1;
    });

    const total = filteredData.length;
    return Object.entries(deptCounts).map(([name, count]) => ({
      name,
      count,
      percentage: total > 0 ? (count / total) * 100 : 0,
    }));
  }, [filteredData]);

  return (
    <div className="bg-bg-base min-h-screen">
      <div className="sticky top-14 z-40 bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-accent outline-none"
            >
              <option value="all">全年度</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}年度
                </option>
              ))}
            </select>

            <select
              value={selectedGrade}
              onChange={(e) => setSelectedGrade(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-accent outline-none"
            >
              <option value="all">すべての学年</option>
              {grades.map((grade) => (
                <option key={grade} value={grade}>
                  {grade}
                </option>
              ))}
            </select>

            <select
              value={selectedGender}
              onChange={(e) => setSelectedGender(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-accent outline-none"
            >
              <option value="all">すべての性別</option>
              <option value="男">男性</option>
              <option value="女">女性</option>
            </select>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <KpiCards
          totalCount={filteredData.length}
          deptCount={deptStats.length}
          topDepts={[...deptStats].sort((a, b) => b.count - a.count)}
        />

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <BarChart deptStats={deptStats} />
          <DoughnutChart deptStats={deptStats} />
        </div>

        <div className="mb-6">
          <TrendChart data={data} />
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <StackedChart data={filteredData} />
          <GenderChart data={filteredData} />
        </div>

        <RankTable deptStats={deptStats} totalCount={filteredData.length} />
      </main>
    </div>
  );
}
