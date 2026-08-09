import { useEffect, useState } from 'react';
import webSocketService from '../services/websocket';

export const useWebSocket = (userId, channels = ['marketplace'], enabled = true) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  useEffect(() => {
    if (!enabled || !userId) {
      webSocketService.disconnect();
      setIsConnected(false);
      setIsConnecting(false);
      return;
    }

    setIsConnecting(true);
    setError(null);

    const handleOpen = () => {
      setIsConnected(true);
      setIsConnecting(false);
      setReconnectAttempts(0);
    };

    const handleClose = () => {
      setIsConnected(false);
      setIsConnecting(false);
    };

    const handleError = (payload) => {
      setError(payload?.error || 'WebSocket connection error');
      setIsConnecting(false);
      setReconnectAttempts((prev) => prev + 1);
    };

    const unsubscribeOpen = webSocketService.on('connection_opened', handleOpen);
    const unsubscribeClose = webSocketService.on('connection_closed', handleClose);
    const unsubscribeError = webSocketService.on('connection_error', handleError);

    webSocketService.connect(userId, channels);

    return () => {
      unsubscribeOpen();
      unsubscribeClose();
      unsubscribeError();
      webSocketService.disconnect();
    };
  }, [userId, channels.join(','), enabled]);

  return {
    isConnected,
    isConnecting,
    error,
    reconnectAttempts,
    disconnect: () => webSocketService.disconnect(),
  };
};

export default useWebSocket;
