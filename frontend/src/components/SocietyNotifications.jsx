import React, { useState, useEffect } from 'react';
import {
  Box,
  Badge,
  IconButton,
  Popover,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel,
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import { useAuth } from '../context/AuthContext';

export default function SocietyNotifications() {
  const { user, authService } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, unread
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  // Fetch notifications
  const fetchNotifications = async () => {
    if (!authService.isAuthenticated()) return;

    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/notifications?limit=50`,
        {
          headers: authService.getAuthHeaders(),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.items);
        setUnreadCount(data.unread_count);
        setError(null);
      } else if (response.status === 401) {
        // Token invalid, need to reauthenticate
        console.warn('Notification fetch failed: Unauthorized');
      } else {
        setError('Failed to fetch notifications');
      }
    } catch (err) {
      console.error('Notification fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount and set up interval
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval, authService]);

  const handleMarkAsRead = async (notificationId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/notifications/${notificationId}/mark-read`,
        {
          method: 'PUT',
          headers: authService.getAuthHeaders(),
        }
      );

      if (response.ok) {
        // Update local state
        setNotifications((prev) =>
          prev.map((n) =>
            n.id === notificationId ? { ...n, is_read: true } : n
          )
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      }
    } catch (err) {
      console.error('Mark as read error:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/notifications/mark-all-read`,
        {
          method: 'PUT',
          headers: authService.getAuthHeaders(),
        }
      );

      if (response.ok) {
        // Update local state
        setNotifications((prev) =>
          prev.map((n) => ({ ...n, is_read: true }))
        );
        setUnreadCount(0);
      }
    } catch (err) {
      console.error('Mark all as read error:', err);
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/notifications/${notificationId}`,
        {
          method: 'DELETE',
          headers: authService.getAuthHeaders(),
        }
      );

      if (response.ok) {
        // Update local state
        setNotifications((prev) =>
          prev.filter((n) => n.id !== notificationId)
        );
      }
    } catch (err) {
      console.error('Delete notification error:', err);
    }
  };

  const handleOpenPopover = (e) => {
    setAnchorEl(e.currentTarget);
  };

  const handleClosePopover = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  // Get icon based on notification type
  const getNotificationIcon = (notification) => {
    switch (notification.type) {
      case 'listing_match':
      case 'match_found':
        return <CheckCircleIcon sx={{ color: 'success.main' }} />;
      case 'digest_ready':
      case 'digest_published':
        return <InfoIcon sx={{ color: 'info.main' }} />;
      case 'announcement':
        return <NotificationsIcon sx={{ color: 'primary.main' }} />;
      case 'admin_message':
        return <WarningIcon sx={{ color: 'warning.main' }} />;
      default:
        return <InfoIcon />;
    }
  };

  // Sort notifications
  const getSortedNotifications = () => {
    let sorted = [...notifications];
    if (sortBy === 'unread') {
      sorted = sorted.filter((n) => !n.is_read);
    }
    if (sortBy === 'oldest') {
      sorted.reverse();
    }
    return sorted;
  };

  const sortedNotifications = getSortedNotifications();

  return (
    <>
      {/* Notification Bell Icon */}
      <IconButton
        onClick={handleOpenPopover}
        sx={{ position: 'relative' }}
        title="Society Notifications"
      >
        {unreadCount > 0 ? (
          <Badge badgeContent={unreadCount > 9 ? '9+' : unreadCount} color="error">
            <NotificationsActiveIcon sx={{ color: 'primary.main' }} />
          </Badge>
        ) : (
          <NotificationsIcon />
        )}
      </IconButton>

      {/* Notifications Popover */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClosePopover}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            width: '400px',
            maxHeight: '600px',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Notifications
            </Typography>
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </Box>

          {/* Sort Options */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {['newest', 'oldest', 'unread'].map((option) => (
              <Chip
                key={option}
                label={option.charAt(0).toUpperCase() + option.slice(1)}
                onClick={() => setSortBy(option)}
                variant={sortBy === option ? 'filled' : 'outlined'}
                size="small"
              />
            ))}
          </Box>
        </Box>

        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ m: 1 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress size={40} />
          </Box>
        )}

        {/* Notifications List */}
        {!loading && (
          <>
            {sortedNotifications.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <NotificationsIcon sx={{ fontSize: 48, color: 'textSecondary', mb: 1 }} />
                <Typography color="textSecondary">
                  {sortBy === 'unread' ? 'No unread notifications' : 'No notifications yet'}
                </Typography>
              </Box>
            ) : (
              <List sx={{ flex: 1, overflowY: 'auto' }}>
                {sortedNotifications.map((notification, index) => (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      disablePadding
                      secondaryAction={
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {!notification.is_read && (
                            <IconButton
                              edge="end"
                              size="small"
                              onClick={() => handleMarkAsRead(notification.id)}
                              title="Mark as read"
                            >
                              <MarkEmailReadIcon fontSize="small" />
                            </IconButton>
                          )}
                          <IconButton
                            edge="end"
                            size="small"
                            onClick={() => handleDeleteNotification(notification.id)}
                            title="Delete"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemButton
                        sx={{
                          bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                        onClick={() => handleMarkAsRead(notification.id)}
                      >
                        <ListItemIcon>
                          {getNotificationIcon(notification)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: notification.is_read ? 'normal' : 'bold',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {notification.title}
                            </Typography>
                          }
                          secondary={
                            <Typography
                              variant="caption"
                              color="textSecondary"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {notification.message}
                            </Typography>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                    {index < sortedNotifications.length - 1 && (
                      <Divider variant="inset" component="li" />
                    )}
                  </React.Fragment>
                ))}
              </List>
            )}

            {/* Footer Actions */}
            {sortedNotifications.length > 0 && (
              <>
                <Divider />
                <Box sx={{ p: 1.5, display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    fullWidth
                    onClick={handleMarkAllAsRead}
                    disabled={unreadCount === 0}
                  >
                    Mark All as Read
                  </Button>
                  <Button
                    size="small"
                    fullWidth
                    variant="outlined"
                    onClick={handleClosePopover}
                  >
                    Close
                  </Button>
                </Box>
              </>
            )}
          </>
        )}

        {/* Refresh Interval Control */}
        <Box sx={{ p: 1.5, borderTop: '1px solid', borderColor: 'divider', fontSize: '0.75rem' }}>
          <FormControlLabel
            control={
              <Switch
                size="small"
                checked={refreshInterval === 30000}
                onChange={(e) => setRefreshInterval(e.target.checked ? 30000 : 60000)}
              />
            }
            label={`Auto-refresh (${refreshInterval / 1000}s)`}
          />
        </Box>
      </Popover>
    </>
  );
}
