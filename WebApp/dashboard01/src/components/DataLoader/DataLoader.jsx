import React, { useRef, useEffect } from 'react';
import { Button, Box, Typography, Snackbar, Alert } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import Papa from 'papaparse';
import { useData } from '../../contexts/DataContext';
import { parseCSVData } from '../../utils/dataUtils';

const DataLoader = () => {
  const fileInputRef = useRef(null);
  const { loadData, setLoadingState, setErrorState, filteredData } = useData();
  const [successOpen, setSuccessOpen] = React.useState(false);

  useEffect(() => {
    if (filteredData.length > 0) {
      setSuccessOpen(true);
    }
  }, [filteredData.length]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setErrorState('CSVファイルを選択してください');
      return;
    }

    setLoadingState(true);
    setErrorState(null);

    Papa.parse(file, {
      header: true,
      encoding: 'UTF-8',
      skipEmptyLines: true,
      complete: (results) => {
        try {
          if (results.errors.length > 0) {
            console.warn('CSVパースエラー:', results.errors);
          }

          const parsedData = parseCSVData(results.data);
          loadData(parsedData);
          setLoadingState(false);
        } catch (error) {
          console.error('データ処理エラー:', error);
          setErrorState('データの処理中にエラーが発生しました');
          setLoadingState(false);
        }
      },
      error: (error) => {
        console.error('CSV読み込みエラー:', error);
        setErrorState('CSVファイルの読み込みに失敗しました');
        setLoadingState(false);
      },
    });
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <Box sx={{ mb: 4 }}>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />
      <Button
        variant="contained"
        startIcon={<CloudUpload />}
        onClick={handleButtonClick}
        sx={{ mb: 1.5, textTransform: 'none', borderRadius: 2, px: 3, py: 1 }}
      >
        CSVファイルを選択
      </Button>
      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
        sample-data.csv を選択してください
      </Typography>
      <Snackbar
        open={successOpen}
        autoHideDuration={3000}
        onClose={() => setSuccessOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccessOpen(false)} severity="success" sx={{ width: '100%' }}>
          データの読み込みが完了しました（{filteredData.length}件）
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DataLoader;

