// Authentication service
// Handles login, registration, token management, and user context

const API_BASE_URL = process.env.REACT_APP_API_URL || '';
const AUTH_STORAGE_KEY = 'auth';

class AuthService {
  constructor() {
    this.token = localStorage.getItem(`${AUTH_STORAGE_KEY}_access_token`);
    this.refreshToken = localStorage.getItem(`${AUTH_STORAGE_KEY}_refresh_token`);
    this.user = JSON.parse(localStorage.getItem(`${AUTH_STORAGE_KEY}_user`) || 'null');
  }

  // ============================================================================
  // AUTHENTICATION ENDPOINTS
  // ============================================================================

  async register(userData) {
    /**
     * Register a new user
     * @param {Object} userData - {firstName, lastName, email, phone, password, bio, address}
     * @returns {Object} - {user_id, email, message}
     */
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: userData.firstName,
          last_name: userData.lastName,
          email: userData.email,
          phone: userData.phone,
          password: userData.password,
          bio: userData.bio || '',
          address: userData.address || '',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async login(email, password) {
    /**
     * Login user and get tokens
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Object} - {access_token, refresh_token, expires_in}
     */
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      this.setTokens(data.access_token, data.refresh_token);
      
      // Fetch and store user info
      await this.fetchCurrentUser();
      
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout() {
    /**
     * Logout user (client-side token deletion)
     */
    try {
      // Call logout endpoint for logging purposes
      await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      }).catch(() => {
        // Ignore errors on logout
      });

      this.clearTokens();
      this.user = null;
      localStorage.removeItem(`${AUTH_STORAGE_KEY}_user`);
    } catch (error) {
      console.error('Logout error:', error);
      this.clearTokens();
    }
  }

  async refreshAccessToken() {
    /**
     * Refresh access token using refresh token
     * @returns {Object} - {access_token, refresh_token, expires_in}
     */
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: this.refreshToken,
        }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      this.setTokens(data.access_token, data.refresh_token);
      return data;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearTokens();
      throw error;
    }
  }

  async fetchCurrentUser() {
    /**
     * Fetch current user information
     * @returns {Object} - User data
     */
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user info');
      }

      const user = await response.json();
      this.user = user;
      localStorage.setItem(`${AUTH_STORAGE_KEY}_user`, JSON.stringify(user));
      return user;
    } catch (error) {
      console.error('Fetch user error:', error);
      throw error;
    }
  }

  // ============================================================================
  // TOKEN MANAGEMENT
  // ============================================================================

  setTokens(accessToken, refreshToken) {
    /**
     * Store tokens in localStorage and memory
     */
    this.token = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem(`${AUTH_STORAGE_KEY}_access_token`, accessToken);
    localStorage.setItem(`${AUTH_STORAGE_KEY}_refresh_token`, refreshToken);
  }

  clearTokens() {
    /**
     * Clear tokens from localStorage and memory
     */
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem(`${AUTH_STORAGE_KEY}_access_token`);
    localStorage.removeItem(`${AUTH_STORAGE_KEY}_refresh_token`);
  }

  getAuthHeaders() {
    /**
     * Get HTTP headers with authorization token
     * @returns {Object} - Headers with Bearer token
     */
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  // ============================================================================
  // STATE CHECKING
  // ============================================================================

  isAuthenticated() {
    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    return !!this.token && !!this.user;
  }

  getCurrentUser() {
    /**
     * Get current user
     * @returns {Object | null}
     */
    return this.user;
  }

  getToken() {
    /**
     * Get access token
     * @returns {string | null}
     */
    return this.token;
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;
