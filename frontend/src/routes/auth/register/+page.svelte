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
                toastStore.success('Account created successfully! Please sign in.');
                // Redirect to login page after successful registration
                goto('/auth/login');
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

<div class="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex">
    <!-- Left side - Features showcase -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-purple-600 to-blue-700 relative overflow-hidden">
        <div class="absolute inset-0 bg-black opacity-20"></div>
        <div class="relative z-10 flex flex-col justify-center p-12 text-white">
            <div class="mb-8">
                <div class="flex items-center mb-6">
                    <div class="h-12 w-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center mr-4">
                        <svg class="h-7 w-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold">AI Issues Tracker</h1>
                        <p class="text-purple-200">Smart Issue Management</p>
                    </div>
                </div>
                <h2 class="text-4xl font-bold mb-4">Join thousands of teams</h2>
                <p class="text-xl text-purple-100 mb-8">
                    Streamline your workflow with AI-powered issue tracking and insights.
                </p>
            </div>

            <div class="space-y-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0 w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-4">
                        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                    <span>AI-powered issue classification and prioritization</span>
                </div>
                <div class="flex items-center">
                    <div class="flex-shrink-0 w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-4">
                        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <span>Real-time collaboration and notifications</span>
                </div>
                <div class="flex items-center">
                    <div class="flex-shrink-0 w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-4">
                        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
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
                                <span class="text-gray-400 hover:text-gray-600 text-sm">
                                    {showPassword ? '🙈' : '👁️'}
                                </span>
                            </button>
                        </div>
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
                                <span class="text-gray-400 hover:text-gray-600 text-sm">
                                    {showConfirmPassword ? '🙈' : '👁️'}
                                </span>
                            </button>
                        </div>
                    </div>

                    <!-- Terms and Privacy -->
                    <div class="text-sm text-gray-600">
                        By creating an account, you agree to our 
                        <a href="#" class="text-purple-600 hover:text-purple-800 font-medium">Terms of Service</a> 
                        and 
                        <a href="#" class="text-purple-600 hover:text-purple-800 font-medium">Privacy Policy</a>.
                    </div>

                    <!-- Submit Button -->
                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {#if loading}
                                <span class="flex items-center">
                                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Creating account...
                                </span>
                            {:else}
                                Create account
                            {/if}
                        </button>
                    </div>

                    <!-- Login Link -->
                    <div class="text-center">
                        <p class="text-sm text-gray-600">
                            Already have an account? 
                            <button 
                                type="button"
                                on:click={goToLogin}
                                class="font-medium text-purple-600 hover:text-purple-500"
                            >
                                Sign in here
                            </button>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>