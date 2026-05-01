#!/usr/bin/env python3
"""
Mock FastAPI Backend Server
Simulates the Society Food Platform API for demo purposes
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_cors_headers()

        if self.path == "/":
            self.send_json_response(200, {
                "message": "Society Food Platform API",
                "version": "1.0.0-alpha.1",
                "docs": "/api/v1/docs",
                "status": "running (mock)"
            })

        elif self.path == "/health":
            self.send_json_response(200, {
                "status": "healthy",
                "service": "backend",
                "mode": "mock"
            })

        elif self.path.startswith("/api/v1/menus"):
            # Mock menu data
            menus = [
                {
                    "id": 1,
                    "seller_id": 1,
                    "name": "Paneer Butter Masala",
                    "description": "Creamy paneer curry with butter",
                    "price": 150.00,
                    "quantity": 8,
                    "category": "veg",
                    "pickup_time": "2024-01-15T20:00:00Z",
                    "is_active": True,
                    "seller": {
                        "id": 1,
                        "name": "Priya Sharma",
                        "flat_number": "A-1205",
                        "rating": 4.8
                    }
                },
                {
                    "id": 2,
                    "seller_id": 2,
                    "name": "Chicken Biryani",
                    "description": "Aromatic basmati rice with tender chicken",
                    "price": 180.00,
                    "quantity": 6,
                    "category": "non-veg",
                    "pickup_time": "2024-01-15T19:30:00Z",
                    "is_active": True,
                    "seller": {
                        "id": 2,
                        "name": "Rajesh Kumar",
                        "flat_number": "A-0803",
                        "rating": 4.9
                    }
                },
                {
                    "id": 3,
                    "seller_id": 3,
                    "name": "Veg Kolhapuri",
                    "description": "Spicy Maharashtrian vegetable curry",
                    "price": 120.00,
                    "quantity": 10,
                    "category": "veg",
                    "pickup_time": "2024-01-15T20:30:00Z",
                    "is_active": True,
                    "seller": {
                        "id": 3,
                        "name": "Anita Desai",
                        "flat_number": "A-1502",
                        "rating": 4.7
                    }
                }
            ]
            self.send_json_response(200, {"menus": menus, "total": len(menus)})

        elif self.path.startswith("/api/v1/orders"):
            # Mock orders data
            orders = [
                {
                    "id": 1,
                    "buyer_id": 4,
                    "menu_item_id": 1,
                    "quantity": 2,
                    "total_price": 300.00,
                    "status": "completed",
                    "ordered_at": "2024-01-14T18:00:00Z",
                    "pickup_confirmed_at": "2024-01-14T20:15:00Z",
                    "menu_item": {
                        "name": "Paneer Butter Masala",
                        "seller": {"name": "Priya Sharma"}
                    }
                }
            ]
            self.send_json_response(200, {"orders": orders, "total": len(orders)})

        else:
            self.send_json_response(404, {"error": "Endpoint not found"})

    def do_POST(self):
        """Handle POST requests"""
        self.send_cors_headers()

        if self.path == "/api/v1/auth/login":
            self.send_json_response(200, {
                "access_token": "mock_jwt_token_12345",
                "refresh_token": "mock_refresh_token_67890",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "name": "Demo User",
                    "flat_number": "A-1001",
                    "is_seller": False
                }
            })

        elif self.path == "/api/v1/orders":
            self.send_json_response(201, {
                "id": 999,
                "message": "Order placed successfully",
                "status": "ordered",
                "estimated_pickup": "2024-01-15T20:00:00Z"
            })

        else:
            self.send_json_response(404, {"error": "Endpoint not found"})

    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json')

    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_cors_headers()
        self.end_headers()

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        if "GET /api/v1/menus" in format or "GET /api/v1/orders" in format:
            return  # Don't log menu/order requests
        super().log_message(format, *args)

def run_server():
    """Run the mock API server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MockAPIHandler)
    print("🚀 Mock FastAPI Backend Server running on http://localhost:8000")
    print("📊 Available endpoints:")
    print("  GET  /                 - API info")
    print("  GET  /health           - Health check")
    print("  GET  /api/v1/menus     - Browse menus")
    print("  GET  /api/v1/orders    - User orders")
    print("  POST /api/v1/auth/login - User login")
    print("  POST /api/v1/orders    - Place order")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Mock server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()