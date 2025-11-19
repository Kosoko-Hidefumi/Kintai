import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Breadcrumbs,
  Link,
  TextField,
  InputAdornment,
  IconButton,
  Badge,
  Container,
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import dayjs from 'dayjs';

const Layout = ({ children }) => {
  const currentDate = dayjs().format('YYYY年MM月DD日');

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="sticky" elevation={0}>
        <Toolbar sx={{ px: { xs: 2, sm: 3 }, py: 1.5 }}>
          <Box sx={{ flexGrow: 1 }}>
            <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 0.5 }}>
              <Link color="inherit" href="#" sx={{ textDecoration: 'none', fontSize: '0.875rem' }}>
                ダッシュボード
              </Link>
              <Typography color="text.primary" sx={{ fontSize: '0.875rem' }}>
                データ分析
              </Typography>
            </Breadcrumbs>
            <Typography variant="h6" component="div" sx={{ fontWeight: 600, fontSize: '1.25rem' }}>
              データ分析ダッシュボード
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <TextField
              size="small"
              placeholder="Search..."
              variant="outlined"
              sx={{
                width: { xs: 150, sm: 200 },
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'background.paper',
                  borderRadius: 2,
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
                  </InputAdornment>
                ),
              }}
            />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 1.5, py: 0.75, borderRadius: 2, bgcolor: 'background.paper' }}>
              <CalendarIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
              <Typography variant="body2" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                {currentDate}
              </Typography>
            </Box>
            <IconButton
              size="small"
              sx={{
                bgcolor: 'background.paper',
                '&:hover': { bgcolor: 'action.hover' },
              }}
            >
              <Badge badgeContent={0} color="error">
                <NotificationsIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
              </Badge>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3, flexGrow: 1 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout;
