<!-- src/routes/auth/register/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { authStore } from '$lib/stores/auth.js';
    import { toastStore } from '$lib/stores/toast.js';
    
    let fullName = '';
    let email = '';
    let password = '';
    let confirmPassword = '';
    let showPassword = false;
    let showConfirmPassword = false;
    let loading = false;
    let passwordInput;
    let confirmPasswordInput;

    onMount(() => {
        if ($authStore.isAuthenticated) {
            goto('/dashboard');
        }
    });

    async function handleSubmit() {
        if (!fullName || !email || !password || !confirmPassword) {
            toastStore.error('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            toastStore.error('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            toastStore.error('Password must be at least 6 characters long');
            return;
        }

        loading = true;
        try {
            const result = await authStore.register({
                full_name: fullName,
                email: email,
                password: password
            });

            if (!result.success) {
                toastStore.error(result.error || 'Registration failed');
            } else {
                toastStore.success('Account created successfully!');
            }
        } catch (error) {
            toastStore.error('Registration failed: ' + error.message);
        }
        loading = false;
    }

    function handleKeydown(event) {
        if (event.key === 'Enter') {
            handleSubmit();
        }
    }

    function togglePassword() {
        showPassword = !showPassword;
        if (passwordInput) {
            passwordInput.type = showPassword ? 'text' : 'password';
        }
    }

    function toggleConfirmPassword() {
        showConfirmPassword = !showConfirmPassword;
        if (confirmPasswordInput) {
            confirmPasswordInput.type = showConfirmPassword ? 'text' : 'password';
        }
    }

    function goToLogin() {
        goto('/auth/login');
    }
</script>

<svelte:head>
    <title>Create Account - AI Issues Tracker</title>
</svelte:head>

<div class="min-h-screen flex">
    <!-- Left side - Branding & Benefits -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-purple-600 to-blue-700 flex-col justify-center items-center text-white p-12">
        <div class="max-w-md w-full">
            <!-- Logo -->
            <div class="flex items-center mb-8">
                <div class="h-12 w-12 bg-white/20 rounded-xl flex items-center justify-center mr-3">
                    <svg class="h-7 w-7" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                </div>
                <div>
                    <h1 class="text-2xl font-bold">AI Issues Tracker</h1>
                    <p class="text-purple-100 text-sm">Smart Issue Management</p>
                </div>
            </div>

            <h2 class="text-3xl font-bold mb-4">Join Our Platform</h2>
            <p class="text-xl text-purple-100 mb-8">
                Create your account and start managing issues with AI-powered insights and team collaboration tools.
            </p>

            <!-- Benefits List -->
            <div class="space-y-4">
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                    </div>
                    <span>Secure and reliable platform</span>
                </div>
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                    </div>
                    <span>AI-powered issue analysis</span>
                </div>
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
                        </svg>
                    </div>
                    <span>Collaborative team workspace</span>
                </div>
                <div class="flex items-center">
                    <div class="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                        </svg>
                    </div>
                    <span>Advanced analytics and reporting</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Right side - Registration Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div class="max-w-md w-full">
            <!-- Mobile Logo -->
            <div class="lg:hidden flex items-center justify-center mb-8">
                <div class="h-12 w-12 bg-gradient-to-br from-purple-600 to-blue-700 rounded-xl flex items-center justify-center mr-3">
                    <svg class="h-7 w-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">AI Issues Tracker</h1>
                    <p class="text-gray-600 text-sm">Smart Issue Management</p>
                </div>
            </div>

            <div class="bg-white">
                <div class="text-center mb-8">
                    <h2 class="text-3xl font-bold text-gray-900">Create your account</h2>
                    <p class="text-gray-600 mt-2">
                        Or 
                        <button 
                            type="button"
                            on:click={goToLogin}
                            class="text-purple-600 hover:text-purple-800 font-medium"
                        >
                            sign in to your existing account
                        </button>
                    </p>
                </div>

                <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                    <!-- Full Name Field -->
                    <div>
                        <label for="fullName" class="block text-sm font-medium text-gray-700 mb-2">
                            Full name
                        </label>
                        <input
                            id="fullName"
                            type="text"
                            bind:value={fullName}
                            on:keydown={handleKeydown}
                            placeholder="Enter your full name"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                            required
                        />
                    </div>

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
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
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
                                placeholder="Create a password"
                                class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                required
                                minlength="6"
                            />
                            <button
                                type="button"
                                on:click={togglePassword}
                                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                                aria-label="Toggle password visibility"
                            >
                                {#if showPassword}
                                    <svg class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                                    </svg>
                                {:else}
                                    <svg class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                    </svg>
                                {/if}
                            </button>
                        </div>
                        <p class="mt-1 text-xs text-gray-500">Must be at least 6 characters</p>
                    </div>

                    <!-- Confirm Password Field -->
                    <div>
                        <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
                            Confirm password
                        </label>
                        <div class="relative">
                            <input
                                bind:this={confirmPasswordInput}
                                id="confirmPassword"
                                type="password"
                                bind:value={confirmPassword}
                                on:keydown={handleKeydown}
                                placeholder="Confirm your password"
                                class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                required
                            />
                            <button
                                type="button"
                                on:click={toggleConfirmPassword}
                                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                                aria-label="Toggle password visibility"
                            >
                                {#if showConfirmPassword}
                                    <svg class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                                    </svg>
                                {:else}
                                    <svg class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                    </svg>
                                {/if}
                            </button>
                        </div>
                        {#if password && confirmPassword && password !== confirmPassword}
                            <p class="mt-1 text-xs text-red-600">Passwords do not match</p>
                        {/if}
                    </div>

                    <!-- Terms and Conditions -->
                    <div class="flex items-start">
                        <div class="flex items-center h-5">
                            <input
                                id="terms"
                                type="checkbox"
                                class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                                required
                            />
                        </div>
                        <div class="ml-3 text-sm">
                            <label for="terms" class="text-gray-700">
                                I agree to the 
                                <a href="/terms" class="text-purple-600 hover:text-purple-800 font-medium">
                                    Terms and Conditions
                                </a>
                                and 
                                <a href="/privacy" class="text-purple-600 hover:text-purple-800 font-medium">
                                    Privacy Policy
                                </a>
                            </label>
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <button
                        type="submit"
                        disabled={loading || !fullName || !email || !password || !confirmPassword || password !== confirmPassword}
                        class="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {#if loading}
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                            </svg>
                            Creating account...
                        {:else}
                            Create account
                        {/if}
                    </button>
                </form>

                <!-- Footer -->
                <div class="mt-8 text-center">
                    <p class="text-xs text-gray-500">
                        By creating an account, you agree to our secure data handling practices
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>