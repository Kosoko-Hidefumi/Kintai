import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useData } from '../../contexts/DataContext';
import { aggregateByCategory } from '../../utils/dataUtils';
import ChartCard from './ChartCard';

const COLORS = ['#1976d2', '#dc004e', '#ed6c02', '#2e7d32', '#9c27b0'];

const CategoryCountChart = () => {
  const { filteredData } = useData();

  const chartData = useMemo(() => {
    return aggregateByCategory(filteredData);
  }, [filteredData]);

  return (
    <ChartCard title="購入カテゴリー別購入件数">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ category, percent }) => percent > 0.05 ? `${category} ${(percent * 100).toFixed(0)}%` : ''}
            outerRadius={100}
            innerRadius={40}
            fill="#8884d8"
            dataKey="count"
            nameKey="category"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default CategoryCountChart;

