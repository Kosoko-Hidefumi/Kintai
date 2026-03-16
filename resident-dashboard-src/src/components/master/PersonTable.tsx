import { useState } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";
import { ResidentRecord } from "../../types";
import { GRADE_COLORS } from "../../utils/colors";
import { getResidentPhotoUrl } from "../../utils/photoMatch";

interface PersonTableProps {
  data: ResidentRecord[];
  grade: string;
  onPersonClick: (person: ResidentRecord) => void;
  showYear?: boolean;
}

type SortColumn =
  | "ふりがな"
  | "性別"
  | "初・後"
  | "専門科"
  | "出身大学"
  | "本籍"
  | "進路"
  | "PHS";

export function PersonTable({
  data,
  grade,
  onPersonClick,
  showYear,
}: PersonTableProps) {
  const [sortColumn, setSortColumn] = useState<SortColumn | null>(null);
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortAsc(!sortAsc);
    } else {
      setSortColumn(column);
      setSortAsc(true);
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortColumn) return 0;
    const aVal = a[sortColumn] || "";
    const bVal = b[sortColumn] || "";
    const compare = aVal.localeCompare(bVal, "ja");
    return sortAsc ? compare : -compare;
  });

  const gradeColor = GRADE_COLORS[grade] || "#64748B";

  const columns: { key: SortColumn; label: string }[] = [
    { key: "ふりがな", label: "名前" },
    { key: "性別", label: "性別" },
    { key: "初・後", label: "期" },
    { key: "専門科", label: "専門科" },
    { key: "出身大学", label: "出身大学" },
    { key: "本籍", label: "本籍" },
    { key: "進路", label: "進路" },
    { key: "PHS", label: "PHS" },
  ];

  return (
    <div className="mb-8">
      <div
        className="flex items-center gap-3 mb-3 px-2"
        style={{ borderLeftWidth: "4px", borderLeftColor: gradeColor }}
      >
        <span
          className="px-3 py-1 rounded-full text-white text-sm font-medium"
          style={{ backgroundColor: gradeColor }}
        >
          {grade}
        </span>
        <span className="text-gray-600">研修医</span>
        <span className="text-gray-500 text-sm">({data.length}名)</span>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b">
              {showYear && (
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  年度
                </th>
              )}
              <th className="px-2 py-3 text-left font-medium text-gray-600 w-12">
                写真
              </th>
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className={`px-4 py-3 text-left font-medium cursor-pointer hover:bg-gray-100 transition-colors ${
                    sortColumn === col.key ? "text-primary-light" : "text-gray-600"
                  }`}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {sortColumn === col.key ? (
                      sortAsc ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )
                    ) : null}
                  </div>
                </th>
              ))}
              <th className="px-4 py-3 text-left font-medium text-gray-600">
                備考
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((person, idx) => (
              <tr
                key={`${person.名前}-${person.年度}-${idx}`}
                onClick={() => onPersonClick(person)}
                className="border-b hover:bg-blue-50 cursor-pointer transition-colors"
              >
                {showYear && (
                  <td className="px-4 py-3 text-gray-600">{person.年度}</td>
                )}
                <td className="px-2 py-3">
                  {getResidentPhotoUrl(person.名前) ? (
                    <img
                      src={getResidentPhotoUrl(person.名前)}
                      alt={person.名前}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 text-[10px]">
                      -
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div>
                    <span className="font-medium text-gray-800">
                      {person.名前}
                    </span>
                    {person.ふりがな && (
                      <span className="text-xs text-gray-500 ml-1">
                        ({person.ふりがな})
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 text-xs rounded ${
                      person.性別 === "男"
                        ? "bg-blue-100 text-blue-700"
                        : person.性別 === "女"
                        ? "bg-pink-100 text-pink-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {person.性別 || "-"}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {person["初・後"] || "-"}
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {person.専門科 || "-"}
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {person.出身大学 || "-"}
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {person.本籍 || "-"}
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {person.進路 || "-"}
                </td>
                <td className="px-4 py-3 text-gray-600">{person.PHS || "-"}</td>
                <td className="px-4 py-3 text-gray-500 text-xs max-w-[200px] truncate">
                  {person.備考 || "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
