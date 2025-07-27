// src/lib/stores/issues.js
import { writable } from 'svelte/store';
import { API_CONFIG, getApiUrl, getAuthHeaders } from '$lib/config.js';

// Issues store
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
            search: '',
            tags: []
        },
        pagination: {
            page: 1,
            pageSize: 20,
            total: 0,
            totalPages: 0
        }
    });

    return {
        subscribe,

        async loadIssues(params = {}) {
            update(state => ({ ...state, loading: true, error: null }));

            try {
                const searchParams = new URLSearchParams();
                
                // Add pagination
                searchParams.append('page', params.page || 1);
                searchParams.append('page_size', params.pageSize || 20);

                // Add filters
                if (params.status) searchParams.append('status', params.status);
                if (params.severity) searchParams.append('severity', params.severity);
                if (params.assignee) searchParams.append('assignee_id', params.assignee);
                if (params.search) searchParams.append('search', params.search);
                if (params.tags?.length) {
                    params.tags.forEach(tag => searchParams.append('tags', tag));
                }

                const response = await fetch(`${getApiUrl(API_CONFIG.endpoints.issues.list)}?${searchParams}`, {
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
                    issues: data.items || data,
                    pagination: {
                        page: data.page || 1,
                        pageSize: data.page_size || 20,
                        total: data.total || data.length,
                        totalPages: data.total_pages || Math.ceil((data.total || data.length) / (data.page_size || 20))
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
                    headers: {
                        ...getAuthHeaders()
                        // Don't set Content-Type for FormData
                    },
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to create issue' }));
                    throw new Error(errorData.detail || 'Failed to create issue');
                }

                const newIssue = await response.json();

                // Add to issues list
                update(state => ({
                    ...state,
                    issues: [newIssue, ...state.issues]
                }));

                return newIssue;

            } catch (error) {
                throw error;
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

                // Update in issues list and current issue
                update(state => ({
                    ...state,
                    issues: state.issues.map(issue => 
                        issue.id === id ? updatedIssue : issue
                    ),
                    currentIssue: state.currentIssue?.id === id ? updatedIssue : state.currentIssue
                }));

                return updatedIssue;

            } catch (error) {
                throw error;
            }
        },

        async deleteIssue(id) {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.issues.delete(id)), {
                    method: 'DELETE',
                    headers: {
                        ...getAuthHeaders()
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to delete issue' }));
                    throw new Error(errorData.detail || 'Failed to delete issue');
                }

                // Remove from issues list
                update(state => ({
                    ...state,
                    issues: state.issues.filter(issue => issue.id !== id),
                    currentIssue: state.currentIssue?.id === id ? null : state.currentIssue
                }));

            } catch (error) {
                throw error;
            }
        },

        updateFilters(newFilters) {
            update(state => ({
                ...state,
                filters: { ...state.filters, ...newFilters }
            }));
        },

        clearFilters() {
            update(state => ({
                ...state,
                filters: {
                    status: '',
                    severity: '',
                    assignee: '',
                    search: '',
                    tags: []
                }
            }));
        },

        clearError() {
            update(state => ({ ...state, error: null }));
        },

        setCurrentIssue(issue) {
            update(state => ({ ...state, currentIssue: issue }));
        },

        clearCurrentIssue() {
            update(state => ({ ...state, currentIssue: null }));
        }
    };
};

export const issuesStore = createIssuesStore();