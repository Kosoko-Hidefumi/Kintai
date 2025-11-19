import React, { useEffect } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import 'dayjs/locale/ja';
import { Snackbar, Alert, CircularProgress, Box } from '@mui/material';
import theme from './theme/theme';
import { DataProvider, useData } from './contexts/DataContext';
import { FilterProvider, useFilter } from './contexts/FilterContext';
import Layout from './components/Layout/Layout';
import DataLoader from './components/DataLoader/DataLoader';
import FilterPanel from './components/Filters/FilterPanel';
import KPIGrid from './components/KPI/KPICard';
import CategoryBarChart from './components/Charts/CategoryBarChart';
import TimeSeriesChart from './components/Charts/TimeSeriesChart';
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
          <CategoryBarChart />
          <TimeSeriesChart />
          <DataTable />
        </>
      )}

      {filteredData.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <p>CSVファイルを読み込んでください</p>
        </Box>
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

