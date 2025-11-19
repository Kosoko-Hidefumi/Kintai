import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

const ChartCard = ({ title, children, height = 400, subtitle }) => {
  return (
    <Card sx={{ height: '100%', transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { boxShadow: 4 } }}>
      <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.125rem', mb: 0.5 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box sx={{ height, mt: 1, flexGrow: 1 }}>
          {children}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ChartCard;

