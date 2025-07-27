<!-- src/lib/components/Navigation.svelte -->
<script>
    import { authStore } from '$lib/stores/auth.js';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    
    $: user = $authStore.user;
    $: isAuthenticated = $authStore.isAuthenticated;
    $: currentPath = $page.url.pathname;

    let mobileMenuOpen = false;

    function handleLogout() {
        authStore.logout();
    }

    function toggleMobileMenu() {
        mobileMenuOpen = !mobileMenuOpen;
    }

    function closeMobileMenu() {
        mobileMenuOpen = false;
    }

    function navigateTo(path) {
        goto(path);
        closeMobileMenu();
    }
</script>

{#if isAuthenticated}
<nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            <!-- Left side - Logo and main nav -->
            <div class="flex">
                <!-- Logo -->
                <div class="flex-shrink-0 flex items-center">
                    <button on:click={() => navigateTo('/dashboard')} class="flex items-center">
                        <div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                            <span class="text-white font-bold text-sm">IT</span>
                        </div>
                        <span class="text-xl font-bold text-gray-900">Issues Tracker</span>
                    </button>
                </div>

                <!-- Desktop Navigation -->
                <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                    {#if user?.role === 'ADMIN' || user?.role === 'MAINTAINER'}
                        <button
                            on:click={() => navigateTo('/dashboard')}
                            class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200
                                {currentPath === '/dashboard' ? 'border-blue-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                        >
                            📊 Dashboard
                        </button>
                    {/if}
                    
                    <button
                        on:click={() => navigateTo('/issues')}
                        class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200
                            {currentPath.startsWith('/issues') ? 'border-blue-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                    >
                        🎫 Issues
                    </button>

                    <button
                        on:click={() => navigateTo('/issues/create')}
                        class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200
                            {currentPath === '/issues/create' ? 'border-blue-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                    >
                        ✏️ Create Issue
                    </button>

                    {#if user?.role === 'ADMIN'}
                        <button
                            on:click={() => navigateTo('/admin')}
                            class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200
                                {currentPath.startsWith('/admin') ? 'border-blue-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                        >
                            ⚙️ Admin
                        </button>
                    {/if}
                </div>
            </div>

            <!-- Right side - User menu -->
            <div class="flex items-center">
                <!-- Desktop user menu -->
                <div class="hidden sm:flex sm:items-center sm:ml-6">
                    <div class="flex items-center space-x-4">
                        <!-- User info -->
                        <div class="flex items-center space-x-3">
                            <div class="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                                <span class="text-sm font-medium text-gray-700">
                                    {user?.full_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                                </span>
                            </div>
                            <div class="hidden lg:block">
                                <div class="text-sm font-medium text-gray-900">
                                    {user?.full_name || user?.email}
                                </div>
                                <div class="text-xs text-gray-500">
                                    {user?.role}
                                </div>
                            </div>
                        </div>

                        <!-- Logout button -->
                        <button
                            on:click={handleLogout}
                            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                        >
                            Sign out
                        </button>
                    </div>
                </div>

                <!-- Mobile menu button -->
                <div class="sm:hidden">
                    <button
                        on:click={toggleMobileMenu}
                        class="bg-white inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                        aria-expanded="false"
                    >
                        <span class="sr-only">Open main menu</span>
                        {#if !mobileMenuOpen}
                            <svg class="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        {:else}
                            <svg class="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        {/if}
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Mobile menu -->
    {#if mobileMenuOpen}
        <div class="sm:hidden">
            <div class="pt-2 pb-3 space-y-1">
                {#if user?.role === 'ADMIN' || user?.role === 'MAINTAINER'}
                    <button
                        on:click={() => navigateTo('/dashboard')}
                        class="block w-full text-left pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200
                            {currentPath === '/dashboard' ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'}"
                    >
                        📊 Dashboard
                    </button>
                {/if}
                
                <button
                    on:click={() => navigateTo('/issues')}
                    class="block w-full text-left pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200
                        {currentPath.startsWith('/issues') ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'}"
                >
                    🎫 Issues
                </button>

                <button
                    on:click={() => navigateTo('/issues/create')}
                    class="block w-full text-left pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200
                        {currentPath === '/issues/create' ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'}"
                >
                    ✏️ Create Issue
                </button>

                {#if user?.role === 'ADMIN'}
                    <button
                        on:click={() => navigateTo('/admin')}
                        class="block w-full text-left pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200
                            {currentPath.startsWith('/admin') ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'}"
                    >
                        ⚙️ Admin
                    </button>
                {/if}
            </div>
            
            <!-- Mobile user section -->
            <div class="pt-4 pb-3 border-t border-gray-200">
                <div class="flex items-center px-4">
                    <div class="h-10 w-10 bg-gray-300 rounded-full flex items-center justify-center">
                        <span class="text-sm font-medium text-gray-700">
                            {user?.full_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                        </span>
                    </div>
                    <div class="ml-3">
                        <div class="text-base font-medium text-gray-800">
                            {user?.full_name || user?.email}
                        </div>
                        <div class="text-sm font-medium text-gray-500">
                            {user?.role}
                        </div>
                    </div>
                </div>
                <div class="mt-3 space-y-1">
                    <button
                        on:click={handleLogout}
                        class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100 transition-colors duration-200"
                    >
                        Sign out
                    </button>
                </div>
            </div>
        </div>
    {/if}
</nav>
{/if}