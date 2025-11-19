import React, { useMemo, useState } from 'react';
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
import { ToggleButtonGroup, ToggleButton, Box } from '@mui/material';
import { useData } from '../../contexts/DataContext';
import {
  aggregateByDay,
  aggregateByWeek,
  aggregateByMonth,
  aggregateByQuarter,
} from '../../utils/dataUtils';
import ChartCard from './ChartCard';

const TransactionCountChart = () => {
  const { filteredData } = useData();
  const [aggregationType, setAggregationType] = useState('month');

  const chartData = useMemo(() => {
    switch (aggregationType) {
      case 'day':
        return aggregateByDay(filteredData);
      case 'week':
        return aggregateByWeek(filteredData);
      case 'month':
        return aggregateByMonth(filteredData);
      case 'quarter':
        return aggregateByQuarter(filteredData);
      default:
        return aggregateByMonth(filteredData);
    }
  }, [filteredData, aggregationType]);

  const getXAxisKey = () => {
    switch (aggregationType) {
      case 'day':
        return 'day';
      case 'week':
        return 'week';
      case 'month':
        return 'month';
      case 'quarter':
        return 'quarter';
      default:
        return 'month';
    }
  };

  const getSubtitle = () => {
    switch (aggregationType) {
      case 'day':
        return '日別の購入件数推移';
      case 'week':
        return '週別の購入件数推移';
      case 'month':
        return '月別の購入件数推移';
      case 'quarter':
        return '四半期別の購入件数推移';
      default:
        return '月別の購入件数推移';
    }
  };

  return (
    <ChartCard title="購入件数の時系列推移" subtitle={getSubtitle()}>
      <Box sx={{ mb: 2 }}>
        <ToggleButtonGroup
          value={aggregationType}
          exclusive
          onChange={(e, newValue) => {
            if (newValue !== null) {
              setAggregationType(newValue);
            }
          }}
          size="small"
          sx={{
            '& .MuiToggleButton-root': {
              textTransform: 'none',
              borderRadius: 2,
              px: 2,
              py: 0.75,
            },
          }}
        >
          <ToggleButton value="day">日別</ToggleButton>
          <ToggleButton value="week">週別</ToggleButton>
          <ToggleButton value="month">月別</ToggleButton>
          <ToggleButton value="quarter">四半期別</ToggleButton>
        </ToggleButtonGroup>
      </Box>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={getXAxisKey()} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#dc004e"
            strokeWidth={2}
            name="購入件数"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default TransactionCountChart;

