import { writable, derived } from 'svelte/store';
import { authStore } from './auth.js';
import { API_CONFIG, getApiUrl } from './config.js';

const createIssuesStore = () => {
    const { subscribe, set, update } = writable({
        issues: [],
        currentIssue: null,
        loading: false,
        error: null,
        filters: {
            status: '',
            severity: '',
            assignee: '',
            search: ''
        },
        pagination: {
            page: 1,
            limit: 20,
            total: 0,
            totalPages: 0
        }
    });

    const getAuthHeaders = () => authStore.getAuthHeaders();

    return {
        subscribe,

        async loadIssues(page = 1, filters = {}) {
            update(state => ({ ...state, loading: true, error: null }));

            try {
                const params = new URLSearchParams({
                    skip: ((page - 1) * 20).toString(),
                    limit: '20',
                    ...filters
                });

                const response = await fetch(`${getApiUrl(API_CONFIG.endpoints.issues.list)}?${params}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to load issues');
                }

                const data = await response.json();

                update(state => ({
                    ...state,
                    issues: data.issues || [],
                    pagination: {
                        page,
                        limit: 20,
                        total: data.total || 0,
                        totalPages: Math.ceil((data.total || 0) / 20)
                    },
                    loading: false
                }));

            } catch (error) {
                update(state => ({
                    ...state,
                    loading: false,
                    error: error.message
                }));
            }
        },

        async loadIssue(id) {
            update(state => ({ ...state, loading: true, error: null }));

            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.issues.detail(id)), {
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to load issue');
                }

                const issue = await response.json();

                update(state => ({
                    ...state,
                    currentIssue: issue,
                    loading: false
                }));

                return issue;

            } catch (error) {
                update(state => ({
                    ...state,
                    loading: false,
                    error: error.message
                }));
                throw error;
            }
        },

        async createIssue(issueData) {
            try {
                const formData = new FormData();
                
                // Add text fields
                Object.keys(issueData).forEach(key => {
                    if (key !== 'file' && issueData[key] !== null && issueData[key] !== undefined) {
                        formData.append(key, issueData[key]);
                    }
                });

                // Add file if present
                if (issueData.file) {
                    formData.append('file', issueData.file);
                }

                const response = await fetch(getApiUrl(API_CONFIG.endpoints.issues.create), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to create issue' }));
                    throw new Error(errorData.detail || 'Failed to create issue');
                }

                const newIssue = await response.json();

                // Add to the beginning of issues list
                update(state => ({
                    ...state,
                    issues: [newIssue, ...state.issues]
                }));

                return newIssue;

            } catch (error) {
                throw new Error(error.message || 'Failed to create issue');
            }
        },

        async updateIssue(id, updateData) {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.issues.update(id)), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify(updateData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to update issue' }));
                    throw new Error(errorData.detail || 'Failed to update issue');
                }

                const updatedIssue = await response.json();

                // Update in issues list
                update(state => ({
                    ...state,
                    issues: state.issues.map(issue => 
                        issue.id === id ? updatedIssue : issue
                    ),
                    currentIssue: state.currentIssue?.id === id ? updatedIssue : state.currentIssue
                }));

                return updatedIssue;

            } catch (error) {
                throw new Error(error.message || 'Failed to update issue');
            }
        },

        setFilters(filters) {
            update(state => ({
                ...state,
                filters: { ...state.filters, ...filters }
            }));
        },

        clearError() {
            update(state => ({ ...state, error: null }));
        }
    };
};

export const issuesStore = createIssuesStore();

// Derived stores
export const issues = derived(issuesStore, $store => $store.issues);
export const currentIssue = derived(issuesStore, $store => $store.currentIssue);
export const issuesLoading = derived(issuesStore, $store => $store.loading);

