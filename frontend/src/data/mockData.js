// Mock data for TripMate app - this will be replaced with backend integration later

export const tripTypes = [
  {
    id: 'beach',
    name: 'Beach Getaway',
    icon: '🏖️',
    color: 'from-blue-400 to-cyan-300',
    items: [
      { id: 1, name: 'Sunscreen SPF 50+', category: 'essentials', packed: false },
      { id: 2, name: 'Swimwear', category: 'clothing', packed: true },
      { id: 3, name: 'Beach towel', category: 'essentials', packed: false },
      { id: 4, name: 'Flip flops', category: 'footwear', packed: false },
      { id: 5, name: 'Sunglasses', category: 'accessories', packed: true },
      { id: 6, name: 'Beach hat', category: 'accessories', packed: false },
      { id: 7, name: 'Water bottle', category: 'essentials', packed: false },
    ]
  },
  {
    id: 'city',
    name: 'City Explorer',
    icon: '🏙️',
    color: 'from-purple-400 to-pink-300',
    items: [
      { id: 8, name: 'Comfortable walking shoes', category: 'footwear', packed: false },
      { id: 9, name: 'Portable charger', category: 'electronics', packed: true },
      { id: 10, name: 'Day backpack', category: 'accessories', packed: false },
      { id: 11, name: 'City map/guidebook', category: 'essentials', packed: false },
      { id: 12, name: 'Camera', category: 'electronics', packed: true },
      { id: 13, name: 'Light jacket', category: 'clothing', packed: false },
      { id: 14, name: 'Reusable water bottle', category: 'essentials', packed: false },
    ]
  },
  {
    id: 'business',
    name: 'Business Trip',
    icon: '💼',
    color: 'from-gray-400 to-slate-300',
    items: [
      { id: 15, name: 'Business cards', category: 'essentials', packed: false },
      { id: 16, name: 'Laptop + charger', category: 'electronics', packed: true },
      { id: 17, name: 'Professional attire', category: 'clothing', packed: false },
      { id: 18, name: 'Dress shoes', category: 'footwear', packed: false },
      { id: 19, name: 'Portfolio/documents', category: 'essentials', packed: false },
      { id: 20, name: 'Phone charger', category: 'electronics', packed: true },
      { id: 21, name: 'Travel adapter', category: 'electronics', packed: false },
    ]
  }
];

export const mockItinerary = [
  {
    id: 1,
    title: 'Flight Departure',
    date: '2025-07-15',
    time: '08:30',
    location: 'John F. Kennedy Airport, Terminal 4',
    description: 'Flight AA123 to Los Angeles',
    type: 'flight',
    icon: '✈️'
  },
  {
    id: 2,
    title: 'Hotel Check-in',
    date: '2025-07-15',
    time: '15:00',
    location: 'Beverly Hills Hotel, 9641 Sunset Blvd',
    description: 'Reservation #BH789456, Premium Suite',
    type: 'accommodation',
    icon: '🏨'
  },
  {
    id: 3,
    title: 'Dinner Reservation',
    date: '2025-07-15',
    time: '19:30',
    location: 'Nobu Malibu, 22706 Pacific Coast Hwy',
    description: 'Table for 2, confirmed reservation',
    type: 'dining',
    icon: '🍽️'
  },
  {
    id: 4,
    title: 'Beach Day',
    date: '2025-07-16',
    time: '10:00',
    location: 'Santa Monica Beach',
    description: 'Relaxing day at the beach, rent bikes for pier ride',
    type: 'activity',
    icon: '🏖️'
  },
  {
    id: 5,
    title: 'Return Flight',
    date: '2025-07-18',
    time: '16:45',
    location: 'Los Angeles International Airport, Terminal 6',
    description: 'Flight AA456 back to New York',
    type: 'flight',
    icon: '✈️'
  }
];

export const exchangeRates = {
  'USD_EUR': { rate: 0.85, lastUpdated: '2025-07-10' },
  'USD_GBP': { rate: 0.73, lastUpdated: '2025-07-10' },
  'USD_JPY': { rate: 110.25, lastUpdated: '2025-07-10' },
  'EUR_USD': { rate: 1.18, lastUpdated: '2025-07-10' },
  'GBP_USD': { rate: 1.37, lastUpdated: '2025-07-10' },
  'JPY_USD': { rate: 0.0091, lastUpdated: '2025-07-10' }
};

export const currencies = [
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' }
];