/**
 * Redux Slice for WebSocket Connection State
 * 
 * Manages state for:
 * - WebSocket connection status
 * - Connection errors
 * - Subscribed channels
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isConnected: false,
  isConnecting: false,
  error: null,
  lastConnectionTime: null,
  lastDisconnectionTime: null,
  subscribedChannels: [],
  reconnectAttempts: 0,
  maxReconnectAttempts: 5,
};

const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    // Connection established
    connectionOpened: (state) => {
      state.isConnected = true;
      state.isConnecting = false;
      state.error = null;
      state.lastConnectionTime = new Date().toISOString();
      state.reconnectAttempts = 0;
    },

    // Connection closed
    connectionClosed: (state) => {
      state.isConnected = false;
      state.lastDisconnectionTime = new Date().toISOString();
    },

    // Connection error
    connectionError: (state, action) => {
      state.error = action.payload;
      state.isConnected = false;
      state.isConnecting = false;
    },

    // Start connecting
    connecting: (state) => {
      state.isConnecting = true;
      state.error = null;
    },

    // Update subscribed channels
    setSubscribedChannels: (state, action) => {
      state.subscribedChannels = action.payload;
    },

    // Increment reconnect attempts
    incrementReconnectAttempts: (state) => {
      state.reconnectAttempts = Math.min(
        state.reconnectAttempts + 1,
        state.maxReconnectAttempts
      );
    },

    // Reset reconnect attempts
    resetReconnectAttempts: (state) => {
      state.reconnectAttempts = 0;
    },

    // Clear error
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  connectionOpened,
  connectionClosed,
  connectionError,
  connecting,
  setSubscribedChannels,
  incrementReconnectAttempts,
  resetReconnectAttempts,
  clearError,
} = websocketSlice.actions;

export default websocketSlice.reducer;
