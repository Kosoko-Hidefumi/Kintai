export function normalizeDept(dept: string): string {
  if (!dept) return "不明";
  if (dept.includes("外科（一般外科）") || dept.includes("外科(一般外科）"))
    return "外科（一般外科）";
  if (dept.includes("外科（整形") || dept.includes("外科(整形)"))
    return "外科（整形外科）";
  if (dept.includes("外科（形成"))
    return "外科（形成外科）";
  if (dept.includes("外科（脳") || dept.includes("外科(脳") || dept.includes("脳神経外科"))
    return "外科（脳神経外科）";
  if (dept.includes("外科（耳鼻") || dept.includes("外科（泌尿") || dept.includes("耳鼻咽喉科"))
    return "外科（その他）";
  if (dept.includes("外科系")) return "外科系";
  if (dept.includes("外科"))    return "外科";
  if (
    dept.includes("救命救急科") || dept.includes("救急救命科") ||
    dept.includes("救急科")     || dept.includes("救急")
  ) return "救急科";
  if (dept.includes("内科"))    return "内科";
  if (dept.includes("泌尿器"))  return "泌尿器科";
  return dept;
}
