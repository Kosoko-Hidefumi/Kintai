import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useData } from '../../contexts/DataContext';
import { aggregateByCategory } from '../../utils/dataUtils';
import ChartCard from './ChartCard';

const CategoryBarChart = () => {
  const { filteredData } = useData();

  const chartData = useMemo(() => {
    return aggregateByCategory(filteredData);
  }, [filteredData]);

  return (
    <ChartCard title="購入カテゴリー別購入金額">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip
            formatter={(value) => [`¥${value.toLocaleString('ja-JP')}`, '購入金額']}
          />
          <Legend />
          <Bar dataKey="amount" fill="#1976d2" name="購入金額" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default CategoryBarChart;

