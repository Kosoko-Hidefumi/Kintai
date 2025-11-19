import React, { createContext, useContext, useState, useCallback } from 'react';

const FilterContext = createContext();

export const useFilter = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilter must be used within FilterProvider');
  }
  return context;
};

const initialFilters = {
  gender: 'all',
  region: 'all',
  categories: [],
  paymentMethods: [],
  ageRange: [18, 75], // データの範囲に合わせて調整
  amountRange: [0, 70000], // データの範囲に合わせて調整
  dateRange: {
    start: null,
    end: null,
  },
};

export const FilterProvider = ({ children }) => {
  const [filters, setFilters] = useState(initialFilters);

  const updateFilter = useCallback((key, value) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, []);

  const value = {
    filters,
    updateFilter,
    resetFilters,
  };

  return (
    <FilterContext.Provider value={value}>
      {children}
    </FilterContext.Provider>
  );
};

