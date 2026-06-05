import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  Link,
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function AuthPage() {
  const navigate = useNavigate();
  const { login, register, loading, error } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    bio: '',
    address: '',
  });
  const [registerError, setRegisterError] = useState(null);

  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setRegisterData((prev) => ({ ...prev, [name]: value }));
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    const result = await login(loginData.email, loginData.password);
    if (result.success) {
      navigate('/dashboard');
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setRegisterError(null);

    // Validate passwords match
    if (registerData.password !== registerData.confirmPassword) {
      setRegisterError('Passwords do not match');
      return;
    }

    // Validate password length
    if (registerData.password.length < 8) {
      setRegisterError('Password must be at least 8 characters');
      return;
    }

    const result = await register({
      firstName: registerData.firstName,
      lastName: registerData.lastName,
      email: registerData.email,
      phone: registerData.phone,
      password: registerData.password,
      bio: registerData.bio,
      address: registerData.address,
    });

    if (result.success) {
      alert('Registration successful! Please log in.');
      setTabValue(0);
      setLoginData({ email: registerData.email, password: '' });
      setRegisterData({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',
        bio: '',
        address: '',
      });
    } else {
      setRegisterError(result.error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Paper elevation={3} sx={{ width: '100%', p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 2 }}>
              🏘️ Society App
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Connect, Share, and Grow Together
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {registerError && <Alert severity="error" sx={{ mb: 2 }}>{registerError}</Alert>}

          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
          >
            <Tab label="Login" id="auth-tab-0" aria-controls="auth-tabpanel-0" />
            <Tab label="Register" id="auth-tab-1" aria-controls="auth-tabpanel-1" />
          </Tabs>

          {/* LOGIN TAB */}
          <TabPanel value={tabValue} index={0}>
            <form onSubmit={handleLoginSubmit}>
              <TextField
                fullWidth
                name="email"
                type="email"
                label="Email"
                value={loginData.email}
                onChange={handleLoginChange}
                required
                margin="normal"
                disabled={loading}
              />
              <TextField
                fullWidth
                name="password"
                type="password"
                label="Password"
                value={loginData.password}
                onChange={handleLoginChange}
                required
                margin="normal"
                disabled={loading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 3 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Login'}
              </Button>
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="textSecondary">
                  Don't have an account?{' '}
                  <Link
                    component="button"
                    variant="body2"
                    onClick={() => setTabValue(1)}
                  >
                    Register here
                  </Link>
                </Typography>
              </Box>
            </form>
          </TabPanel>

          {/* REGISTER TAB */}
          <TabPanel value={tabValue} index={1}>
            <form onSubmit={handleRegisterSubmit}>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5 }}>
                <TextField
                  name="firstName"
                  label="First Name"
                  value={registerData.firstName}
                  onChange={handleRegisterChange}
                  required
                  disabled={loading}
                  size="small"
                />
                <TextField
                  name="lastName"
                  label="Last Name"
                  value={registerData.lastName}
                  onChange={handleRegisterChange}
                  required
                  disabled={loading}
                  size="small"
                />
              </Box>

              <TextField
                fullWidth
                name="email"
                type="email"
                label="Email"
                value={registerData.email}
                onChange={handleRegisterChange}
                required
                margin="normal"
                disabled={loading}
              />

              <TextField
                fullWidth
                name="phone"
                label="Phone Number"
                value={registerData.phone}
                onChange={handleRegisterChange}
                required
                margin="normal"
                disabled={loading}
                placeholder="+91XXXXXXXXXX"
              />

              <TextField
                fullWidth
                name="password"
                type="password"
                label="Password (min 8 characters)"
                value={registerData.password}
                onChange={handleRegisterChange}
                required
                margin="normal"
                disabled={loading}
              />

              <TextField
                fullWidth
                name="confirmPassword"
                type="password"
                label="Confirm Password"
                value={registerData.confirmPassword}
                onChange={handleRegisterChange}
                required
                margin="normal"
                disabled={loading}
              />

              <TextField
                fullWidth
                name="bio"
                label="Bio (optional)"
                value={registerData.bio}
                onChange={handleRegisterChange}
                margin="normal"
                disabled={loading}
                multiline
                rows={2}
              />

              <TextField
                fullWidth
                name="address"
                label="Address (optional)"
                value={registerData.address}
                onChange={handleRegisterChange}
                margin="normal"
                disabled={loading}
                multiline
                rows={2}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 3 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Register'}
              </Button>

              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="textSecondary">
                  Already have an account?{' '}
                  <Link
                    component="button"
                    variant="body2"
                    onClick={() => setTabValue(0)}
                  >
                    Login here
                  </Link>
                </Typography>
              </Box>
            </form>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
}
