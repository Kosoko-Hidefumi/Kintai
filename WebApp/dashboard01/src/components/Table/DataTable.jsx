import React, { useMemo } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { useData } from '../../contexts/DataContext';

const DataTable = () => {
  const { filteredData, loading } = useData();

  const columns = [
    { field: '顧客ID', headerName: '顧客ID', width: 100, flex: 0.5 },
    { field: '年齢', headerName: '年齢', width: 100, flex: 0.5 },
    { field: '性別', headerName: '性別', width: 100, flex: 0.5 },
    { field: '地域', headerName: '地域', width: 120, flex: 0.6 },
    { field: '購入カテゴリー', headerName: '購入カテゴリー', width: 150, flex: 0.8 },
    {
      field: '購入金額',
      headerName: '購入金額',
      width: 150,
      flex: 0.8,
      valueFormatter: (value) => `¥${value.toLocaleString('ja-JP')}`,
    },
    { field: '購入日', headerName: '購入日', width: 150, flex: 0.8 },
    { field: '支払方法', headerName: '支払方法', width: 150, flex: 0.8 },
  ];

  const rows = useMemo(() => {
    return filteredData.map((row, index) => ({
      id: index,
      ...row,
    }));
  }, [filteredData]);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, fontSize: '1.125rem', mb: 2 }}>
          データテーブル
        </Typography>
        <Box sx={{ height: 500, width: '100%' }}>
          <DataGrid
            rows={rows}
            columns={columns}
            pageSizeOptions={[10, 25, 50, 100]}
            initialState={{
              pagination: {
                paginationModel: { pageSize: 25 },
              },
            }}
            loading={loading}
            disableRowSelectionOnClick
            sx={{
              border: 'none',
              '& .MuiDataGrid-cell': {
                borderBottom: '1px solid rgba(0, 0, 0, 0.05)',
              },
              '& .MuiDataGrid-columnHeaders': {
                backgroundColor: 'rgba(0, 0, 0, 0.02)',
                borderBottom: '2px solid rgba(0, 0, 0, 0.1)',
              },
            }}
          />
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2, fontSize: '0.75rem' }}>
          表示件数: {filteredData.length}件
        </Typography>
      </CardContent>
    </Card>
  );
};

export default DataTable;

