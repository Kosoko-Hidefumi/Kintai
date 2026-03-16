import { useState, useCallback, useRef } from "react";
import { Upload, FileSpreadsheet, Loader2 } from "lucide-react";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
  error: string | null;
}

export function FileUpload({ onFileSelect, isLoading, error }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file && (file.name.endsWith(".xlsx") || file.name.endsWith(".xlsm"))) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleClick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  return (
    <div className="min-h-screen bg-bg-base">
      <header className="bg-gradient-to-r from-primary to-primary-light shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="w-8 h-8 text-white" />
            <h1 className="text-2xl font-bold text-white">
              研修医マスタ & ダッシュボード
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-16">
        <div
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`bg-white rounded-2xl shadow-xl p-12 cursor-pointer transition-all border-2 border-dashed ${
            isDragging
              ? "border-accent bg-accent/5 scale-[1.02]"
              : "border-gray-300 hover:border-accent hover:bg-gray-50"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".xlsx,.xlsm"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="text-center">
            {isLoading ? (
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="w-16 h-16 text-accent animate-spin" />
                <p className="text-lg text-gray-600">読み込み中...</p>
              </div>
            ) : (
              <>
                <Upload
                  className={`w-16 h-16 mx-auto mb-6 ${
                    isDragging ? "text-accent" : "text-gray-400"
                  }`}
                />
                <h2 className="text-xl font-semibold text-gray-700 mb-2">
                  Excelファイルをドラッグ&ドロップ
                </h2>
                <p className="text-gray-500 mb-4">
                  または クリックしてファイルを選択
                </p>
                <p className="text-sm text-gray-400">
                  対応形式: .xlsx / .xlsm
                </p>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-center">{error}</p>
          </div>
        )}
      </main>
    </div>
  );
}
