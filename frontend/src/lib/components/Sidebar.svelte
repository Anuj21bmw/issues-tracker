<script>
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';
	
	export let open = false;
	
	$: userRole = $authStore.user?.role;
	
	const navigation = [
		{ name: 'Dashboard', href: '/dashboard', icon: '📊', roles: ['ADMIN', 'MAINTAINER'] },
		{ name: 'Issues', href: '/issues', icon: '🎫', roles: ['ADMIN', 'MAINTAINER', 'REPORTER'] },
		{ name: 'Create Issue', href: '/issues/create', icon: '➕', roles: ['ADMIN', 'MAINTAINER', 'REPORTER'] },
		{ name: 'Users', href: '/users', icon: '👥', roles: ['ADMIN'] },
		{ name: 'Analytics', href: '/analytics', icon: '📈', roles: ['ADMIN', 'MAINTAINER'] }
	];
	
	$: filteredNavigation = navigation.filter(item => 
		item.roles.includes(userRole)
	);
	
	function isActive(href) {
		return $page.url.pathname === href || 
			   ($page.url.pathname.startsWith(href) && href !== '/');
	}

	function handleBackdropClick() {
		open = false;
	}

	function handleBackdropKeydown(event) {
		if (event.key === 'Escape') {
			open = false;
		}
	}
</script>

<!-- Mobile backdrop -->
{#if open}
	<div class="fixed inset-0 z-40 lg:hidden">
		<button 
			class="fixed inset-0 bg-gray-600 bg-opacity-75" 
			on:click={handleBackdropClick}
			on:keydown={handleBackdropKeydown}
			aria-label="Close sidebar"
		></button>
	</div>
{/if}

<!-- Sidebar -->
<aside class="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform {open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-transform duration-300 ease-in-out lg:top-16">
	<div class="flex flex-col h-full lg:h-[calc(100vh-4rem)]">
		<!-- Mobile header (hidden on desktop) -->
		<div class="flex items-center h-16 px-6 border-b border-gray-200 lg:hidden">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
						<span class="text-white font-bold">IT</span>
					</div>
				</div>
				<div class="ml-3">
					<div class="text-sm font-medium text-gray-900">Issues Tracker</div>
				</div>
			</div>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
			{#each filteredNavigation as item}
				<a
					href={item.href}
					class="{isActive(item.href) ? 'nav-link-active' : 'nav-link-inactive'}"
					on:click={() => open = false}
				>
					<span class="mr-3 text-lg">{item.icon}</span>
					<span class="font-medium">{item.name}</span>
				</a>
			{/each}
		</nav>

		<!-- User info -->
		<div class="p-4 border-t border-gray-200">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<div class="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
						<span class="text-sm font-medium text-blue-600">
							{$authStore.user?.full_name?.charAt(0) || 'U'}
						</span>
					</div>
				</div>
				<div class="ml-3 flex-1 min-w-0">
					<div class="text-sm font-medium text-gray-900 truncate">
						{$authStore.user?.full_name || 'User'}
					</div>
					<div class="text-xs text-gray-500 truncate">
						{$authStore.user?.email || ''}
					</div>
				</div>
			</div>
		</div>
	</div>
</aside>