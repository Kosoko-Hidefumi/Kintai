import { useState, useCallback, useEffect } from "react";
import * as XLSX from "xlsx";
import { ResidentRecord } from "../types";
import { normalizeDept } from "../utils/normalizeDept";
import {
  saveResidentData,
  loadResidentData,
  clearResidentData,
} from "../utils/storage";

/** process_master_file の戻り値を Master 用のフラット配列に変換 */
function flattenProcessMasterResult(raw: unknown): ResidentRecord[] | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as { periods?: unknown };
  if (!Array.isArray(o.periods)) return null;
  const out: ResidentRecord[] = [];
  for (const period of o.periods as { data?: unknown }[]) {
    const rows = period?.data;
    if (!Array.isArray(rows)) continue;
    for (const r of rows) {
      if (!r || typeof r !== "object") continue;
      const row = r as Record<string, unknown>;
      if (!String(row["名前"] ?? "").trim()) continue;
      const 専門科 = String(row["専門科"] ?? "");
      out.push({
        年度: String(row["年度"] ?? ""),
        学年: String(row["学年"] ?? ""),
        "初・後": String(row["初・後"] ?? ""),
        PHS: String(row["PHS"] ?? ""),
        名前: String(row["名前"] ?? ""),
        ふりがな: String(row["ふりがな"] ?? ""),
        性別: String(row["性別"] ?? ""),
        専門科,
        進路: String(row["進路"] ?? ""),
        動向調査: String(row["動向調査"] ?? ""),
        本籍: String(row["本籍"] ?? ""),
        出身大学: String(row["出身大学"] ?? ""),
        備考: String(row["備考"] ?? ""),
        email: String(row["email"] ?? ""),
        専門科正規化: normalizeDept(専門科),
      });
    }
  }
  return out.length > 0 ? out : null;
}

/** 初・後列を検出（「初・後」以外の列名にも対応） */
function findKiColumn(rows: Record<string, unknown>[]): string | null {
  if (rows.length === 0) return null;
  const first = rows[0];
  if (!first) return null;
  if (first["初・後"] !== undefined) return "初・後";
  for (const key of Object.keys(first)) {
    if (key.includes("初") || key.includes("後") || key.includes("期")) return key;
  }
  return null;
}

/** 学年列を検出（「学年」以外の列名にも対応。PGY形式の値を持つ列を探す） */
function findGradeColumn(rows: Record<string, unknown>[]): string | null {
  if (rows.length === 0) return null;
  const first = rows[0];
  if (!first) return null;
  if (first["学年"] !== undefined) return "学年";
  for (const key of Object.keys(first)) {
    if (key === "PGY" || key === "学年" || /学年|年次/.test(key)) return key;
  }
  // 列の値が PGY1〜PGY6 の形式ならその列を学年として使用（複数行をスキャン、1行目が空の場合に対応）
  for (const key of Object.keys(first)) {
    if (key === "年度" || key === "名前") continue;
    for (let i = 0; i < Math.min(10, rows.length); i++) {
      const val = String((rows[i] as Record<string, unknown>)?.[key] ?? "").trim();
      if (/^PGY[1-6]$/.test(val)) return key;
    }
  }
  return null;
}

export function useExcelParser() {
  const [data, setData] = useState<ResidentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const win = window as unknown as {
        __RESIDENT_INITIAL_DATA__?: unknown;
        __RESIDENT_FILENAME__?: string;
      };
      const fromStreamlit = flattenProcessMasterResult(
        win.__RESIDENT_INITIAL_DATA__
      );
      if (fromStreamlit?.length) {
        setData(fromStreamlit);
        const fn = win.__RESIDENT_FILENAME__ || "";
        setFileName(fn);
        saveResidentData(fromStreamlit, fn);
        setIsRestoring(false);
        return;
      }
    }
    const stored = loadResidentData();
    if (stored?.data?.length) {
      setData(stored.data);
      setFileName(stored.fileName || "");
    }
    setIsRestoring(false);
  }, []);

  const parseFile = useCallback((file: File) => {
    setIsLoading(true);
    setError(null);
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const buffer = e.target?.result as ArrayBuffer;
        const wb = XLSX.read(buffer, { type: "array" });
        const sheetName = wb.SheetNames.includes("main")
          ? "main"
          : wb.SheetNames[0];
        const ws = wb.Sheets[sheetName];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(ws, {
          defval: "",
        });
        const kiCol = findKiColumn(rows);
        const gradeCol = findGradeColumn(rows);
        const parsed: ResidentRecord[] = rows
          .filter((r) => r["名前"])
          .map((r) => ({
            年度:   String(r["年度"]   ?? ""),
            学年:   String(gradeCol ? (r[gradeCol] ?? "") : (r["学年"] ?? "")),
            "初・後": String(kiCol ? (r[kiCol] ?? "") : (r["初・後"] ?? "")),
            PHS:    String(r["PHS"]    ?? ""),
            名前:   String(r["名前"]   ?? ""),
            ふりがな: String(r["ふりがな"] ?? ""),
            性別:   String(r["性別"]   ?? ""),
            専門科: String(r["専門科"] ?? ""),
            進路:   String(r["進路"]   ?? ""),
            動向調査: String(r["動向調査"] ?? ""),
            本籍:   String(r["本籍"]   ?? ""),
            出身大学: String(r["出身大学"] ?? ""),
            備考:   String(r["備考"]   ?? ""),
            email:  String(r["email"]  ?? ""),
            専門科正規化: normalizeDept(String(r["専門科"] ?? "")),
          }));
        setData(parsed);
        saveResidentData(parsed, file.name);
      } catch {
        setError("Excelファイルの読み込みに失敗しました。形式を確認してください。");
      } finally {
        setIsLoading(false);
      }
    };
    reader.readAsArrayBuffer(file);
  }, []);

  const resetData = useCallback(() => {
    clearResidentData();
    setData([]);
    setFileName("");
    setError(null);
  }, []);

  return { data, isLoading, isRestoring, error, fileName, parseFile, resetData };
}
