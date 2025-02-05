// index.tsx
import { Box, Paper, useTheme } from '@mui/material';
import { PerformanceMetrics } from '../../components/PerformanceMetrics';

export default function PerformanceCenter() {
  const theme = useTheme();

  return (
    <Box
      sx={{
        bgcolor: theme.palette.mode === 'dark' ? '#030712' : '#fff',
        minHeight: '100vh',
        color: theme.palette.text.primary
      }}
    >
      <Paper
        elevation={0}
        sx={{
          maxWidth: 'lg',
          mx: 'auto',
          p: 0,
          bgcolor: theme.palette.mode === 'dark' ? '#111827' : '#fff',
          borderRadius: 0,
          color: theme.palette.mode === 'dark' ? '#fff' : 'inherit'
        }}
      >
        <PerformanceMetrics />
      </Paper>
    </Box>
  );
}