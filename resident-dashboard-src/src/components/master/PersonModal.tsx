import { X, User, Mail, Phone, MapPin, GraduationCap, Building2 } from "lucide-react";
import { ResidentRecord } from "../../types";
import { GRADE_COLORS, getDeptColor } from "../../utils/colors";
import { getResidentPhotoUrl } from "../../utils/photoMatch";

interface PersonModalProps {
  person: ResidentRecord;
  onClose: () => void;
}

export function PersonModal({ person, onClose }: PersonModalProps) {
  const gradeColor = GRADE_COLORS[person.学年] || "#64748B";
  const deptColor = getDeptColor(person.専門科正規化 || "");
  const photoUrl = getResidentPhotoUrl(person.名前);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const fields = [
    { label: "年度", value: person.年度, icon: null },
    { label: "学年", value: person.学年, icon: null },
    { label: "期", value: person["初・後"], icon: null },
    { label: "性別", value: person.性別, icon: User },
    { label: "専門科", value: person.専門科, icon: Building2 },
    { label: "進路", value: person.進路, icon: null },
    { label: "出身大学", value: person.出身大学, icon: GraduationCap },
    { label: "本籍", value: person.本籍, icon: MapPin },
    { label: "PHS", value: person.PHS, icon: Phone },
    { label: "Email", value: person.email, icon: Mail },
  ].filter((f) => f.value);

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span
              className="px-3 py-1 rounded-full text-white text-sm font-medium"
              style={{ backgroundColor: gradeColor }}
            >
              {person.学年}
            </span>
            {person.専門科 && (
              <span
                className="px-3 py-1 rounded-full text-white text-sm font-medium"
                style={{ backgroundColor: deptColor }}
              >
                {person.専門科}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="p-6">
          <div className="flex items-start gap-4 mb-6">
            {photoUrl ? (
              <img
                src={photoUrl}
                alt={person.名前}
                className="w-20 h-20 rounded-full object-cover flex-shrink-0"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 text-gray-400 text-sm">
                写真
              </div>
            )}
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                {person.名前}
              </h2>
              <p className="text-gray-500">{person.ふりがな}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {fields.map((field) => (
              <div
                key={field.label}
                className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
              >
                {field.icon && (
                  <field.icon className="w-4 h-4 text-gray-400 mt-0.5" />
                )}
                <div>
                  <p className="text-xs text-gray-500">{field.label}</p>
                  <p className="text-gray-800 font-medium">{field.value}</p>
                </div>
              </div>
            ))}
          </div>

          {(person.動向調査 || person.備考) && (
            <div className="mt-6 space-y-4">
              {person.動向調査 && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">動向調査</p>
                  <p className="text-gray-800">{person.動向調査}</p>
                </div>
              )}
              {person.備考 && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">備考</p>
                  <p className="text-gray-800">{person.備考}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
