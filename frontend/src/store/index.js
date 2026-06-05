/**
 * Redux Store Configuration
 * 
 * Manages global state including:
 * - Real-time listings (offers and requests)
 * - Matches and notifications
 * - Digests and delivery status
 * - User preferences
 */

import { configureStore } from '@reduxjs/toolkit';
import listingsReducer from './slices/listings';
import matchesReducer from './slices/matches';
import digestsReducer from './slices/digests';
import userReducer from './slices/user';
import websocketReducer from './slices/websocket';

export const store = configureStore({
  reducer: {
    listings: listingsReducer,
    matches: matchesReducer,
    digests: digestsReducer,
    user: userReducer,
    websocket: websocketReducer,
  },
});

export default store;
