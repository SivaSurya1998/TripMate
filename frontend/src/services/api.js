import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// =============================================================================
// PACKING LIST API
// =============================================================================

export const packingListAPI = {
  // Get all trip types
  getTripTypes: async () => {
    const response = await apiClient.get('/trip-types');
    return response.data;
  },

  // Get specific trip type
  getTripType: async (tripId) => {
    const response = await apiClient.get(`/trip-types/${tripId}`);
    return response.data;
  },

  // Add item to trip type
  addItem: async (tripId, item) => {
    const response = await apiClient.post(`/trip-types/${tripId}/items`, item);
    return response.data;
  },

  // Update item (toggle packed status)
  updateItem: async (tripId, itemId, packed) => {
    const response = await apiClient.put(`/trip-types/${tripId}/items/${itemId}`, { packed });
    return response.data;
  },

  // Delete item
  deleteItem: async (tripId, itemId) => {
    const response = await apiClient.delete(`/trip-types/${tripId}/items/${itemId}`);
    return response.data;
  },
};

// =============================================================================
// ITINERARY API
// =============================================================================

export const itineraryAPI = {
  // Get all events
  getEvents: async () => {
    const response = await apiClient.get('/events');
    return response.data;
  },

  // Create new event
  createEvent: async (event) => {
    const response = await apiClient.post('/events', event);
    return response.data;
  },

  // Update event
  updateEvent: async (eventId, event) => {
    const response = await apiClient.put(`/events/${eventId}`, event);
    return response.data;
  },

  // Delete event
  deleteEvent: async (eventId) => {
    const response = await apiClient.delete(`/events/${eventId}`);
    return response.data;
  },
};

// =============================================================================
// CURRENCY CONVERTER API
// =============================================================================

export const currencyAPI = {
  // Get supported currencies
  getCurrencies: async () => {
    const response = await apiClient.get('/currencies');
    return response.data;
  },

  // Get exchange rates
  getExchangeRates: async () => {
    const response = await apiClient.get('/exchange-rates');
    return response.data;
  },

  // Convert currency
  convertCurrency: async (amount, fromCurrency, toCurrency) => {
    const response = await apiClient.post('/convert', {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency,
    });
    return response.data;
  },

  // Update exchange rate
  updateExchangeRate: async (fromCurrency, toCurrency, rate) => {
    const response = await apiClient.put(`/exchange-rates/${fromCurrency}/${toCurrency}`, { rate });
    return response.data;
  },
};

// =============================================================================
// GENERAL API
// =============================================================================

export const generalAPI = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/');
    return response.data;
  },
};

export default apiClient;