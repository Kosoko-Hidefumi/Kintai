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
import { aggregateByPaymentMethod } from '../../utils/dataUtils';
import ChartCard from './ChartCard';

const COLORS = ['#1976d2', '#dc004e', '#ed6c02'];

const PaymentMethodChart = () => {
  const { filteredData } = useData();

  const chartData = useMemo(() => {
    return aggregateByPaymentMethod(filteredData);
  }, [filteredData]);

  return (
    <ChartCard title="支払方法別購入金額分布">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ method, percent }) => percent > 0.05 ? `${method} ${(percent * 100).toFixed(0)}%` : ''}
            outerRadius={100}
            innerRadius={40}
            fill="#8884d8"
            dataKey="amount"
            nameKey="method"
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

export default PaymentMethodChart;

