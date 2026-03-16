import { useState } from "react";
import { ResidentRecord, SortMode, ViewMode } from "../../types";
import { useDataFilter } from "../../hooks/useDataFilter";
import { ControlBar } from "../layout/ControlBar";
import { YearTabs } from "./YearTabs";
import { GradeSection } from "./GradeSection";
import { PersonTable } from "./PersonTable";
import { PersonModal } from "./PersonModal";

function getLatestYear(data: ResidentRecord[]): string {
  const yearSet = new Set<string>();
  data.forEach((r) => {
    if (r.年度) yearSet.add(r.年度);
  });
  const years = Array.from(yearSet).sort();
  return years.length > 0 ? years[years.length - 1] : "all";
}

interface MasterTabProps {
  data: ResidentRecord[];
}

export function MasterTab({ data }: MasterTabProps) {
  const [searchText, setSearchText] = useState("");
  const [selectedYear, setSelectedYear] = useState(() => getLatestYear(data));
  const [selectedGrade, setSelectedGrade] = useState("all");
  const [selectedGender, setSelectedGender] = useState("all");
  const [selectedDept, setSelectedDept] = useState("all");
  const [sortMode, setSortMode] = useState<SortMode>("grade");
  const [viewMode, setViewMode] = useState<ViewMode>("card");
  const [selectedPerson, setSelectedPerson] = useState<ResidentRecord | null>(
    null
  );

  const { sortedByGrade, years, grades, depts, totalCount } = useDataFilter(
    data,
    {
      searchText,
      selectedYear,
      selectedGrade,
      selectedGender,
      selectedDept,
      sortMode,
    }
  );

  const gradeOrder = ["PGY1", "PGY2", "PGY3", "PGY4", "PGY5", "PGY6", "受入", "後期", "その他"];
  const showYear = selectedYear === "all";

  return (
    <div className="bg-bg-base min-h-screen">
      <ControlBar
        searchText={searchText}
        onSearchChange={setSearchText}
        selectedGrade={selectedGrade}
        onGradeChange={setSelectedGrade}
        selectedGender={selectedGender}
        onGenderChange={setSelectedGender}
        selectedDept={selectedDept}
        onDeptChange={setSelectedDept}
        sortMode={sortMode}
        onSortModeChange={setSortMode}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        grades={grades}
        depts={depts}
        totalCount={totalCount}
      />

      <YearTabs
        years={years}
        selectedYear={selectedYear}
        onYearChange={setSelectedYear}
      />

      <main className="max-w-7xl mx-auto px-4 py-6">
        {viewMode === "card" ? (
          gradeOrder.map((grade) => {
            const persons = sortedByGrade[grade];
            if (!persons || persons.length === 0) return null;
            return (
              <GradeSection
                key={grade}
                grade={grade}
                persons={persons}
                sortMode={sortMode}
                onPersonClick={setSelectedPerson}
                showYear={showYear}
              />
            );
          })
        ) : (
          gradeOrder.map((grade) => {
            const persons = sortedByGrade[grade];
            if (!persons || persons.length === 0) return null;
            return (
              <PersonTable
                key={grade}
                data={persons}
                grade={grade}
                onPersonClick={setSelectedPerson}
                showYear={showYear}
              />
            );
          })
        )}

        {totalCount === 0 && (
          <div className="text-center py-16">
            <p className="text-gray-500 text-lg">
              該当する研修医が見つかりません
            </p>
          </div>
        )}
      </main>

      {selectedPerson && (
        <PersonModal
          person={selectedPerson}
          onClose={() => setSelectedPerson(null)}
        />
      )}
    </div>
  );
}
