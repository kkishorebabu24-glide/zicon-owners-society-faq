/**
 * WebSocket Service for Real-time Updates
 * 
 * Handles connection, subscription, and event listening for:
 * - Listing updates (new, modified, closed offers/requests)
 * - Match notifications (when matches are found)
 * - Digest delivery (new digest published or delivered)
 */

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = {
      listing_created: [],
      listing_updated: [],
      listing_closed: [],
      match_found: [],
      digest_published: [],
      digest_delivered: [],
      connection_opened: [],
      connection_closed: [],
      connection_error: [],
    };
  }

  /**
   * Initialize WebSocket connection
   * @param {number} userId - Current user ID
   * @param {string[]} channels - Channels to subscribe to
   * @param {string} apiUrl - API base URL (default: http://localhost:8000)
   */
  connect(userId, channels = ['marketplace'], apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000') {
    if (this.isConnected) {
      console.warn('WebSocket already connected');
      return;
    }

    const wsUrl = apiUrl.replace(/^http/, 'ws');
    const channelParam = channels.join(',');
    const url = `${wsUrl}/api/v1/marketplace/ws/listings?user_id=${userId}&channels=${channelParam}`;

    console.log(`Connecting to WebSocket: ${url}`);

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.isConnected = true;
      console.log('WebSocket connected');
      this.emit('connection_opened', { timestamp: new Date() });
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error, event.data);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('connection_error', { error: error.message || 'WebSocket error' });
    };

    this.socket.onclose = () => {
      this.isConnected = false;
      console.log('WebSocket disconnected');
      this.emit('connection_closed', { timestamp: new Date() });
    };
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }

  /**
   * Handle incoming WebSocket messages
   * @private
   */
  handleMessage(message) {
    const { event_type, data, timestamp } = message;

    console.log(`Received event: ${event_type}`, data);

    switch (event_type) {
      case 'listing_created':
        this.emit('listing_created', { ...data, received_at: timestamp });
        break;

      case 'listing_updated':
        this.emit('listing_updated', { ...data, received_at: timestamp });
        break;

      case 'listing_closed':
        this.emit('listing_closed', { ...data, received_at: timestamp });
        break;

      case 'match_found':
        this.emit('match_found', { ...data, received_at: timestamp });
        break;

      case 'digest_published':
        this.emit('digest_published', { ...data, received_at: timestamp });
        break;

      case 'digest_delivered':
        this.emit('digest_delivered', { ...data, received_at: timestamp });
        break;

      default:
        console.warn(`Unknown event type: ${event_type}`);
    }
  }

  /**
   * Subscribe to an event
   * @param {string} eventType - Event type to subscribe to
   * @param {Function} callback - Callback function
   */
  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = [];
    }
    this.listeners[eventType].push(callback);

    // Return unsubscribe function
    return () => {
      this.off(eventType, callback);
    };
  }

  /**
   * Unsubscribe from an event
   * @param {string} eventType - Event type to unsubscribe from
   * @param {Function} callback - Callback function
   */
  off(eventType, callback) {
    if (this.listeners[eventType]) {
      this.listeners[eventType] = this.listeners[eventType].filter(
        (cb) => cb !== callback
      );
    }
  }

  /**
   * Emit an event to all listeners
   * @private
   */
  emit(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for ${eventType}:`, error);
        }
      });
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isWebSocketConnected() {
    return this.isConnected && this.socket && this.socket.readyState === WebSocket.OPEN;
  }

  /**
   * Send a message through WebSocket
   * @param {Object} message - Message to send
   */
  send(message) {
    if (this.isWebSocketConnected()) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  /**
   * Reconnect with exponential backoff
   */
  reconnectWithBackoff(userId, channels, apiUrl, maxAttempts = 5) {
    let attempts = 0;

    const attemptConnect = () => {
      attempts++;
      console.log(`Reconnection attempt ${attempts}/${maxAttempts}`);

      try {
        this.connect(userId, channels, apiUrl);

        if (this.isWebSocketConnected()) {
          console.log('Reconnection successful');
          return;
        }
      } catch (error) {
        console.error('Reconnection failed:', error);
      }

      if (attempts < maxAttempts) {
        const delay = Math.min(1000 * Math.pow(2, attempts - 1), 30000); // Exponential backoff, max 30s
        console.log(`Retrying in ${delay}ms...`);
        setTimeout(attemptConnect, delay);
      } else {
        console.error('Max reconnection attempts reached');
      }
    };

    attemptConnect();
  }
}

// Create a singleton instance
export const webSocketService = new WebSocketService();

export default WebSocketService;
