import { getDeptColor } from "../../utils/colors";

interface DeptStat {
  name: string;
  count: number;
  percentage: number;
}

interface RankTableProps {
  deptStats: DeptStat[];
  totalCount: number;
}

export function RankTable({ deptStats, totalCount }: RankTableProps) {
  const sortedStats = [...deptStats].sort((a, b) => b.count - a.count);
  const maxCount = sortedStats[0]?.count || 1;

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-700">専門科ランキング</h3>
        <span className="text-sm text-gray-500">
          全{deptStats.length}専門科 / 合計{totalCount}名
        </span>
      </div>

      <div className="space-y-2">
        {sortedStats.map((stat, idx) => (
          <div
            key={stat.name}
            className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0"
          >
            <span className="w-6 text-sm font-medium text-gray-500 text-right">
              {idx + 1}
            </span>
            <span
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: getDeptColor(stat.name) }}
            />
            <span className="flex-1 text-gray-800 truncate">{stat.name}</span>
            <div className="w-32 bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${(stat.count / maxCount) * 100}%`,
                  backgroundColor: getDeptColor(stat.name),
                }}
              />
            </div>
            <span className="w-12 text-right text-gray-600 font-medium">
              {stat.count}名
            </span>
            <span className="w-16 text-right text-gray-500 text-sm">
              {stat.percentage.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
