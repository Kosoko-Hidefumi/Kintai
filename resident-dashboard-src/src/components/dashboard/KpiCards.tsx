import { Users, Building2, Trophy } from "lucide-react";
import { getDeptColor } from "../../utils/colors";

interface DeptStat {
  name: string;
  count: number;
  percentage: number;
}

interface KpiCardsProps {
  totalCount: number;
  deptCount: number;
  topDepts: DeptStat[];
}

export function KpiCards({ totalCount, deptCount, topDepts }: KpiCardsProps) {
  const medals = ["🥇", "🥈", "🥉"];

  return (
    <div
      className="grid gap-4 mb-6"
      style={{ gridTemplateColumns: "repeat(auto-fill, minmax(145px, 1fr))" }}
    >
      <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-primary">
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
          <Users className="w-4 h-4" />
          総人数
        </div>
        <p className="text-2xl font-bold text-gray-800">{totalCount}名</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-accent">
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
          <Building2 className="w-4 h-4" />
          専門科数
        </div>
        <p className="text-2xl font-bold text-gray-800">{deptCount}科</p>
      </div>

      {topDepts.slice(0, 3).map((dept, idx) => (
        <div
          key={dept.name}
          className="bg-white rounded-lg shadow-sm p-4"
          style={{ borderLeftWidth: "4px", borderLeftColor: getDeptColor(dept.name) }}
        >
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
            <Trophy className="w-4 h-4" />
            {medals[idx]} {idx + 1}位
          </div>
          <p className="text-lg font-bold text-gray-800 truncate">{dept.name}</p>
          <p className="text-sm text-gray-500">
            {dept.count}名 ({dept.percentage.toFixed(1)}%)
          </p>
        </div>
      ))}
    </div>
  );
}
