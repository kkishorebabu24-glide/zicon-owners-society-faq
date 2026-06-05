# Real-time Updates Guide

## Overview

The Society App now features **real-time updates** for:
- **Marketplace Listings**: Instantly see new offers/requests as they're posted
- **Matches**: Get notified when someone matches with your listing
- **Digest Delivery**: Receive instant notifications when digests are published

All updates are delivered via **WebSocket** with automatic fallback and reconnection handling.

## Architecture

### Backend Components

#### 1. WebSocket Manager (`backend/app/core/websocket_manager.py`)
Manages all WebSocket connections and Redis pub/sub:

```python
from app.core.websocket_manager import get_connection_manager

manager = get_connection_manager()

# Publish an event to Redis
await manager.publish_event(
    event_type="listing_created",
    data={
        "listing_id": 123,
        "title": "Offer: Furniture",
        "price": 500,
    },
    target_users=[456, 789]  # Optional: specific users
)
```

#### 2. Real-time API Routes

**Marketplace Listings** (`/api/v1/marketplace/`)
- `GET /listings` - List all listings (with filters)
- `POST /listings` - Create new listing (broadcasts `listing_created`)
- `PUT /listings/{id}` - Update listing (broadcasts `listing_updated`)
- `DELETE /listings/{id}` - Close listing (broadcasts `listing_closed`)
- `POST /listings/{id}/matches` - Create match (broadcasts `match_found`)
- `WS /ws/listings` - WebSocket for real-time updates

**Digests** (`/api/v1/digests/`)
- `GET /` - List all digests
- `POST /` - Create new digest
- `PUT /{id}/publish` - Publish digest (broadcasts `digest_published`)
- `PUT /{id}/subscriptions/{sid}/mark-delivered` - Deliver digest (broadcasts `digest_delivered`)

#### 3. Redis Pub/Sub Channels
- `listing_updates`: All listing-related events
- `digest_delivery`: All digest-related events
- `marketplace`: General marketplace activity

### Frontend Components

#### 1. WebSocket Service (`frontend/src/services/websocket.js`)

```javascript
import { webSocketService } from './services/websocket';

// Connect to WebSocket
webSocketService.connect(userId, ['marketplace', 'digest_delivery']);

// Listen to events
webSocketService.on('listing_created', (data) => {
  console.log('New listing:', data);
});

webSocketService.on('match_found', (data) => {
  console.log('Match found:', data);
});

// Manually disconnect
webSocketService.disconnect();
```

#### 2. Redux Store Structure

```javascript
// Store organized by entity type
store.listings  // { items: [], filter: {}, pagination: {} }
store.matches   // { items: [], notifications: [] }
store.digests   // { items: [], unreadCount: 0 }
store.user      // { currentUser: {}, preferences: {} }
store.websocket // { isConnected: bool, error: null, ... }
```

#### 3. Custom Hook: `useWebSocket`

```javascript
import useWebSocket from './hooks/useWebSocket';

function MyComponent() {
  const websocket = useWebSocket(userId, ['marketplace'], true);
  
  return (
    <div>
      Status: {websocket.isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      Error: {websocket.error}
      Reconnect attempts: {websocket.reconnectAttempts}
    </div>
  );
}
```

#### 4. Real-time Components

**ListingsComponent** (`frontend/src/components/ListingsComponent.jsx`)
- Displays marketplace listings
- Filters by type, category, search
- Updates instantly when listings change

**DigestsComponent** (`frontend/src/components/DigestsComponent.jsx`)
- Shows all digests with full content
- Marks as read/unread
- Shows delivery status

**NotificationCenter** (`frontend/src/components/NotificationCenter.jsx`)
- Notification bell with badge count
- Popup showing recent notifications
- Clear all functionality

## Usage Examples

### Backend: Publishing Events

#### Example 1: Create a Listing with Real-time Broadcast

```python
# In demand_supply.py route
@router.post("/listings")
async def create_listing(listing_data: ListingCreate, creator_id: int, db: Session):
    # Create the listing in database
    listing = Listing(...)
    db.add(listing)
    db.commit()
    
    # Broadcast real-time update
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="listing_created",
        data={
            "listing_id": listing.id,
            "type": listing.type.value,
            "title": listing.title,
            "category": listing.category,
            "price": listing.price,
            "creator_id": creator_id,
            "created_at": listing.created_at.isoformat(),
        }
    )
    
    return ListingResponse.model_validate(listing)
```

#### Example 2: Publish a Digest to Specific Users

```python
@router.put("/digests/{digest_id}/publish")
async def publish_digest(digest_id: int, db: Session):
    digest = db.query(Digest).filter(Digest.id == digest_id).first()
    
    # Mark as published
    digest.is_published = True
    digest.published_at = datetime.utcnow()
    db.commit()
    
    # Get subscribed users (e.g., from preferences)
    subscribed_users = [user.id for user in get_subscribed_users(digest)]
    
    # Broadcast to specific users
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="digest_published",
        data={
            "digest_id": digest.id,
            "title": digest.title,
            "published_at": digest.published_at.isoformat(),
        },
        target_users=subscribed_users
    )
    
    return DigestResponse.model_validate(digest)
```

### Frontend: Listening to Events

#### Example 1: Real-time Listing Updates

```javascript
// In App.js or component using useWebSocket hook
const App = () => {
  const dispatch = useDispatch();
  
  // Automatically sets up WebSocket and listeners
  useWebSocket(userId, ['marketplace', 'digest_delivery'], true);
  
  // Redux automatically handles updates via dispatched actions
  const listings = useSelector(state => state.listings.items);
  
  return (
    <div>
      {listings.map(listing => (
        <ListingCard key={listing.id} listing={listing} />
      ))}
    </div>
  );
};
```

#### Example 2: Manual Event Listener

```javascript
import { webSocketService } from './services/websocket';

const MyComponent = () => {
  useEffect(() => {
    // Subscribe to specific event
    const unsubscribe = webSocketService.on('listing_created', (data) => {
      console.log('New listing created:', data);
      // Update local state, show toast, etc.
    });
    
    // Cleanup
    return () => unsubscribe();
  }, []);
  
  return <div>Component content</div>;
};
```

#### Example 3: Check Connection Status

```javascript
const StatusBar = () => {
  const websocket = useSelector(state => state.websocket);
  
  return (
    <div>
      {websocket.isConnected ? (
        <span>🟢 Connected to {websocket.subscribedChannels.join(', ')}</span>
      ) : websocket.isConnecting ? (
        <span>🟡 Connecting... (attempt {websocket.reconnectAttempts})</span>
      ) : (
        <span>🔴 {websocket.error || 'Disconnected'}</span>
      )}
    </div>
  );
};
```

## Event Types Reference

### Listing Events
```javascript
// listing_created
{
  event_type: "listing_created",
  timestamp: "2026-06-04T10:30:00.000Z",
  data: {
    listing_id: 123,
    type: "offer",
    title: "Furniture for Sale",
    category: "furniture",
    price: 500,
    creator_id: 1,
    created_at: "2026-06-04T10:30:00.000Z"
  }
}

// listing_updated
{
  event_type: "listing_updated",
  timestamp: "2026-06-04T10:35:00.000Z",
  data: {
    listing_id: 123,
    updated_fields: {
      title: "Updated Title",
      price: 450,
      status: "active"
    },
    updated_at: "2026-06-04T10:35:00.000Z"
  }
}

// listing_closed
{
  event_type: "listing_closed",
  timestamp: "2026-06-04T10:40:00.000Z",
  data: {
    listing_id: 123,
    status: "cancelled",
    closed_at: "2026-06-04T10:40:00.000Z"
  }
}
```

### Match Events
```javascript
// match_found
{
  event_type: "match_found",
  timestamp: "2026-06-04T10:45:00.000Z",
  data: {
    match_id: 456,
    listing_id: 123,
    user_id: 2,
    match_score: 0.95,
    created_at: "2026-06-04T10:45:00.000Z"
  }
}
```

### Digest Events
```javascript
// digest_published
{
  event_type: "digest_published",
  timestamp: "2026-06-04T07:00:00.000Z",
  data: {
    digest_id: 789,
    title: "Daily Digest - June 4",
    telegram_group_id: 1,
    period_start: "2026-06-03T00:00:00.000Z",
    period_end: "2026-06-04T00:00:00.000Z",
    published_at: "2026-06-04T07:00:00.000Z"
  }
}

// digest_delivered
{
  event_type: "digest_delivered",
  timestamp: "2026-06-04T07:05:00.000Z",
  data: {
    digest_id: 789,
    subscription_id: 999,
    delivery_channel: "email",
    delivered_at: "2026-06-04T07:05:00.000Z"
  }
}
```

## Connection Management

### Automatic Reconnection

The WebSocket service automatically reconnects with exponential backoff:
- Attempt 1: 1 second delay
- Attempt 2: 2 seconds
- Attempt 3: 4 seconds
- Attempt 4: 8 seconds
- Attempt 5: 16 seconds (max 5 attempts)

```javascript
// Connection status with retry info
const websocket = useSelector(state => state.websocket);
console.log(`Reconnection attempt: ${websocket.reconnectAttempts}/${websocket.maxReconnectAttempts}`);
```

### Manual Connection Control

```javascript
import { webSocketService } from './services/websocket';

// Connect
webSocketService.connect(userId, ['marketplace']);

// Check if connected
if (webSocketService.isWebSocketConnected()) {
  console.log('Connected!');
}

// Disconnect
webSocketService.disconnect();

// Reconnect with exponential backoff
webSocketService.reconnectWithBackoff(userId, ['marketplace'], apiUrl, 5);
```

## Scaling

The real-time system scales horizontally using Redis pub/sub:

```
┌─────────────────────────────────────────────────────────┐
│                   Redis Server                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Channels:                                      │    │
│  │  - listing_updates                              │    │
│  │  - digest_delivery                              │    │
│  │  - marketplace                                  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                    ▲         ▲
                    │         │
        Publish  ┌──┴─────────┴──┐  Subscribe
                 │                │
        ┌────────▼───────┐  ┌────▼────────┐
        │  API Server 1  │  │ API Server 2│
        │  ┌──────────┐  │  │ ┌──────────┐│
        │  │WS Client1│  │  │ │WS Client3││
        │  │WS Client2│  │  │ │WS Client4││
        │  └──────────┘  │  │ └──────────┘│
        └────────────────┘  └─────────────┘
```

Multiple API servers can publish to the same Redis channels, and all WebSocket clients across all servers receive the updates.

## Troubleshooting

### WebSocket Connection Fails

1. **Check backend is running**: `curl http://localhost:8000/health`
2. **Check CORS configuration**: Ensure your frontend URL is in `CORS_ORIGINS`
3. **Check Redis is running**: `redis-cli ping` should return `PONG`
4. **Check WebSocket URL**: Should match `ws://localhost:8000/api/v1/marketplace/ws/listings`

### Events Not Received

1. **Check subscribed channels**: `useWebSocket(userId, ['marketplace', 'digest_delivery'])`
2. **Verify events are being published**: Check backend logs for "Published event"
3. **Check Redux state**: `store.websocket.subscribedChannels`

### High Memory Usage

If many WebSocket connections accumulate:
1. Check `ConnectionManager.get_connection_stats()` in logs
2. Ensure client cleanup on disconnect (useWebSocket hook handles this)
3. Monitor Redis memory: `INFO memory`

## Performance Tips

1. **Limit update frequency**: Don't dispatch too many Redux actions
2. **Use Redux selectors**: Prevent unnecessary re-renders
3. **Batch updates**: Group related changes together
4. **Compression**: Backend already uses GZip middleware

## Security Considerations

1. **WebSocket Authentication**: Add user authentication to WebSocket endpoint
2. **Rate Limiting**: Enabled by default (`RATE_LIMIT_ENABLED=true`)
3. **CORS**: Configured for trusted origins only
4. **Message Validation**: All incoming messages validated with Pydantic
5. **Authorization**: Verify user ownership before broadcasting to specific users

## Future Enhancements

- [ ] WebSocket authentication with JWT tokens
- [ ] Message encryption for sensitive data
- [ ] Message persistence queue for offline clients
- [ ] Activity streaming with full audit trail
- [ ] Real-time user presence indicators
- [ ] Typing indicators for collaborative features
