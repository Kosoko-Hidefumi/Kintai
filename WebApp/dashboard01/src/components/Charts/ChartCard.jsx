import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

const ChartCard = ({ title, children, height = 400 }) => {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ height, mt: 2 }}>
          {children}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ChartCard;

