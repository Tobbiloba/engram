/**
 * API Client module for frontend
 * Handles all HTTP requests to the backend
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:3000/api';

/**
 * Generic fetch wrapper with error handling
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise<any>} - Response data
 */
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'API request failed');
    }

    return response.json();
}

/**
 * Authentication API methods
 */
export const authAPI = {
    async login(username, password) {
        const data = await fetchAPI('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        localStorage.setItem('authToken', data.token);
        return data;
    },

    async logout() {
        await fetchAPI('/auth/logout', { method: 'POST' });
        localStorage.removeItem('authToken');
    },

    async getCurrentUser() {
        return fetchAPI('/auth/me');
    },
};

/**
 * Posts API methods
 */
export const postsAPI = {
    async getAll() {
        return fetchAPI('/posts');
    },

    async getById(id) {
        return fetchAPI(`/posts/${id}`);
    },

    async create(title, content) {
        return fetchAPI('/posts', {
            method: 'POST',
            body: JSON.stringify({ title, content }),
        });
    },

    async update(id, title, content) {
        return fetchAPI(`/posts/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ title, content }),
        });
    },

    async delete(id) {
        return fetchAPI(`/posts/${id}`, { method: 'DELETE' });
    },
};
