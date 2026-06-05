/**
 * Redux Slice for User
 * 
 * Manages state for:
 * - Current user information
 * - User preferences
 * - Authentication state
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  currentUser: null,
  isAuthenticated: false,
  preferences: {
    digestFrequency: 'daily',
    receiveNotifications: true,
    notificationChannels: {
      email: true,
      telegram: false,
      sms: false,
    },
  },
  loading: false,
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    // Set current user
    setCurrentUser: (state, action) => {
      state.currentUser = action.payload;
      state.isAuthenticated = !!action.payload;
    },

    // Update preferences
    updatePreferences: (state, action) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },

    // Logout
    logout: (state) => {
      state.currentUser = null;
      state.isAuthenticated = false;
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
  setCurrentUser,
  updatePreferences,
  logout,
  setLoading,
  setError,
  clearError,
} = userSlice.actions;

export default userSlice.reducer;
