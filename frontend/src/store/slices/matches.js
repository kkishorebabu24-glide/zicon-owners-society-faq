/**
 * Redux Slice for Matches
 * 
 * Manages state for:
 * - Match notifications
 * - User's matches
 * - Match status updates
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: [],
  notifications: [],
  loading: false,
  error: null,
  lastUpdated: null,
};

const matchesSlice = createSlice({
  name: 'matches',
  initialState,
  reducers: {
    // Add a new match (user found a match)
    matchFound: (state, action) => {
      const newMatch = {
        id: action.payload.match_id,
        listing_id: action.payload.listing_id,
        user_id: action.payload.user_id,
        match_score: action.payload.match_score,
        status: 'pending',
        created_at: action.payload.created_at,
      };

      // Add to matches list
      state.items.push(newMatch);

      // Add to notifications
      state.notifications.push({
        id: `match_${newMatch.id}`,
        type: 'match_found',
        title: 'New Match Found!',
        message: `You have a potential match for listing ${action.payload.listing_id}`,
        data: newMatch,
        read: false,
        timestamp: new Date().toISOString(),
      });

      state.lastUpdated = new Date().toISOString();
    },

    // Update match status
    matchStatusUpdated: (state, action) => {
      const { match_id, status } = action.payload;
      const match = state.items.find((item) => item.id === match_id);

      if (match) {
        match.status = status;
        state.lastUpdated = new Date().toISOString();
      }
    },

    // Set matches from API
    setMatches: (state, action) => {
      state.items = action.payload || [];
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
  matchFound,
  matchStatusUpdated,
  setMatches,
  markNotificationRead,
  clearNotifications,
  setLoading,
  setError,
  clearError,
} = matchesSlice.actions;

export default matchesSlice.reducer;
