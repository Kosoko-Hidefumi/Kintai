export interface ResidentRecord {
  年度: string;
  学年: string;
  "初・後": string;
  PHS: string;
  名前: string;
  ふりがな: string;
  性別: string;
  専門科: string;
  進路: string;
  動向調査: string;
  本籍: string;
  出身大学: string;
  備考: string;
  email: string;
  専門科正規化?: string;
}

export type ViewMode = "card" | "table";
export type SortMode = "grade" | "kana" | "dept";
export type TabType = "master" | "dashboard";
