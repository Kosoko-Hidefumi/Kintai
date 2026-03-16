import { ResidentRecord, SortMode } from "../../types";
import { PersonCard } from "./PersonCard";
import { GRADE_COLORS, getDeptColor } from "../../utils/colors";

interface GradeSectionProps {
  grade: string;
  persons: ResidentRecord[];
  sortMode: SortMode;
  onPersonClick: (person: ResidentRecord) => void;
  showYear?: boolean;
}

export function GradeSection({
  grade,
  persons,
  sortMode,
  onPersonClick,
  showYear,
}: GradeSectionProps) {
  const gradeColor = GRADE_COLORS[grade] || "#64748B";

  if (sortMode === "dept") {
    const deptGroups: Record<string, ResidentRecord[]> = {};
    persons.forEach((p) => {
      const dept = p.専門科正規化 || "不明";
      if (!deptGroups[dept]) deptGroups[dept] = [];
      deptGroups[dept].push(p);
    });

    const sortedDepts = Object.keys(deptGroups).sort((a, b) =>
      a.localeCompare(b, "ja")
    );

    return (
      <section className="mb-8">
        <div
          className="flex items-center gap-3 mb-4 px-2"
          style={{ borderLeftWidth: "4px", borderLeftColor: gradeColor }}
        >
          <span
            className="px-3 py-1 rounded-full text-white text-sm font-medium"
            style={{ backgroundColor: gradeColor }}
          >
            {grade}
          </span>
          <span className="text-gray-600 font-medium">研修医</span>
          <span className="text-gray-500 text-sm">({persons.length}名)</span>
        </div>

        <div className="space-y-4 pl-4">
          {sortedDepts.map((dept) => {
            const deptPersons = deptGroups[dept];
            const deptColor = getDeptColor(dept);

            return (
              <div key={`${grade}-${dept}`} className="mb-4">
                <div
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-white text-sm mb-3"
                  style={{ backgroundColor: deptColor }}
                >
                  🏥 {dept}
                  <span className="opacity-80">({deptPersons.length}名)</span>
                </div>
                <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))" }}>
                  {deptPersons.map((person, idx) => (
                    <PersonCard
                      key={`${person.名前}-${person.年度}-${idx}`}
                      person={person}
                      onClick={() => onPersonClick(person)}
                      showYear={showYear}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>
    );
  }

  return (
    <section className="mb-8">
      <div
        className="flex items-center gap-3 mb-4 px-2"
        style={{ borderLeftWidth: "4px", borderLeftColor: gradeColor }}
      >
        <span
          className="px-3 py-1 rounded-full text-white text-sm font-medium"
          style={{ backgroundColor: gradeColor }}
        >
          {grade}
        </span>
        <span className="text-gray-600 font-medium">研修医</span>
        <span className="text-gray-500 text-sm">({persons.length}名)</span>
      </div>

      <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))" }}>
        {persons.map((person, idx) => (
          <PersonCard
            key={`${person.名前}-${person.年度}-${idx}`}
            person={person}
            onClick={() => onPersonClick(person)}
            showYear={showYear}
          />
        ))}
      </div>
    </section>
  );
}
