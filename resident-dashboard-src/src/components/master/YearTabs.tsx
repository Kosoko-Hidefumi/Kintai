interface YearTabsProps {
  years: string[];
  selectedYear: string;
  onYearChange: (year: string) => void;
}

export function YearTabs({ years, selectedYear, onYearChange }: YearTabsProps) {
  return (
    <div className="bg-gray-50 border-b">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onYearChange("all")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedYear === "all"
                ? "bg-primary text-white"
                : "bg-white text-gray-700 border hover:bg-gray-100"
            }`}
          >
            全年度
          </button>
          {years.map((year) => (
            <button
              key={year}
              onClick={() => onYearChange(year)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedYear === year
                  ? "bg-primary-light text-white"
                  : "bg-white text-gray-700 border hover:bg-gray-100"
              }`}
            >
              {year}年度
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
