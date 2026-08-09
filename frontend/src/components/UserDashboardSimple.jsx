import React, { useState } from 'react';
import {
  Container,
  Button,
  TextField,
  Paper,
  Box,
  Typography,
} from '@mui/material';

export default function UserDashboardSimple() {
  const [testValue, setTestValue] = useState('');

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Control Test
        </Typography>

        <TextField
          label="Type something"
          value={testValue}
          onChange={(e) => {
            console.log('Text changed:', e.target.value);
            setTestValue(e.target.value);
          }}
          fullWidth
          sx={{ mb: 2 }}
        />

        <Button
          variant="contained"
          onClick={() => {
            console.log('Button clicked!');
            alert('Button works!');
          }}
          sx={{ mb: 2 }}
        >
          Test Button
        </Button>

        <Box sx={{ mt: 3 }}>
          <Typography>Input value: {testValue}</Typography>
        </Box>
      </Paper>
    </Container>
  );
}
