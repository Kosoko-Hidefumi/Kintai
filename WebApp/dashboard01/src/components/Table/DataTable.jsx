import React, { useMemo } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Typography } from '@mui/material';
import { useData } from '../../contexts/DataContext';

const DataTable = () => {
  const { filteredData, loading } = useData();

  const columns = [
    { field: '顧客ID', headerName: '顧客ID', width: 100 },
    { field: '年齢', headerName: '年齢', width: 100 },
    { field: '性別', headerName: '性別', width: 100 },
    { field: '地域', headerName: '地域', width: 120 },
    { field: '購入カテゴリー', headerName: '購入カテゴリー', width: 150 },
    {
      field: '購入金額',
      headerName: '購入金額',
      width: 150,
      valueFormatter: (value) => `¥${value.toLocaleString('ja-JP')}`,
    },
    { field: '購入日', headerName: '購入日', width: 150 },
    { field: '支払方法', headerName: '支払方法', width: 150 },
  ];

  const rows = useMemo(() => {
    return filteredData.map((row, index) => ({
      id: index,
      ...row,
    }));
  }, [filteredData]);

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        データテーブル
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
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
        />
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        表示件数: {filteredData.length}件
      </Typography>
    </Box>
  );
};

export default DataTable;

