import React from 'react';
import {
  Paper,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Select,
  MenuItem,
  FormControl as MuiFormControl,
  InputLabel,
  Checkbox,
  ListItemText,
  Box,
  Button,
  Slider,
  Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import 'dayjs/locale/ja';
import { useFilter } from '../../contexts/FilterContext';

const FilterPanel = () => {
  const { filters, updateFilter, resetFilters } = useFilter();

  const categories = ['スポーツ', '家電', '食品', 'ファッション', '書籍'];
  const regions = ['関東', '中部', '関西', '九州'];
  const paymentMethods = ['クレジットカード', '電子マネー', '現金'];

  return (
    <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.125rem' }}>
          フィルタ
        </Typography>
        <Button
          variant="outlined"
          size="small"
          onClick={resetFilters}
          sx={{ textTransform: 'none', borderRadius: 2 }}
        >
          リセット
        </Button>
      </Box>

      {/* 性別フィルタ */}
      <FormControl component="fieldset" sx={{ mb: 3, width: '100%' }}>
        <FormLabel component="legend" sx={{ mb: 1, fontSize: '0.875rem', fontWeight: 500 }}>
          性別
        </FormLabel>
        <RadioGroup
          row
          value={filters.gender}
          onChange={(e) => updateFilter('gender', e.target.value)}
        >
          <FormControlLabel value="all" control={<Radio size="small" />} label="すべて" />
          <FormControlLabel value="男性" control={<Radio size="small" />} label="男性" />
          <FormControlLabel value="女性" control={<Radio size="small" />} label="女性" />
        </RadioGroup>
      </FormControl>

      {/* 地域フィルタ */}
      <MuiFormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>地域</InputLabel>
        <Select
          value={filters.region}
          label="地域"
          onChange={(e) => updateFilter('region', e.target.value)}
        >
          <MenuItem value="all">すべて</MenuItem>
          {regions.map((region) => (
            <MenuItem key={region} value={region}>
              {region}
            </MenuItem>
          ))}
        </Select>
      </MuiFormControl>

      {/* 購入カテゴリーフィルタ */}
      <MuiFormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>購入カテゴリー</InputLabel>
        <Select
          multiple
          value={filters.categories}
          label="購入カテゴリー"
          onChange={(e) => updateFilter('categories', e.target.value)}
          renderValue={(selected) => selected.join(', ')}
        >
          {categories.map((category) => (
            <MenuItem key={category} value={category}>
              <Checkbox checked={filters.categories.indexOf(category) > -1} />
              <ListItemText primary={category} />
            </MenuItem>
          ))}
        </Select>
      </MuiFormControl>

      {/* 支払方法フィルタ */}
      <MuiFormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>支払方法</InputLabel>
        <Select
          multiple
          value={filters.paymentMethods}
          label="支払方法"
          onChange={(e) => updateFilter('paymentMethods', e.target.value)}
          renderValue={(selected) => selected.join(', ')}
        >
          {paymentMethods.map((method) => (
            <MenuItem key={method} value={method}>
              <Checkbox checked={filters.paymentMethods.indexOf(method) > -1} />
              <ListItemText primary={method} />
            </MenuItem>
          ))}
        </Select>
      </MuiFormControl>

      <Divider sx={{ my: 3 }} />

      {/* 日付範囲フィルタ */}
      <Typography variant="subtitle2" gutterBottom sx={{ mb: 2 }}>
        購入日範囲
      </Typography>
      <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ja">
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <DatePicker
            label="開始日"
            value={filters.dateRange.start ? dayjs(filters.dateRange.start) : null}
            onChange={(newValue) => {
              updateFilter('dateRange', {
                ...filters.dateRange,
                start: newValue ? newValue.format('YYYY-MM-DD') : null,
              });
            }}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
          <DatePicker
            label="終了日"
            value={filters.dateRange.end ? dayjs(filters.dateRange.end) : null}
            onChange={(newValue) => {
              updateFilter('dateRange', {
                ...filters.dateRange,
                end: newValue ? newValue.format('YYYY-MM-DD') : null,
              });
            }}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
        </Box>
      </LocalizationProvider>

      <Divider sx={{ my: 3 }} />

      {/* 年齢範囲フィルタ */}
      <Typography variant="subtitle2" gutterBottom sx={{ mb: 1 }}>
        年齢範囲: {filters.ageRange[0]}歳 ～ {filters.ageRange[1]}歳
      </Typography>
      <Slider
        value={filters.ageRange}
        onChange={(e, newValue) => updateFilter('ageRange', newValue)}
        valueLabelDisplay="auto"
        min={18}
        max={75}
        marks={[
          { value: 18, label: '18' },
          { value: 30, label: '30' },
          { value: 50, label: '50' },
          { value: 75, label: '75' },
        ]}
        sx={{ mb: 3 }}
      />

      {/* 購入金額範囲フィルタ */}
      <Typography variant="subtitle2" gutterBottom sx={{ mb: 1 }}>
        購入金額範囲: ¥{filters.amountRange[0].toLocaleString('ja-JP')} ～ ¥{filters.amountRange[1].toLocaleString('ja-JP')}
      </Typography>
      <Slider
        value={filters.amountRange}
        onChange={(e, newValue) => updateFilter('amountRange', newValue)}
        valueLabelDisplay="auto"
        valueLabelFormat={(value) => `¥${value.toLocaleString('ja-JP')}`}
        min={0}
        max={70000}
        step={1000}
        marks={[
          { value: 0, label: '¥0' },
          { value: 25000, label: '¥25,000' },
          { value: 50000, label: '¥50,000' },
          { value: 70000, label: '¥70,000' },
        ]}
      />
    </Paper>
  );
};

export default FilterPanel;

