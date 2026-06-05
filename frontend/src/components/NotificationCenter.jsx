/**
 * Real-time Notifications Component
 * 
 * Displays notifications for:
 * - New listings created
 * - Matches found
 * - Digests published and delivered
 */

import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Badge,
  IconButton,
  Popover,
  List,
  ListItem,
  ListItemText,
  Typography,
  Button,
  Chip,
  Stack,
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import CloseIcon from '@mui/icons-material/Close';
import { markNotificationRead, clearNotifications } from '../store/slices/matches';

const NotificationCenter = () => {
  const dispatch = useDispatch();
  const [anchorEl, setAnchorEl] = useState(null);

  // Get notifications from all slices
  const matchNotifications = useSelector((state) => state.matches.notifications || []);
  const digestNotifications = useSelector((state) => state.digests.notifications || []);
  
  const allNotifications = [...matchNotifications, ...digestNotifications].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  const unreadCount = allNotifications.filter((n) => !n.read).length;

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMarkRead = (notificationId) => {
    dispatch(markNotificationRead(notificationId));
  };

  const handleClearAll = () => {
    dispatch(clearNotifications());
  };

  const open = Boolean(anchorEl);

  const getNotificationColor = (type) => {
    switch (type) {
      case 'match_found':
        return 'info';
      case 'digest_published':
        return 'success';
      case 'digest_delivered':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <>
      <IconButton
        onClick={handleClick}
        color="inherit"
        aria-label="notifications"
      >
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ width: 400, maxHeight: 500, overflow: 'auto' }}>
          <Box sx={{ p: 2, borderBottom: '1px solid #eee' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">Notifications</Typography>
              {allNotifications.length > 0 && (
                <Button
                  size="small"
                  onClick={handleClearAll}
                  variant="text"
                >
                  Clear All
                </Button>
              )}
            </Stack>
          </Box>

          {allNotifications.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="textSecondary">
                No notifications yet
              </Typography>
            </Box>
          ) : (
            <List disablePadding>
              {allNotifications.map((notification) => (
                <ListItem
                  key={notification.id}
                  sx={{
                    bgcolor: notification.read ? 'transparent' : '#f5f5f5',
                    borderBottom: '1px solid #eee',
                    '&:hover': {
                      bgcolor: notification.read ? '#fafafa' : '#ebebeb',
                    },
                  }}
                >
                  <ListItemText
                    primary={
                      <Stack direction="row" alignItems="center" gap={1}>
                        <Typography variant="body2" fontWeight="bold">
                          {notification.title}
                        </Typography>
                        <Chip
                          label={notification.type.replace('_', ' ')}
                          size="small"
                          color={getNotificationColor(notification.type)}
                          variant="outlined"
                        />
                      </Stack>
                    }
                    secondary={
                      <>
                        <Typography variant="body2" color="textSecondary">
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {new Date(notification.timestamp).toLocaleString()}
                        </Typography>
                      </>
                    }
                  />
                  {!notification.read && (
                    <IconButton
                      size="small"
                      onClick={() => handleMarkRead(notification.id)}
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  )}
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Popover>
    </>
  );
};

export default NotificationCenter;
