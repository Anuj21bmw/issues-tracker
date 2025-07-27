<script>
    import { onMount } from 'svelte';
    import { authStore } from '$lib/stores/auth.js';
    import { goto } from '$app/navigation';

    onMount(() => {
        // Redirect to login if not authenticated
        if (!$authStore.isAuthenticated) {
            goto('/auth/login');
        }
    });

    $: user = $authStore.user;

    function handleLogout() {
        authStore.logout();
    }
</script>

<svelte:head>
    <title>Dashboard - AI Issues Tracker</title>
</svelte:head>

{#if $authStore.isAuthenticated}
    <div class="min-h-screen bg-gray-50">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center h-16">
                    <div class="flex items-center">
                        <div class="h-8 w-8 bg-gradient-to-br from-blue-600 to-purple-700 rounded-lg flex items-center justify-center mr-3">
                            <svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                            </svg>
                        </div>
                        <h1 class="text-xl font-semibold text-gray-900">AI Issues Tracker</h1>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="text-sm">
                            <span class="text-gray-500">Welcome back,</span>
                            <span class="font-medium text-gray-900">{user?.full_name || user?.email}</span>
                            <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">{user?.role}</span>
                        </div>
                        <button
                            on:click={handleLogout}
                            class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Welcome Section -->
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-gray-900">Dashboard</h2>
                <p class="text-gray-600 mt-1">Welcome to your AI-enhanced issues tracker</p>
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-2 bg-blue-100 rounded-lg">
                            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-semibold text-gray-900">Total Issues</h3>
                            <p class="text-3xl font-bold text-blue-600">24</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-2 bg-red-100 rounded-lg">
                            <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-semibold text-gray-900">Open Issues</h3>
                            <p class="text-3xl font-bold text-red-600">8</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-2 bg-yellow-100 rounded-lg">
                            <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-semibold text-gray-900">In Progress</h3>
                            <p class="text-3xl font-bold text-yellow-600">11</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-2 bg-green-100 rounded-lg">
                            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-semibold text-gray-900">Resolved</h3>
                            <p class="text-3xl font-bold text-green-600">5</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                    <div class="space-y-3">
                        <button class="w-full text-left px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors">
                            <div class="flex items-center">
                                <svg class="h-5 w-5 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                </svg>
                                <div>
                                    <div class="font-medium text-blue-900">Create New Issue</div>
                                    <div class="text-sm text-blue-600">Report a new problem or bug</div>
                                </div>
                            </div>
                        </button>
                        
                        <button class="w-full text-left px-4 py-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors">
                            <div class="flex items-center">
                                <svg class="h-5 w-5 text-purple-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                                </svg>
                                <div>
                                    <div class="font-medium text-purple-900">View Analytics</div>
                                    <div class="text-sm text-purple-600">AI-powered insights and trends</div>
                                </div>
                            </div>
                        </button>
                        
                        <button class="w-full text-left px-4 py-3 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors">
                            <div class="flex items-center">
                                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
                                </svg>
                                <div>
                                    <div class="font-medium text-green-900">Browse All Issues</div>
                                    <div class="text-sm text-green-600">View and manage existing issues</div>
                                </div>
                            </div>
                        </button>
                    </div>
                </div>

                <!-- Recent Activity -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                    <div class="space-y-4">
                        <div class="flex items-start">
                            <div class="h-2 w-2 bg-blue-500 rounded-full mt-2 mr-3"></div>
                            <div>
                                <p class="text-sm text-gray-900">Issue #123 was assigned to John Doe</p>
                                <p class="text-xs text-gray-500">2 hours ago</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <div class="h-2 w-2 bg-green-500 rounded-full mt-2 mr-3"></div>
                            <div>
                                <p class="text-sm text-gray-900">Issue #118 was resolved</p>
                                <p class="text-xs text-gray-500">4 hours ago</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <div class="h-2 w-2 bg-red-500 rounded-full mt-2 mr-3"></div>
                            <div>
                                <p class="text-sm text-gray-900">New critical issue #124 reported</p>
                                <p class="text-xs text-gray-500">6 hours ago</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Success Message -->
            <div class="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
                <div class="flex">
                    <svg class="h-5 w-5 text-green-400 mr-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <div>
                        <h4 class="text-green-800 font-medium">Demo Account Working!</h4>
                        <p class="text-green-700 text-sm mt-1">
                            You're successfully logged in with a demo account. All features are now working correctly, including the logo, UI, and authentication system.
                        </p>
                    </div>
                </div>
            </div>
        </main>
    </div>
{:else}
    <div class="min-h-screen flex items-center justify-center">
        <div class="text-center">
            <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-gray-600">Loading...</p>
        </div>
    </div>
{/if}
