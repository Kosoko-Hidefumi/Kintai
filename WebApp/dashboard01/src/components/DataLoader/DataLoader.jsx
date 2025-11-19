import React, { useRef } from 'react';
import { Button, Box, Typography } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import Papa from 'papaparse';
import { useData } from '../../contexts/DataContext';
import { parseCSVData } from '../../utils/dataUtils';

const DataLoader = () => {
  const fileInputRef = useRef(null);
  const { loadData, setLoadingState, setErrorState } = useData();

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
    <Box sx={{ mb: 3 }}>
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
        sx={{ mb: 2 }}
      >
        CSVファイルを選択
      </Button>
      <Typography variant="body2" color="text.secondary">
        sample-data.csv を選択してください
      </Typography>
    </Box>
  );
};

export default DataLoader;

