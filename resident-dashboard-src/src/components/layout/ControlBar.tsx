import { Search, Grid3X3, List } from "lucide-react";
import { SortMode, ViewMode } from "../../types";

interface ControlBarProps {
  searchText: string;
  onSearchChange: (text: string) => void;
  selectedGrade: string;
  onGradeChange: (grade: string) => void;
  selectedGender: string;
  onGenderChange: (gender: string) => void;
  selectedDept: string;
  onDeptChange: (dept: string) => void;
  sortMode: SortMode;
  onSortModeChange: (mode: SortMode) => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  grades: string[];
  depts: string[];
  totalCount: number;
}

export function ControlBar({
  searchText,
  onSearchChange,
  selectedGrade,
  onGradeChange,
  selectedGender,
  onGenderChange,
  selectedDept,
  onDeptChange,
  sortMode,
  onSortModeChange,
  viewMode,
  onViewModeChange,
  grades,
  depts,
  totalCount,
}: ControlBarProps) {
  return (
    <div className="sticky top-14 z-40 bg-white border-b shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px] max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchText}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="名前・ふりがな・大学・専門科・本籍で検索"
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent focus:border-transparent outline-none"
            />
          </div>

          <select
            value={selectedGrade}
            onChange={(e) => onGradeChange(e.target.value)}
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
            onChange={(e) => onGenderChange(e.target.value)}
            className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-accent outline-none"
          >
            <option value="all">すべての性別</option>
            <option value="男">男性</option>
            <option value="女">女性</option>
          </select>

          <select
            value={selectedDept}
            onChange={(e) => onDeptChange(e.target.value)}
            className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-accent outline-none"
          >
            <option value="all">すべての専門科</option>
            {depts.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>

          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => onSortModeChange("grade")}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                sortMode === "grade"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-200"
              }`}
            >
              🎓 学年別
            </button>
            <button
              onClick={() => onSortModeChange("kana")}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                sortMode === "kana"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-200"
              }`}
            >
              あ 五十音
            </button>
            <button
              onClick={() => onSortModeChange("dept")}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                sortMode === "dept"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-200"
              }`}
            >
              🏥 専門科別
            </button>
          </div>

          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => onViewModeChange("card")}
              className={`p-2 rounded transition-colors ${
                viewMode === "card"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-200"
              }`}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => onViewModeChange("table")}
              className={`p-2 rounded transition-colors ${
                viewMode === "table"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-200"
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          <span className="ml-auto text-gray-600 font-medium">
            {totalCount} 件
          </span>
        </div>
      </div>
    </div>
  );
}
