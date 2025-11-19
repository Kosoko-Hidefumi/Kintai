import React, { useEffect } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import 'dayjs/locale/ja';
import { Snackbar, Alert, CircularProgress, Box, Grid, Card, CardContent, Typography } from '@mui/material';
import theme from './theme/theme';
import { DataProvider, useData } from './contexts/DataContext';
import { FilterProvider, useFilter } from './contexts/FilterContext';
import Layout from './components/Layout/Layout';
import DataLoader from './components/DataLoader/DataLoader';
import FilterPanel from './components/Filters/FilterPanel';
import KPIGrid from './components/KPI/KPICard';
import CategoryBarChart from './components/Charts/CategoryBarChart';
import CategoryCountChart from './components/Charts/CategoryCountChart';
import TimeSeriesChart from './components/Charts/TimeSeriesChart';
import TransactionCountChart from './components/Charts/TransactionCountChart';
import RegionBarChart from './components/Charts/RegionBarChart';
import PaymentMethodChart from './components/Charts/PaymentMethodChart';
import GenderBarChart from './components/Charts/GenderBarChart';
import DataTable from './components/Table/DataTable';
import { applyFilters } from './utils/dataUtils';

const DashboardContent = () => {
  const { rawData, filteredData, loading, error, updateFilteredData, setErrorState } = useData();
  const { filters } = useFilter();
  const [snackbarOpen, setSnackbarOpen] = React.useState(false);
  const [snackbarMessage, setSnackbarMessage] = React.useState('');

  // フィルタ適用
  useEffect(() => {
    if (rawData.length > 0) {
      const filtered = applyFilters(rawData, filters);
      updateFilteredData(filtered);
    }
  }, [rawData, filters, updateFilteredData]);

  // エラー通知
  useEffect(() => {
    if (error) {
      setSnackbarMessage(error);
      setSnackbarOpen(true);
    }
  }, [error]);

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Layout>
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      <DataLoader />

      {filteredData.length > 0 && (
        <>
          <FilterPanel />
          <KPIGrid />
          <Box sx={{ mb: 4 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} lg={6}>
                <TimeSeriesChart />
              </Grid>
              <Grid item xs={12} lg={6}>
                <TransactionCountChart />
              </Grid>
            </Grid>
          </Box>
          <Box sx={{ mb: 4 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6} lg={4}>
                <CategoryBarChart />
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                <CategoryCountChart />
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                <RegionBarChart />
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                <PaymentMethodChart />
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                <GenderBarChart />
              </Grid>
            </Grid>
          </Box>
          <DataTable />
        </>
      )}

      {filteredData.length === 0 && !loading && (
        <Card sx={{ textAlign: 'center', py: 8, mb: 3 }}>
          <CardContent>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
              データがありません
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
              CSVファイルを読み込んでデータを表示してください
            </Typography>
          </CardContent>
        </Card>
      )}

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity="error" sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Layout>
  );
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ja">
        <DataProvider>
          <FilterProvider>
            <DashboardContent />
          </FilterProvider>
        </DataProvider>
      </LocalizationProvider>
    </ThemeProvider>
  );
}

export default App;

