export const GRADE_COLORS: Record<string, string> = {
  PGY1: "#3B82F6",
  PGY2: "#10B981",
  PGY3: "#F59E0B",
  PGY4: "#EF4444",
  PGY5: "#8B5CF6",
  PGY6: "#EC4899",
};

export const DEPT_COLORS: Record<string, string> = {
  "内科":           "#3B82F6",
  "総合診療科":     "#10B981",
  "救急科":         "#F59E0B",
  "産婦人科":       "#EC4899",
  "小児科":         "#8B5CF6",
  "外科":           "#EF4444",
  "外科（一般外科）": "#F97316",
  "プライマリ":     "#22C55E",
  "外科（脳神経外科）": "#84CC16",
  "外科（形成外科）":  "#14B8A6",
  "外科（整形外科）":  "#A78BFA",
  "外科（その他）":    "#64748B",
  "外科系":         "#FB923C",
  "泌尿器科":       "#6B7280",
  "麻酔科":         "#06B6D4",
  "病理":           "#94A3B8",
  "精神科":         "#0EA5E9",
  "うるま":         "#78716C",
};

export function getDeptColor(dept: string): string {
  return DEPT_COLORS[dept] ?? "#94A3B8";
}

export function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}
