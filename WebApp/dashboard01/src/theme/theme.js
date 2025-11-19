import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#e33371',
      dark: '#9a0036',
    },
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
    },
    error: {
      main: '#d32f2f',
      light: '#ef5350',
      dark: '#c62828',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Helvetica',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.2,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.3,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '0.875rem',
    },
    body2: {
      fontSize: '0.75rem',
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 1px 3px rgba(0, 0, 0, 0.08)',
    '0px 2px 6px rgba(0, 0, 0, 0.08)',
    '0px 4px 12px rgba(0, 0, 0, 0.08)',
    '0px 8px 24px rgba(0, 0, 0, 0.08)',
    '0px 12px 32px rgba(0, 0, 0, 0.08)',
    '0px 16px 40px rgba(0, 0, 0, 0.08)',
    '0px 20px 48px rgba(0, 0, 0, 0.08)',
    '0px 24px 56px rgba(0, 0, 0, 0.08)',
    '0px 28px 64px rgba(0, 0, 0, 0.08)',
    '0px 32px 72px rgba(0, 0, 0, 0.08)',
    '0px 36px 80px rgba(0, 0, 0, 0.08)',
    '0px 40px 88px rgba(0, 0, 0, 0.08)',
    '0px 44px 96px rgba(0, 0, 0, 0.08)',
    '0px 48px 104px rgba(0, 0, 0, 0.08)',
    '0px 52px 112px rgba(0, 0, 0, 0.08)',
    '0px 56px 120px rgba(0, 0, 0, 0.08)',
    '0px 60px 128px rgba(0, 0, 0, 0.08)',
    '0px 64px 136px rgba(0, 0, 0, 0.08)',
    '0px 68px 144px rgba(0, 0, 0, 0.08)',
    '0px 72px 152px rgba(0, 0, 0, 0.08)',
    '0px 76px 160px rgba(0, 0, 0, 0.08)',
    '0px 80px 168px rgba(0, 0, 0, 0.08)',
    '0px 84px 176px rgba(0, 0, 0, 0.08)',
  ],
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.08)',
          borderRadius: 12,
          border: '1px solid rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: 'rgba(0, 0, 0, 0.87)',
          boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
  },
});

export default theme;

