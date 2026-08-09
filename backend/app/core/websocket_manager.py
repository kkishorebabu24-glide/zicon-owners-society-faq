"""
WebSocket Connection Manager for Real-time Updates

Manages WebSocket connections and Redis pub/sub for real-time notifications
on listings, matches, and digest delivery.
"""

import json
import logging
from typing import Dict, Set, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from app.config import settings

try:
    import aioredis
except ImportError:  # Python 3.13+ compatibility
    import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts real-time updates.
    
    Supports multiple connection groups:
    - user_{user_id}: User-specific updates (matches, digests, etc.)
    - listing_updates: All listing changes (new, updated, closed)
    - digest_delivery: Digest publication and delivery events
    - marketplace: Marketplace activity (new offers/requests)
    """

    def __init__(self, redis_url: str = "redis://redis:6379/0"):
        self.redis_url = redis_url
        self.redis: Optional[Any] = None
        
        # Active WebSocket connections grouped by subscription type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "user": {},  # user_{user_id} -> {user_id: {websockets}}
            "listing_updates": set(),
            "digest_delivery": set(),
            "marketplace": set(),
        }
        
        self.pubsub_channels: Dict[str, Any] = {}
        # Maximum allowed concurrent WebSocket connections to protect resources
        try:
            self.max_connections = int(getattr(settings, 'WEBSOCKET_MAX_CONNECTIONS', 500))
        except Exception:
            self.max_connections = 500

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
            logger.info("Redis connection established for WebSocket manager")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None, channels: List[str] = None):
        """
        Accept WebSocket connection and subscribe to channels
        
        Args:
            websocket: WebSocket connection
            user_id: User ID for user-specific updates
            channels: List of channels to subscribe to (user, listing_updates, digest_delivery, marketplace)
        """
        # Accept connection then enforce max-connections limit
        await websocket.accept()
        stats = self.get_connection_stats()
        total_connections = stats.get('total_connections', 0)
        if total_connections >= self.max_connections:
            # Too many connections - politely close with try-again-later code
            logger.warning(f"WebSocket connection refused: too many connections ({total_connections})")
            try:
                await websocket.close(code=1013)
            except Exception:
                pass
            return
        logger.info(f"WebSocket connected - User ID: {user_id}, Channels: {channels}")
        
        if channels is None:
            channels = ["marketplace"]
        
        # Subscribe to user-specific channel if user_id provided
        if user_id:
            user_channel = f"user_{user_id}"
            if user_channel not in self.active_connections["user"]:
                self.active_connections["user"][user_channel] = set()
            self.active_connections["user"][user_channel].add(websocket)
            logger.debug(f"Added connection to {user_channel}")
        
        # Subscribe to requested channels
        for channel in channels:
            if channel in self.active_connections:
                if isinstance(self.active_connections[channel], set):
                    self.active_connections[channel].add(websocket)
                    logger.debug(f"Added connection to {channel}")

    def disconnect(self, websocket: WebSocket, user_id: Optional[int] = None, channels: List[str] = None):
        """
        Remove WebSocket connection from all subscribed channels
        
        Args:
            websocket: WebSocket connection
            user_id: User ID for user-specific updates
            channels: List of channels to unsubscribe from
        """
        if channels is None:
            channels = ["marketplace"]
        
        # Remove from user-specific channel
        if user_id:
            user_channel = f"user_{user_id}"
            if user_channel in self.active_connections["user"]:
                self.active_connections["user"][user_channel].discard(websocket)
                if not self.active_connections["user"][user_channel]:
                    del self.active_connections["user"][user_channel]
                logger.debug(f"Removed connection from {user_channel}")
        
        # Remove from requested channels
        for channel in channels:
            if channel in self.active_connections:
                if isinstance(self.active_connections[channel], set):
                    self.active_connections[channel].discard(websocket)
                    logger.debug(f"Removed connection from {channel}")

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """
        Broadcast message to all connections in a channel
        
        Args:
            channel: Channel name (listing_updates, digest_delivery, marketplace)
            message: Message dictionary to send
        """
        if channel not in self.active_connections:
            logger.warning(f"Unknown channel: {channel}")
            return
        
        connections = self.active_connections[channel]
        if isinstance(connections, set):
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {channel}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected websockets
            for conn in disconnected:
                connections.discard(conn)

    async def broadcast_to_user(self, user_id: int, message: Dict[str, Any]):
        """
        Broadcast message to specific user's connections
        
        Args:
            user_id: User ID
            message: Message dictionary to send
        """
        user_channel = f"user_{user_id}"
        if user_channel not in self.active_connections["user"]:
            logger.debug(f"No active connections for user {user_id}")
            return
        
        connections = self.active_connections["user"][user_channel]
        disconnected = set()
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected websockets
        for conn in disconnected:
            connections.discard(conn)

    async def publish_event(self, event_type: str, data: Dict[str, Any], target_users: List[int] = None):
        """
        Publish event to Redis pub/sub for distribution across instances
        
        Args:
            event_type: Type of event (listing_created, match_found, digest_published, etc.)
            data: Event data
            target_users: List of user IDs to target (if None, broadcast to all)
        """
        if not self.redis:
            logger.warning("Redis not connected, cannot publish event")
            return
        
        payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "target_users": target_users,
        }
        
        try:
            # Publish to specific channel based on event type
            if event_type.startswith("listing_"):
                channel = "listing_updates"
            elif event_type.startswith("digest_"):
                channel = "digest_delivery"
            elif event_type.startswith("match_"):
                channel = "marketplace"
            else:
                channel = "marketplace"
            
            await self.redis.publish(channel, json.dumps(payload))
            logger.debug(f"Published {event_type} to Redis channel {channel}")
        except Exception as e:
            logger.error(f"Error publishing event to Redis: {e}")

    async def subscribe_to_redis(self, channel: str):
        """
        Subscribe to Redis pub/sub channel and relay messages to WebSocket clients
        
        Args:
            channel: Redis channel name
        """
        if not self.redis:
            logger.warning("Redis not connected, cannot subscribe")
            return
        
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            self.pubsub_channels[channel] = pubsub
            logger.info(f"Subscribed to Redis channel: {channel}")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        
                        # Route message to appropriate WebSocket connections
                        if data.get("target_users"):
                            # Send to specific users
                            for user_id in data["target_users"]:
                                await self.broadcast_to_user(user_id, data)
                        else:
                            # Broadcast to all connections in channel
                            await self.broadcast_to_channel(channel, data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode Redis message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")
        except Exception as e:
            logger.error(f"Error in Redis subscription for {channel}: {e}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        stats = {
            "total_connections": 0,
            "by_channel": {},
            "by_user": {},
        }
        
        # Count connections by channel
        for channel, connections in self.active_connections.items():
            if isinstance(connections, set):
                count = len(connections)
                stats["by_channel"][channel] = count
                stats["total_connections"] += count
            elif isinstance(connections, dict):
                count = sum(len(conns) for conns in connections.values())
                stats["by_channel"][channel] = count
                stats["total_connections"] += count
        
        # Count connections by user
        for user_channel, connections in self.active_connections["user"].items():
            user_id = user_channel.replace("user_", "")
            stats["by_user"][user_id] = len(connections)
        
        return stats


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


async def init_connection_manager(redis_url: str = "redis://redis:6379/0"):
    """Initialize the global connection manager"""
    global _connection_manager
    _connection_manager = ConnectionManager(redis_url)
    await _connection_manager.initialize()
    return _connection_manager


async def close_connection_manager():
    """Close the global connection manager"""
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None
