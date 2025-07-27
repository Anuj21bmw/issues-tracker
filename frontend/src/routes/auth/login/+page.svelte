<!-- Replace: frontend/src/routes/auth/login/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { authStore } from '$lib/stores/auth.js';
    import { toastStore } from '$lib/stores/toast.js';
    import { getApiUrl } from '$lib/config.js';
    
    let email = '';
    let password = '';
    let showPassword = false;
    let showDemoAccounts = false;
    let loading = false;
    let passwordInput;
    
    // Backend connectivity testing
    let backendStatus = 'checking';
    let backendError = null;
    let showBackendTest = false;

    onMount(async () => {
        if ($authStore.isAuthenticated) {
            goto('/dashboard');
        }
        await testBackendConnection();
    });

    async function testBackendConnection() {
        try {
            backendStatus = 'checking';
            const response = await fetch(getApiUrl('/health'));
            if (!response.ok) {
                throw new Error(`Backend not responding (${response.status})`);
            }
            const data = await response.json();
            backendStatus = 'connected';
            backendError = null;
            console.log('Backend health check:', data);
        } catch (err) {
            backendStatus = 'failed';
            backendError = err.message;
            console.error('Backend connection failed:', err);
        }
    }

    async function handleSubmit(event) {
        if (event) event.preventDefault();
        
        if (backendStatus !== 'connected') {
            toastStore.error('Backend is not available. Please check server status.');
            return;
        }
        
        if (!email || !password) {
            toastStore.error('Please fill in all fields');
            return;
        }

        loading = true;
        try {
            const result = await authStore.login(email, password);
            if (!result.success) {
                toastStore.error(result.error || 'Login failed');
            } else {
                toastStore.success('Login successful!');
                // Navigate based on user role
                if (result.user?.role === 'ADMIN' || result.user?.role === 'MAINTAINER') {
                    goto('/dashboard');
                } else {
                    goto('/issues');
                }
            }
        } catch (error) {
            toastStore.error('Login failed: ' + error.message);
        }
        loading = false;
    }

    function quickLogin(role) {
        const accounts = {
            admin: { email: 'admin@example.com', password: 'admin123' },
            maintainer: { email: 'maintainer@example.com', password: 'maintainer123' },
            reporter: { email: 'reporter@example.com', password: 'reporter123' }
        };
        
        const account = accounts[role];
        if (account) {
            email = account.email;
            password = account.password;
            showDemoAccounts = false;
            setTimeout(() => {
                handleSubmit();
            }, 100);
        }
    }

    function toggleDemoAccounts(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        showDemoAccounts = !showDemoAccounts;
    }

    function togglePassword() {
        showPassword = !showPassword;
        if (passwordInput) {
            passwordInput.type = showPassword ? 'text' : 'password';
        }
    }

    function goToRegister() {
        goto('/auth/register');
    }
</script>

<svelte:head>
    <title>Sign In - AI Issues Tracker</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
        <!-- Backend Status Indicator -->
        <div class="text-center mb-4">
            <div class="flex items-center justify-center space-x-2 text-sm">
                <span>Backend Status:</span>
                {#if backendStatus === 'checking'}
                    <span class="text-yellow-600">🔄 Checking...</span>
                {:else if backendStatus === 'connected'}
                    <span class="text-green-600">✅ Connected</span>
                {:else}
                    <span class="text-red-600">❌ Disconnected</span>
                {/if}
                <button 
                    on:click={() => showBackendTest = !showBackendTest}
                    class="text-blue-600 hover:text-blue-800 underline text-xs"
                >
                    Details
                </button>
            </div>
            
            {#if showBackendTest}
                <div class="mt-2 p-3 bg-white rounded border text-sm text-left">
                    <div><strong>API URL:</strong> {getApiUrl('/')}</div>
                    <div><strong>Status:</strong> {backendStatus}</div>
                    {#if backendError}
                        <div class="text-red-600"><strong>Error:</strong> {backendError}</div>
                    {/if}
                    <button 
                        on:click={testBackendConnection}
                        class="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
                    >
                        🔄 Test Again
                    </button>
                </div>
            {/if}
        </div>

        <!-- Logo and Header -->
        <div class="text-center">
            <div class="flex items-center justify-center mb-6">
                <div class="h-12 w-12 bg-gradient-to-br from-blue-600 to-purple-700 rounded-xl flex items-center justify-center mr-3">
                    <svg class="h-7 w-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">AI Issues Tracker</h1>
                    <p class="text-gray-600 text-sm">Smart Issue Management</p>
                </div>
            </div>
            <h2 class="text-3xl font-bold text-gray-900">
                Welcome back
            </h2>
            <p class="mt-2 text-sm text-gray-600">
                Don't have an account? 
                <button 
                    type="button"
                    on:click={goToRegister}
                    class="font-medium text-blue-600 hover:text-blue-500"
                >
                    Create new account
                </button>
            </p>
        </div>

        <!-- Login Form -->
        <form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
            <div class="space-y-4">
                <!-- Email Field -->
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                        Email address
                    </label>
                    <input
                        id="email"
                        type="email"
                        bind:value={email}
                        placeholder="Enter your email"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        required
                    />
                </div>

                <!-- Password Field -->
                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                        Password
                    </label>
                    <div class="relative">
                        <input
                            bind:this={passwordInput}
                            id="password"
                            type="password"
                            bind:value={password}
                            placeholder="Enter your password"
                            class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            required
                        />
                        <button
                            type="button"
                            on:click={togglePassword}
                            class="absolute inset-y-0 right-0 pr-3 flex items-center"
                            aria-label="Toggle password visibility"
                        >
                            <span class="text-gray-400 hover:text-gray-600 text-sm">
                                {showPassword ? '🙈' : '👁️'}
                            </span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Remember me & Demo accounts -->
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <input
                        id="remember-me"
                        type="checkbox"
                        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="remember-me" class="ml-2 block text-sm text-gray-900">
                        Remember me
                    </label>
                </div>

                <button
                    type="button"
                    on:click={toggleDemoAccounts}
                    class="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center cursor-pointer"
                    disabled={backendStatus !== 'connected'}
                >
                    Demo accounts
                    <span class="ml-1 transition-transform duration-200 {showDemoAccounts ? 'rotate-180' : ''}">
                        ⬇️
                    </span>
                </button>
            </div>

            <!-- Demo Accounts Section -->
            {#if showDemoAccounts && backendStatus === 'connected'}
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
                    <h4 class="text-sm font-semibold text-blue-900 mb-3">🎯 Try Demo Accounts:</h4>
                    
                    <button
                        type="button"
                        on:click|preventDefault={() => quickLogin('admin')}
                        class="w-full text-left p-3 bg-white border border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-all group cursor-pointer"
                    >
                        <div class="flex items-center justify-between">
                            <div>
                                <div class="font-medium text-blue-900">👑 Admin User</div>
                                <div class="text-sm text-blue-600">admin@example.com</div>
                            </div>
                            <span class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full font-medium">ADMIN</span>
                        </div>
                    </button>

                    <button
                        type="button"
                        on:click|preventDefault={() => quickLogin('maintainer')}
                        class="w-full text-left p-3 bg-white border border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-all group cursor-pointer"
                    >
                        <div class="flex items-center justify-between">
                            <div>
                                <div class="font-medium text-blue-900">🔧 Maintainer User</div>
                                <div class="text-sm text-blue-600">maintainer@example.com</div>
                            </div>
                            <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full font-medium">MAINTAINER</span>
                        </div>
                    </button>

                    <button
                        type="button"
                        on:click|preventDefault={() => quickLogin('reporter')}
                        class="w-full text-left p-3 bg-white border border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-all group cursor-pointer"
                    >
                        <div class="flex items-center justify-between">
                            <div>
                                <div class="font-medium text-blue-900">📝 Reporter User</div>
                                <div class="text-sm text-blue-600">reporter@example.com</div>
                            </div>
                            <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">REPORTER</span>
                        </div>
                    </button>

                    <p class="text-xs text-blue-600 mt-3 text-center">
                        ✨ Click any demo account to instantly sign in!
                    </p>
                </div>
            {:else if showDemoAccounts && backendStatus !== 'connected'}
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p class="text-sm text-red-700">
                        ⚠️ Demo accounts are not available because the backend is not connected.
                        Please ensure the backend server is running at {getApiUrl('/')}.
                    </p>
                </div>
            {/if}

            <!-- Submit Button -->
            <div>
                <button
                    type="submit"
                    disabled={loading || backendStatus !== 'connected'}
                    class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    {#if loading}
                        <span class="flex items-center">
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Signing in...
                        </span>
                    {:else if backendStatus !== 'connected'}
                        <span class="flex items-center">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                            Backend Disconnected
                        </span>
                    {:else}
                        Sign in
                    {/if}
                </button>
            </div>

            <!-- Backend Connection Help -->
            {#if backendStatus === 'failed'}
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-yellow-800">
                                Backend Connection Issue
                            </h3>
                            <div class="mt-2 text-sm text-yellow-700">
                                <p>The backend server is not responding. To fix this:</p>
                                <ol class="list-decimal list-inside mt-2 space-y-1">
                                    <li>Ensure backend is running: <code class="bg-yellow-100 px-1 rounded">docker-compose up backend</code></li>
                                    <li>Check health endpoint: <a href="{getApiUrl('/health')}" target="_blank" class="underline">{getApiUrl('/health')}</a></li>
                                    <li>Verify database connection in logs</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        </form>
    </div>
</div>