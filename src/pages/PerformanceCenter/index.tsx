// index.tsx
import { Box, Paper, useTheme } from '@mui/material';
import { PerformanceMetrics } from '../../components/PerformanceMetrics';

export default function PerformanceCenter() {
  const theme = useTheme();

  return (
    <Box
      sx={{
        bgcolor: theme.palette.mode === 'dark' ? 'background.default' : '#fff',
        minHeight: '100vh',
        color: theme.palette.text.primary
      }}
    >
      <Paper
        elevation={0}
        sx={{
          maxWidth: 'lg',
          mx: 'auto',
          p: 3,
          bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : '#fff',
          borderRadius: 2
        }}
      >
        <PerformanceMetrics />
      </Paper>
    </Box>
  );
}