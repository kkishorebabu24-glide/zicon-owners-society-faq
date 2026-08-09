import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Chip, Button, Menu, MenuItem, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import ArticleIcon from '@mui/icons-material/Article';
import NotificationCenter from './components/NotificationCenter';
import SocietyNotifications from './components/SocietyNotifications';
import AuthPage from './components/AuthPage';
import UserDashboard from './components/UserDashboard';
import ListingsComponent from './components/ListingsComponent';
import DigestsComponent from './components/DigestsComponent';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import useWebSocket from './hooks/useWebSocket';

function AppLayout({ children }) {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Initialize WebSocket if authenticated
  const webSocketStatus = useWebSocket(user?.id, ['marketplace', 'digest_delivery'], isAuthenticated);

  const handleMenuOpen = (e) => {
    setAnchorEl(e.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    navigate('/auth');
  };

  const navigationItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { label: 'Marketplace', icon: <ShoppingBagIcon />, path: '/marketplace' },
    { label: 'Digests', icon: <ArticleIcon />, path: '/digests' },
  ];

  const handleNavigate = (path) => {
    navigate(path);
    setDrawerOpen(false);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: '#fafafa' }}>
      {/* App Bar */}
      {isAuthenticated && (
        <AppBar position="static" elevation={1}>
          <Toolbar>
            <Button
              onClick={() => setDrawerOpen(true)}
              sx={{ color: 'white', mr: 2 }}
            >
              <MenuIcon />
            </Button>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              🏘️ Society App
            </Typography>

            {/* WebSocket Status */}
            {webSocketStatus.isConnected ? (
              <Chip
                label="🟢 Online"
                color="success"
                variant="filled"
                size="small"
                sx={{ mr: 2 }}
              />
            ) : (
              <Chip
                label="🔴 Offline"
                color="error"
                variant="outlined"
                size="small"
                sx={{ mr: 2 }}
              />
            )}

            {/* Society Notifications */}
            <SocietyNotifications />

            {/* Notification Center */}
            <NotificationCenter />

            {/* User Menu */}
            <Button
              onClick={handleMenuOpen}
              startIcon={<AccountCircleIcon />}
              sx={{ color: 'white', ml: 2 }}
            >
              {user?.first_name}
            </Button>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleLogout}>
                <LogoutIcon sx={{ mr: 1 }} /> Logout
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
      )}

      {/* Navigation Drawer */}
      {isAuthenticated && (
        <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
          <Box sx={{ width: 280, p: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
              Navigation
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <List>
              {navigationItems.map((item) => (
                <ListItemButton
                  key={item.path}
                  onClick={() => handleNavigate(item.path)}
                  sx={{
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              ))}
            </List>
          </Box>
        </Drawer>
      )}

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {children}
      </Box>
    </Box>
  );
}

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          {/* Auth Routes */}
          <Route path="/auth" element={<PublicRoute element={<AuthPage />} />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={<ProtectedRoute element={<UserDashboard />} />} />
          <Route path="/marketplace" element={<ProtectedRoute element={<ListingsComponent />} />} />
          <Route path="/digests" element={<ProtectedRoute element={<DigestsComponent />} />} />

          {/* Fallback Route */}
          <Route path="/" element={isAuthenticated ? <UserDashboard /> : <AuthPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;

