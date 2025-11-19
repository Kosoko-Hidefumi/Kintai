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
} from '@mui/material';
import { useFilter } from '../../contexts/FilterContext';

const FilterPanel = () => {
  const { filters, updateFilter, resetFilters } = useFilter();

  const categories = ['スポーツ', '家電', '食品', 'ファッション', '書籍'];
  const regions = ['関東', '中部', '関西', '九州'];
  const paymentMethods = ['クレジットカード', '電子マネー', '現金'];

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">フィルタ</Typography>
        <Button size="small" onClick={resetFilters}>
          リセット
        </Button>
      </Box>

      {/* 性別フィルタ */}
      <FormControl component="fieldset" sx={{ mb: 3, width: '100%' }}>
        <FormLabel component="legend">性別</FormLabel>
        <RadioGroup
          row
          value={filters.gender}
          onChange={(e) => updateFilter('gender', e.target.value)}
        >
          <FormControlLabel value="all" control={<Radio />} label="すべて" />
          <FormControlLabel value="男性" control={<Radio />} label="男性" />
          <FormControlLabel value="女性" control={<Radio />} label="女性" />
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
    </Paper>
  );
};

export default FilterPanel;

