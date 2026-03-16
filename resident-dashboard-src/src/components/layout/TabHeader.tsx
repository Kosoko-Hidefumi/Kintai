import { Building2, Users, BarChart3, FileUp } from "lucide-react";
import { TabType } from "../../types";

interface TabHeaderProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  fileName: string;
  onReset: () => void;
}

export function TabHeader({
  activeTab,
  onTabChange,
  fileName,
  onReset,
}: TabHeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-gradient-to-r from-primary to-primary-light shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-2">
            <Building2 className="w-6 h-6 text-white" />
            <span className="text-white font-bold text-lg">研修医マスタ</span>
          </div>

          <nav className="flex items-center gap-1">
            <button
              onClick={() => onTabChange("master")}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${
                activeTab === "master"
                  ? "text-white border-b-2 border-accent"
                  : "text-white/70 hover:text-white"
              }`}
            >
              <Users className="w-4 h-4" />
              <span>研修医マスタ</span>
            </button>
            <button
              onClick={() => onTabChange("dashboard")}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${
                activeTab === "dashboard"
                  ? "text-white border-b-2 border-accent"
                  : "text-white/70 hover:text-white"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>専門科ダッシュボード</span>
            </button>
          </nav>

          <div className="flex items-center gap-3">
            <span className="text-white/70 text-sm truncate max-w-[200px]">
              {fileName}
            </span>
            <button
              onClick={onReset}
              className="flex items-center gap-1 px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white text-sm rounded transition-colors"
            >
              <FileUp className="w-4 h-4" />
              ファイルを変更
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
