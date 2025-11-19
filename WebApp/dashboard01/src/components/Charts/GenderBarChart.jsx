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
import { aggregateByGender } from '../../utils/dataUtils';
import ChartCard from './ChartCard';

const COLORS = ['#1976d2', '#dc004e'];

const GenderBarChart = () => {
  const { filteredData } = useData();

  const chartData = useMemo(() => {
    return aggregateByGender(filteredData);
  }, [filteredData]);

  return (
    <ChartCard title="性別購入金額分布">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ gender, percent }) => `${gender} ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            innerRadius={40}
            fill="#8884d8"
            dataKey="amount"
            nameKey="gender"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => `¥${value.toLocaleString('ja-JP')}`}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default GenderBarChart;

