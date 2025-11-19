import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useData } from '../../contexts/DataContext';
import { aggregateByMonth } from '../../utils/dataUtils';
import ChartCard from './ChartCard';

const TimeSeriesChart = () => {
  const { filteredData } = useData();

  const chartData = useMemo(() => {
    return aggregateByMonth(filteredData);
  }, [filteredData]);

  return (
    <ChartCard title="購入金額の時系列推移（月別）">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip
            formatter={(value) => [`¥${value.toLocaleString('ja-JP')}`, '購入金額']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="amount"
            stroke="#1976d2"
            strokeWidth={2}
            name="購入金額"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default TimeSeriesChart;

