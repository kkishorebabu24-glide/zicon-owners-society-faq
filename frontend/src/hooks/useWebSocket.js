/**
 * Custom Hook for WebSocket Management
 * 
 * Handles:
 * - WebSocket connection lifecycle
 * - Redux dispatch on events
 * - Automatic reconnection
 */

import { useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { webSocketService } from '../services/websocket';
import {
  connectionOpened,
  connectionClosed,
  connectionError,
  connecting,
  setSubscribedChannels,
  incrementReconnectAttempts,
  resetReconnectAttempts,
} from '../store/slices/websocket';
import {
  listingCreated,
  listingUpdated,
  listingClosed,
} from '../store/slices/listings';
import {
  matchFound,
} from '../store/slices/matches';
import {
  digestPublished,
  digestDelivered,
} from '../store/slices/digests';

/**
 * Hook to connect WebSocket and listen to real-time events
 * @param {number} userId - Current user ID
 * @param {string[]} channels - Channels to subscribe to
 * @param {boolean} enabled - Whether to enable auto-connect
 */
export const useWebSocket = (userId, channels = ['marketplace'], enabled = true) => {
  const dispatch = useDispatch();
  const websocketState = useSelector((state) => state.websocket);
  const unsubscribeCallbacks = useRef([]);

  const handleConnect = useCallback(() => {
    if (!enabled || websocketState.isConnected) return;

    dispatch(connecting());
    try {
      webSocketService.connect(userId, channels);
      dispatch(setSubscribedChannels(channels));
      dispatch(resetReconnectAttempts());
    } catch (error) {
      dispatch(connectionError(error.message));
      dispatch(incrementReconnectAttempts());
    }
  }, [userId, channels, enabled, dispatch, websocketState.isConnected]);

  const handleDisconnect = useCallback(() => {
    webSocketService.disconnect();
    
    // Unsubscribe all listeners
    unsubscribeCallbacks.current.forEach((unsubscribe) => {
      try {
        unsubscribe();
      } catch (e) {
        console.warn('Error unsubscribing:', e);
      }
    });
    unsubscribeCallbacks.current = [];
  }, []);

  const setupEventListeners = useCallback(() => {
    // Connection events
    const unsubConnection = webSocketService.on('connection_opened', () => {
      dispatch(connectionOpened());
    });

    const unsubDisconnection = webSocketService.on('connection_closed', () => {
      dispatch(connectionClosed());
    });

    const unsubError = webSocketService.on('connection_error', (error) => {
      dispatch(connectionError(error.error || 'Unknown error'));
      dispatch(incrementReconnectAttempts());
    });

    // Listing events
    const unsubListingCreated = webSocketService.on('listing_created', (data) => {
      dispatch(listingCreated(data));
    });

    const unsubListingUpdated = webSocketService.on('listing_updated', (data) => {
      dispatch(listingUpdated(data));
    });

    const unsubListingClosed = webSocketService.on('listing_closed', (data) => {
      dispatch(listingClosed(data));
    });

    // Match events
    const unsubMatchFound = webSocketService.on('match_found', (data) => {
      dispatch(matchFound(data));
    });

    // Digest events
    const unsubDigestPublished = webSocketService.on('digest_published', (data) => {
      dispatch(digestPublished(data));
    });

    const unsubDigestDelivered = webSocketService.on('digest_delivered', (data) => {
      dispatch(digestDelivered(data));
    });

    // Store unsubscribe callbacks
    unsubscribeCallbacks.current = [
      unsubConnection,
      unsubDisconnection,
      unsubError,
      unsubListingCreated,
      unsubListingUpdated,
      unsubListingClosed,
      unsubMatchFound,
      unsubDigestPublished,
      unsubDigestDelivered,
    ];
  }, [dispatch]);

  // Connect on mount and setup listeners
  useEffect(() => {
    if (enabled) {
      handleConnect();
      setupEventListeners();
    }

    return () => {
      if (enabled) {
        handleDisconnect();
      }
    };
  }, [enabled, handleConnect, handleDisconnect, setupEventListeners]);

  // Auto-reconnect on connection error
  useEffect(() => {
    if (
      !websocketState.isConnected &&
      !websocketState.isConnecting &&
      websocketState.reconnectAttempts < websocketState.maxReconnectAttempts &&
      enabled
    ) {
      const reconnectDelay = Math.min(1000 * Math.pow(2, websocketState.reconnectAttempts), 30000);
      const timer = setTimeout(handleConnect, reconnectDelay);
      return () => clearTimeout(timer);
    }
  }, [websocketState, enabled, handleConnect]);

  return {
    isConnected: websocketState.isConnected,
    isConnecting: websocketState.isConnecting,
    error: websocketState.error,
    reconnectAttempts: websocketState.reconnectAttempts,
    connect: handleConnect,
    disconnect: handleDisconnect,
  };
};

export default useWebSocket;
