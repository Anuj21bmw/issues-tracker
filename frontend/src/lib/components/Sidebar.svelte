<script>
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';
	import { 
		Home, 
		AlertTriangle, 
		Users, 
		BarChart3, 
		Settings,
		Plus
	} from 'lucide-svelte';
	
	export let open = false;
	
	$: userRole = $authStore.user?.role;
	
	const navigation = [
		{ name: 'Dashboard', href: '/dashboard', icon: Home, roles: ['ADMIN', 'MAINTAINER'] },
		{ name: 'Issues', href: '/issues', icon: AlertTriangle, roles: ['ADMIN', 'MAINTAINER', 'REPORTER'] },
		{ name: 'Create Issue', href: '/issues/create', icon: Plus, roles: ['ADMIN', 'MAINTAINER', 'REPORTER'] },
		{ name: 'Users', href: '/users', icon: Users, roles: ['ADMIN'] },
		{ name: 'Analytics', href: '/analytics', icon: BarChart3, roles: ['ADMIN', 'MAINTAINER'] },
		{ name: 'Settings', href: '/settings', icon: Settings, roles: ['ADMIN'] }
	];
	
	$: filteredNavigation = navigation.filter(item => 
		item.roles.includes(userRole)
	);
	
	function isActive(href) {
		return $page.url.pathname === href || 
			   ($page.url.pathname.startsWith(href) && href !== '/');
	}
</script>

<!-- Mobile menu overlay -->
{#if open}
	<div class="fixed inset-0 z-40 lg:hidden">
		<div class="fixed inset-0 bg-gray-600 bg-opacity-75" on:click={() => open = false}></div>
	</div>
{/if}

<!-- Sidebar -->
<aside class="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform {open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-transform duration-300 ease-in-out">
	<div class="flex flex-col h-full">
		<!-- Logo -->
		<div class="flex items-center h-16 px-6 border-b border-gray-200 dark:border-gray-700">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<div class="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
						<AlertTriangle class="h-5 w-5 text-white" />
					</div>
				</div>
				<div class="ml-3">
					<div class="text-sm font-medium text-gray-900 dark:text-white">Issues Tracker</div>
				</div>
			</div>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
			{#each filteredNavigation as item}
				<a
					href={item.href}
					class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 {
						isActive(item.href)
							? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 border-r-2 border-primary-500'
							: 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
					}"
					on:click={() => open = false}
				>
					<svelte:component 
						this={item.icon} 
						class="mr-3 h-5 w-5 {isActive(item.href) ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'}" 
					/>
					{item.name}
				</a>
			{/each}
		</nav>

		<!-- User info -->
		<div class="p-4 border-t border-gray-200 dark:border-gray-700">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<div class="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
						<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$authStore.user?.full_name?.charAt(0) || 'U'}
						</span>
					</div>
				</div>
				<div class="ml-3 flex-1 min-w-0">
					<div class="text-sm font-medium text-gray-900 dark:text-white truncate">
						{$authStore.user?.full_name || 'User'}
					</div>
					<div class="text-xs text-gray-500 dark:text-gray-400 truncate">
						{$authStore.user?.role || 'REPORTER'}
					</div>
				</div>
			</div>
		</div>
	</div>
</aside>

<!-- Spacer for fixed sidebar on desktop -->
<div class="hidden lg:block lg:w-64"></div>