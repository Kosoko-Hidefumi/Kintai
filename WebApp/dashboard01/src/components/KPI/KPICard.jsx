import React from 'react';
import { Card, CardContent, Typography, Grid } from '@mui/material';
import { useData } from '../../contexts/DataContext';
import { calculateKPIs } from '../../utils/dataUtils';

const KPICard = ({ title, value, format = (v) => v }) => {
  return (
    <Card>
      <CardContent>
        <Typography color="text.secondary" gutterBottom variant="body2">
          {title}
        </Typography>
        <Typography variant="h5" component="div">
          {format(value)}
        </Typography>
      </CardContent>
    </Card>
  );
};

const KPIGrid = () => {
  const { filteredData } = useData();
  const kpis = calculateKPIs(filteredData);

  const formatCurrency = (value) => {
    return `¥${value.toLocaleString('ja-JP')}`;
  };

  const formatNumber = (value) => {
    return value.toLocaleString('ja-JP');
  };

  const formatAge = (value) => {
    return `${value.toFixed(1)}歳`;
  };

  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={2.4}>
        <KPICard
          title="総購入金額"
          value={kpis.totalAmount}
          format={formatCurrency}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={2.4}>
        <KPICard
          title="平均購入金額"
          value={kpis.averageAmount}
          format={formatCurrency}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={2.4}>
        <KPICard
          title="総顧客数"
          value={kpis.totalCustomers}
          format={formatNumber}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={2.4}>
        <KPICard
          title="購入件数"
          value={kpis.totalTransactions}
          format={formatNumber}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={2.4}>
        <KPICard
          title="平均年齢"
          value={kpis.averageAge}
          format={formatAge}
        />
      </Grid>
    </Grid>
  );
};

export default KPIGrid;

