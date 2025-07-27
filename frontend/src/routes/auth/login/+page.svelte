<!-- src/routes/auth/login/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { authStore } from '$lib/stores/auth.js';
    import { toastStore } from '$lib/stores/toast.js';
    
    let email = '';
    let password = '';
    let showPassword = false;
    let showDemoAccounts = false;
    let loading = false;
    let passwordInput;

    onMount(() => {
        if ($authStore.isAuthenticated) {
            goto('/dashboard');
        }
    });

    async function handleSubmit(event) {
        if (event) event.preventDefault();
        
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

    function handleKeydown(event) {
        if (event.key === 'Enter') {
            handleSubmit();
        }
    }
</script>

<svelte:head>
    <title>Sign In - AI Issues Tracker</title>
</svelte:head>

<div class="min-h-screen flex">
    <!-- Left side - Branding -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-purple-700 flex-col justify-center items-center text-white p-12">
        <div class="max-w-md w-full">
            <!-- Logo -->
            <div class="flex items-center mb-8">
                <div class="h-12 w-12 bg-white/20 rounded-xl flex items-center justify-center mr-3">
                    <span class="text-2xl font-bold">✓</span>
                </div>
                <div>
                    <h1 class="text-2xl font-bold">AI Issues Tracker</h1>
                    <p class="text-blue-100 text-sm">Smart Issue Management</p>
                </div>
            </div>

            <h2 class="text-3xl font-bold mb-4">Welcome Back</h2>
            <p class="text-xl text-blue-100 mb-8">
                Sign in to access your AI-enhanced issue tracking dashboard and stay on top of your team's progress.
            </p>

            <!-- Features List -->
            <div class="space-y-4">
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <span class="text-lg">✓</span>
                    </div>
                    <span>Track and manage issues efficiently</span>
                </div>
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <span class="text-lg">⚡</span>
                    </div>
                    <span>AI-powered insights and predictions</span>
                </div>
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <span class="text-lg">👥</span>
                    </div>
                    <span>Real-time team collaboration</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Right side - Login Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div class="max-w-md w-full">
            <!-- Mobile Logo -->
            <div class="lg:hidden flex items-center justify-center mb-8">
                <div class="h-12 w-12 bg-gradient-to-br from-blue-600 to-purple-700 rounded-xl flex items-center justify-center mr-3">
                    <span class="text-2xl font-bold text-white">✓</span>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">AI Issues Tracker</h1>
                    <p class="text-gray-600 text-sm">Smart Issue Management</p>
                </div>
            </div>

            <div class="bg-white">
                <div class="text-center mb-8">
                    <h2 class="text-3xl font-bold text-gray-900">Sign in to your account</h2>
                    <p class="text-gray-600 mt-2">
                        Don't have an account? 
                        <a href="/auth/register" class="text-blue-600 hover:text-blue-800 font-medium">
                            Sign up for free
                        </a>
                    </p>
                </div>

                <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                    <!-- Email Field -->
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                            Email address
                        </label>
                        <input
                            id="email"
                            type="email"
                            bind:value={email}
                            on:keydown={handleKeydown}
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
                                on:keydown={handleKeydown}
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
                                <span class="text-gray-400 hover:text-gray-600">
                                    {showPassword ? '🙈' : '👁️'}
                                </span>
                            </button>
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
                        >
                            Demo accounts
                            <span class="ml-1 transition-transform duration-200 {showDemoAccounts ? 'rotate-180' : ''}">
                                ⬇️
                            </span>
                        </button>
                    </div>

                    <!-- Demo Accounts Section -->
                    {#if showDemoAccounts}
                        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3 animate-in">
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
                    {/if}

                    <!-- Submit Button -->
                    <button
                        type="submit"
                        disabled={loading}
                        class="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    >
                        {#if loading}
                            <span class="mr-2">⏳</span>
                            Signing in...
                        {:else}
                            Sign in
                        {/if}
                    </button>
                </form>

                <!-- Footer Links -->
                <div class="mt-8 text-center space-y-2">
                    <p class="text-sm text-gray-600">
                        Forgot your password? 
                        <a href="/auth/forgot-password" class="text-blue-600 hover:text-blue-800 font-medium">
                            Reset it here
                        </a>
                    </p>
                    <p class="text-xs text-gray-500">
                        🔒 Secure sign-in with industry-standard encryption
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>