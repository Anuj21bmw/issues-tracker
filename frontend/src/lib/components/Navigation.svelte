<script>
    import { page } from '$app/stores';
    import { authStore } from '$lib/stores/auth.js';
    import { uiStore } from '$lib/stores/ui.js';

    export let user = null;

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: '📊', roles: ['ADMIN', 'MAINTAINER'] },
        { name: 'Issues', href: '/issues', icon: '🎯', roles: ['ADMIN', 'MAINTAINER', 'REPORTER'] },
        { name: 'Create Issue', href: '/issues/create', icon: '➕', roles: ['ADMIN', 'MAINTAINER', 'REPORTER'] },
        { name: 'Analytics', href: '/analytics', icon: '📈', roles: ['ADMIN', 'MAINTAINER'] },
        { name: 'Settings', href: '/settings', icon: '⚙️', roles: ['ADMIN'] }
    ];

    $: currentPath = $page.url.pathname;
    $: userRole = user?.role || 'REPORTER';
    $: filteredNavigation = navigation.filter(item => item.roles.includes(userRole));

    function isActive(href) {
        if (href === '/dashboard') {
            return currentPath === '/' || currentPath === '/dashboard';
        }
        return currentPath.startsWith(href);
    }

    function handleLogout() {
        authStore.logout();
    }
</script>

<nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            <!-- Logo and primary navigation -->
            <div class="flex">
                <div class="flex-shrink-0 flex items-center">
                    <a href="/" class="flex items-center">
                        <div class="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center mr-3">
                            <span class="text-white font-bold text-sm">🤖</span>
                        </div>
                        <span class="text-xl font-bold text-gray-900">Issues Tracker</span>
                    </a>
                </div>
                
                <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                    {#each filteredNavigation as item}
                        <a
                            href={item.href}
                            class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors {
                                isActive(item.href)
                                    ? 'border-indigo-500 text-gray-900'
                                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                            }"
                        >
                            <span class="mr-2">{item.icon}</span>
                            {item.name}
                        </a>
                    {/each}
                </div>
            </div>

            <!-- User menu -->
            <div class="flex items-center space-x-4">
                <!-- Theme toggle -->
                <button
                    class="p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-md"
                    on:click={() => uiStore.setTheme($uiStore.theme === 'light' ? 'dark' : 'light')}
                >
                    {#if $uiStore.theme === 'light'}
                        🌙
                    {:else}
                        ☀️
                    {/if}
                </button>

                <!-- User info -->
                {#if user}
                    <div class="flex items-center space-x-3">
                        <div class="text-sm">
                            <p class="font-medium text-gray-900">{user.full_name}</p>
                            <p class="text-gray-500">{user.role}</p>
                        </div>
                        <button
                            class="btn-secondary text-sm"
                            on:click={handleLogout}
                        >
                            Logout
                        </button>
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <!-- Mobile navigation -->
    <div class="sm:hidden">
        <div class="pt-2 pb-3 space-y-1">
            {#each filteredNavigation as item}
                <a
                    href={item.href}
                    class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors {
                        isActive(item.href)
                            ? 'bg-indigo-50 border-indigo-500 text-indigo-700'
                            : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'
                    }"
                >
                    <span class="mr-3">{item.icon}</span>
                    {item.name}
                </a>
            {/each}
        </div>
    </div>
</nav>