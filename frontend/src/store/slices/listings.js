/**
 * Redux Slice for Listings (Offers & Requests)
 * 
 * Manages state for marketplace listings including:
 * - All active listings
 * - Filtering and searching
 * - Real-time updates from WebSocket
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: [],
  filter: {
    type: null, // 'offer' or 'request'
    status: 'active',
    category: null,
    searchQuery: '',
  },
  pagination: {
    skip: 0,
    limit: 20,
    total: 0,
  },
  loading: false,
  error: null,
  lastUpdated: null,
};

const listingsSlice = createSlice({
  name: 'listings',
  initialState,
  reducers: {
    // Add a new listing
    listingCreated: (state, action) => {
      const newListing = {
        id: action.payload.listing_id,
        type: action.payload.type,
        title: action.payload.title,
        category: action.payload.category,
        price: action.payload.price,
        creator_id: action.payload.creator_id,
        created_at: action.payload.created_at,
        status: 'active',
        view_count: 0,
        interest_count: 0,
      };
      
      // Add to beginning of list if it matches current filters
      if (
        (!state.filter.type || state.filter.type === newListing.type) &&
        (!state.filter.category || state.filter.category === newListing.category)
      ) {
        state.items.unshift(newListing);
        state.pagination.total += 1;
      }
      state.lastUpdated = new Date().toISOString();
    },

    // Update an existing listing
    listingUpdated: (state, action) => {
      const { listing_id, updated_fields } = action.payload;
      const listing = state.items.find((item) => item.id === listing_id);
      
      if (listing) {
        Object.assign(listing, updated_fields);
        state.lastUpdated = new Date().toISOString();
      }
    },

    // Mark listing as closed/cancelled
    listingClosed: (state, action) => {
      const { listing_id } = action.payload;
      const listing = state.items.find((item) => item.id === listing_id);
      
      if (listing) {
        listing.status = 'cancelled';
        state.lastUpdated = new Date().toISOString();
      }
    },

    // Set listings from API
    setListings: (state, action) => {
      state.items = action.payload.items || [];
      state.pagination = {
        skip: action.payload.skip || 0,
        limit: action.payload.limit || 20,
        total: action.payload.total || 0,
      };
      state.lastUpdated = new Date().toISOString();
    },

    // Update filter
    setFilter: (state, action) => {
      state.filter = { ...state.filter, ...action.payload };
    },

    // Reset pagination
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
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

    // Increment view count
    incrementViewCount: (state, action) => {
      const listing = state.items.find((item) => item.id === action.payload);
      if (listing) {
        listing.view_count += 1;
      }
    },

    // Increment interest count
    incrementInterestCount: (state, action) => {
      const listing = state.items.find((item) => item.id === action.payload);
      if (listing) {
        listing.interest_count += 1;
      }
    },
  },
});

export const {
  listingCreated,
  listingUpdated,
  listingClosed,
  setListings,
  setFilter,
  setPagination,
  setLoading,
  setError,
  clearError,
  incrementViewCount,
  incrementInterestCount,
} = listingsSlice.actions;

export default listingsSlice.reducer;
