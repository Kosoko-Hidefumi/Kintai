import dayjs from 'dayjs';

/**
 * CSVデータをパースして、適切な型に変換する
 */
export const parseCSVData = (csvData) => {
  return csvData.map((row) => ({
    ...row,
    顧客ID: parseInt(row.顧客ID, 10),
    年齢: parseInt(row.年齢, 10),
    購入金額: parseInt(row.購入金額, 10),
    購入日: dayjs(row.購入日).format('YYYY-MM-DD'),
  }));
};

/**
 * フィルタを適用してデータをフィルタリング
 */
export const applyFilters = (data, filters) => {
  let filtered = [...data];

  // 性別フィルタ
  if (filters.gender !== 'all') {
    filtered = filtered.filter((item) => item.性別 === filters.gender);
  }

  // 地域フィルタ
  if (filters.region !== 'all') {
    filtered = filtered.filter((item) => item.地域 === filters.region);
  }

  // 購入カテゴリーフィルタ
  if (filters.categories.length > 0) {
    filtered = filtered.filter((item) =>
      filters.categories.includes(item.購入カテゴリー)
    );
  }

  // 支払方法フィルタ
  if (filters.paymentMethods.length > 0) {
    filtered = filtered.filter((item) =>
      filters.paymentMethods.includes(item.支払方法)
    );
  }

  // 年齢範囲フィルタ
  filtered = filtered.filter(
    (item) =>
      item.年齢 >= filters.ageRange[0] && item.年齢 <= filters.ageRange[1]
  );

  // 購入金額範囲フィルタ
  filtered = filtered.filter(
    (item) =>
      item.購入金額 >= filters.amountRange[0] &&
      item.購入金額 <= filters.amountRange[1]
  );

  // 日付範囲フィルタ
  if (filters.dateRange && filters.dateRange.start) {
    filtered = filtered.filter((item) =>
      dayjs(item.購入日).isSameOrAfter(dayjs(filters.dateRange.start))
    );
  }
  if (filters.dateRange && filters.dateRange.end) {
    filtered = filtered.filter((item) =>
      dayjs(item.購入日).isSameOrBefore(dayjs(filters.dateRange.end))
    );
  }

  return filtered;
};

/**
 * KPI指標を計算
 */
export const calculateKPIs = (data) => {
  if (data.length === 0) {
    return {
      totalAmount: 0,
      averageAmount: 0,
      totalCustomers: 0,
      totalTransactions: data.length,
      averageAge: 0,
    };
  }

  const totalAmount = data.reduce((sum, item) => sum + item.購入金額, 0);
  const averageAmount = totalAmount / data.length;
  const uniqueCustomers = new Set(data.map((item) => item.顧客ID)).size;
  const totalAge = data.reduce((sum, item) => sum + item.年齢, 0);
  const averageAge = totalAge / data.length;

  return {
    totalAmount,
    averageAmount,
    totalCustomers: uniqueCustomers,
    totalTransactions: data.length,
    averageAge,
  };
};

/**
 * 月別集計
 */
export const aggregateByMonth = (data) => {
  const aggregated = {};
  
  data.forEach((item) => {
    const month = dayjs(item.購入日).format('YYYY-MM');
    if (!aggregated[month]) {
      aggregated[month] = {
        month,
        amount: 0,
        count: 0,
      };
    }
    aggregated[month].amount += item.購入金額;
    aggregated[month].count += 1;
  });

  return Object.values(aggregated).sort((a, b) => a.month.localeCompare(b.month));
};

/**
 * カテゴリー別集計
 */
export const aggregateByCategory = (data) => {
  const aggregated = {};
  
  data.forEach((item) => {
    const category = item.購入カテゴリー;
    if (!aggregated[category]) {
      aggregated[category] = {
        category,
        amount: 0,
        count: 0,
      };
    }
    aggregated[category].amount += item.購入金額;
    aggregated[category].count += 1;
  });

  return Object.values(aggregated);
};

