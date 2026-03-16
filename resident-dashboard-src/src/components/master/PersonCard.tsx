import { Phone } from "lucide-react";
import { ResidentRecord } from "../../types";
import { getDeptColor } from "../../utils/colors";
import { getResidentPhotoUrl } from "../../utils/photoMatch";

interface PersonCardProps {
  person: ResidentRecord;
  onClick: () => void;
  showYear?: boolean;
}

export function PersonCard({ person, onClick, showYear }: PersonCardProps) {
  const deptColor = getDeptColor(person.専門科正規化 || "");
  const photoUrl = getResidentPhotoUrl(person.名前);

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-sm border cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md hover:border-accent group"
      style={{ borderTopWidth: "3px", borderTopColor: deptColor }}
    >
      <div className="p-4">
        <div className="flex justify-between items-start gap-3 mb-2">
          {photoUrl ? (
            <img
              src={photoUrl}
              alt={person.名前}
              className="w-12 h-12 rounded-full object-cover flex-shrink-0"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 text-gray-400 text-xs">
              写真
            </div>
          )}
          <div className="flex-1 min-w-0 overflow-hidden">
            <h3 className="font-bold text-gray-800 group-hover:text-primary break-words leading-tight">
              {person.名前}
            </h3>
            <p className="text-sm text-gray-500 break-words leading-tight">{person.ふりがな}</p>
          </div>
          {person.PHS && (
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Phone className="w-3 h-3" />
              {person.PHS}
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-1.5 mt-3">
          {showYear && person.年度 && (
            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
              {person.年度}年
            </span>
          )}
          {person.専門科 && (
            <span
              className="px-2 py-0.5 text-xs text-white rounded"
              style={{ backgroundColor: deptColor }}
            >
              {person.専門科}
            </span>
          )}
          {person["初・後"] && (
            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
              {person["初・後"]}
            </span>
          )}
          {person.出身大学 && (
            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
              {person.出身大学}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
