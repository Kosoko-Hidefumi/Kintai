import React, { useMemo } from 'react';
import { Card, CardContent, Typography, Box, Grid } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts';
import { useData } from '../../contexts/DataContext';
import { calculateKPIs, aggregateByMonth } from '../../utils/dataUtils';

const KPICard = ({ title, value, format = (v) => v, trend, trendData, color = '#1976d2' }) => {
  const isPositive = trend >= 0;

  return (
    <Card sx={{ height: '100%', transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 } }}>
      <CardContent sx={{ p: 2.5 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontSize: '0.75rem', fontWeight: 500 }}>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4" component="div" sx={{ fontWeight: 600, fontSize: '1.75rem', lineHeight: 1.2 }}>
            {format(value)}
          </Typography>
          {trend !== null && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                color: isPositive ? 'success.main' : 'error.main',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              {isPositive ? (
                <TrendingUp sx={{ fontSize: 16 }} />
              ) : (
                <TrendingDown sx={{ fontSize: 16 }} />
              )}
              <Typography variant="body2" sx={{ fontSize: '0.75rem', fontWeight: 600 }}>
                {isPositive ? '+' : ''}{trend.toFixed(1)}%
              </Typography>
            </Box>
          )}
        </Box>
        {trendData && trendData.length > 0 && (
          <Box sx={{ height: 60, mt: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <Tooltip contentStyle={{ display: 'none' }} />
                <Line
                  type="monotone"
                  dataKey="amount"
                  stroke={color}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontSize: '0.7rem' }}>
          フィルタ適用後のデータ
        </Typography>
      </CardContent>
    </Card>
  );
};

const KPIGrid = () => {
  const { filteredData, rawData } = useData();
  const kpis = calculateKPIs(filteredData);
  const rawKPIs = useMemo(() => {
    if (rawData.length === 0) return null;
    return calculateKPIs(rawData);
  }, [rawData]);

  // トレンドデータ（月別集計）
  const monthlyData = useMemo(() => {
    if (filteredData.length === 0) return [];
    const data = aggregateByMonth(filteredData);
    // トレンドグラフ用に簡略化（最後の6ヶ月分）
    return data.slice(-6).map(item => ({ amount: item.amount }));
  }, [filteredData]);

  // 変化率の計算
  const calculateTrend = (current, previous) => {
    if (!rawKPIs || previous === 0) return null;
    return ((current - previous) / previous) * 100;
  };

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `¥${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `¥${(value / 1000).toFixed(0)}k`;
    }
    return `¥${value.toLocaleString('ja-JP')}`;
  };

  const formatNumber = (value) => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}k`;
    }
    return value.toLocaleString('ja-JP');
  };

  const formatAge = (value) => {
    return `${value.toFixed(1)}歳`;
  };

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} sm={6} md={4} lg={2.4}>
        <KPICard
          title="総購入金額"
          value={kpis.totalAmount}
          format={formatCurrency}
          trend={rawKPIs ? calculateTrend(kpis.totalAmount, rawKPIs.totalAmount) : null}
          trendData={monthlyData}
          color="#1976d2"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={2.4}>
        <KPICard
          title="平均購入金額"
          value={kpis.averageAmount}
          format={formatCurrency}
          trend={rawKPIs ? calculateTrend(kpis.averageAmount, rawKPIs.averageAmount) : null}
          trendData={monthlyData}
          color="#dc004e"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={2.4}>
        <KPICard
          title="総顧客数"
          value={kpis.totalCustomers}
          format={formatNumber}
          trend={rawKPIs ? calculateTrend(kpis.totalCustomers, rawKPIs.totalCustomers) : null}
          color="#2e7d32"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={2.4}>
        <KPICard
          title="購入件数"
          value={kpis.totalTransactions}
          format={formatNumber}
          trend={rawKPIs ? calculateTrend(kpis.totalTransactions, rawKPIs.totalTransactions) : null}
          trendData={monthlyData.map(item => ({ amount: item.count }))}
          color="#ed6c02"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={2.4}>
        <KPICard
          title="平均年齢"
          value={kpis.averageAge}
          format={formatAge}
          trend={rawKPIs ? calculateTrend(kpis.averageAge, rawKPIs.averageAge) : null}
          color="#9c27b0"
        />
      </Grid>
    </Grid>
  );
};

export default KPIGrid;
