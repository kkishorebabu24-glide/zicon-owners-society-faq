/**
 * Redux Slice for Digests
 * 
 * Manages state for:
 * - Digest delivery notifications
 * - Digest list and content
 * - Read/unread status
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: [],
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
  lastUpdated: null,
};

const digestsSlice = createSlice({
  name: 'digests',
  initialState,
  reducers: {
    // New digest published
    digestPublished: (state, action) => {
      const newDigest = {
        id: action.payload.digest_id,
        title: action.payload.title,
        telegram_group_id: action.payload.telegram_group_id,
        period_start: action.payload.period_start,
        period_end: action.payload.period_end,
        published_at: action.payload.published_at,
        is_read: false,
        delivered_at: null,
      };

      state.items.unshift(newDigest);
      state.unreadCount += 1;

      // Add notification
      state.notifications.push({
        id: `digest_${newDigest.id}`,
        type: 'digest_published',
        title: 'New Digest Available',
        message: `${newDigest.title} is now available`,
        data: newDigest,
        read: false,
        timestamp: new Date().toISOString(),
      });

      state.lastUpdated = new Date().toISOString();
    },

    // Digest delivered to user
    digestDelivered: (state, action) => {
      const { digest_id } = action.payload;
      const digest = state.items.find((item) => item.id === digest_id);

      if (digest) {
        digest.delivered_at = action.payload.delivered_at;

        // Add notification
        state.notifications.push({
          id: `digest_delivered_${digest_id}`,
          type: 'digest_delivered',
          title: 'Digest Delivered',
          message: `${digest.title} has been delivered via ${action.payload.delivery_channel}`,
          data: digest,
          read: false,
          timestamp: new Date().toISOString(),
        });

        state.lastUpdated = new Date().toISOString();
      }
    },

    // Mark digest as read
    markDigestRead: (state, action) => {
      const digest = state.items.find((item) => item.id === action.payload);

      if (digest && !digest.is_read) {
        digest.is_read = true;
        state.unreadCount = Math.max(0, state.unreadCount - 1);
        state.lastUpdated = new Date().toISOString();
      }
    },

    // Set digests from API
    setDigests: (state, action) => {
      state.items = action.payload || [];
      state.unreadCount = state.items.filter((d) => !d.is_read).length;
      state.lastUpdated = new Date().toISOString();
    },

    // Mark notification as read
    markNotificationRead: (state, action) => {
      const notification = state.notifications.find(
        (n) => n.id === action.payload
      );
      if (notification) {
        notification.read = true;
      }
    },

    // Clear notifications
    clearNotifications: (state) => {
      state.notifications = [];
    },

    // Set loading state
    setLoading: (state, action) => {
      state.loading = action.payload;
    },

    // Set error
    setError: (state, action) => {
      state.error = action.payload;
    },

    // Clear error
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  digestPublished,
  digestDelivered,
  markDigestRead,
  setDigests,
  markNotificationRead,
  clearNotifications,
  setLoading,
  setError,
  clearError,
} = digestsSlice.actions;

export default digestsSlice.reducer;
