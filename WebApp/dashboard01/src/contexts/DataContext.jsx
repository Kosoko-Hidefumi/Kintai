import React, { createContext, useContext, useState, useCallback } from 'react';

const DataContext = createContext();

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [rawData, setRawData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadData = useCallback((data) => {
    setRawData(data);
    setFilteredData(data);
    setError(null);
  }, []);

  const updateFilteredData = useCallback((data) => {
    setFilteredData(data);
  }, []);

  const setLoadingState = useCallback((isLoading) => {
    setLoading(isLoading);
  }, []);

  const setErrorState = useCallback((errorMessage) => {
    setError(errorMessage);
  }, []);

  const value = {
    rawData,
    filteredData,
    loading,
    error,
    loadData,
    updateFilteredData,
    setLoadingState,
    setErrorState,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};

