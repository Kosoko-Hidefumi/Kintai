import { useState } from "react";
import { TabType } from "./types";
import { useExcelParser } from "./hooks/useExcelParser";
import { FileUpload } from "./components/upload/FileUpload";
import { TabHeader } from "./components/layout/TabHeader";
import { MasterTab } from "./components/master/MasterTab";
import { DashboardTab } from "./components/dashboard/DashboardTab";

function App() {
  const { data, isLoading, isRestoring, error, fileName, parseFile, resetData } =
    useExcelParser();
  const [activeTab, setActiveTab] = useState<TabType>("master");

  if (isRestoring) {
    return (
      <div className="min-h-screen bg-bg-base flex items-center justify-center">
        <div className="animate-pulse text-gray-500">読み込み中...</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <FileUpload
        onFileSelect={parseFile}
        isLoading={isLoading}
        error={error}
      />
    );
  }

  return (
    <div className="min-h-screen bg-bg-base">
      <TabHeader
        activeTab={activeTab}
        onTabChange={setActiveTab}
        fileName={fileName}
        onReset={resetData}
      />
      {activeTab === "master" && <MasterTab data={data} />}
      {activeTab === "dashboard" && <DashboardTab data={data} />}
    </div>
  );
}

export default App;
