<script>
	import { authStore } from '$lib/stores/auth';
	
	export let toggleSidebar;
	
	let showUserMenu = false;
	
	function handleLogout() {
		authStore.logout();
		showUserMenu = false;
	}

	function handleKeydown(event) {
		if (event.key === 'Escape') {
			showUserMenu = false;
		}
	}
</script>

<nav class="bg-white shadow-sm border-b border-gray-200 fixed w-full z-50 top-0">
	<div class="px-4 sm:px-6 lg:px-8">
		<div class="flex justify-between h-16">
			<div class="flex items-center">
				<!-- Mobile menu button -->
				<button
					on:click={toggleSidebar}
					class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
					aria-label="Toggle sidebar"
				>
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				
				<!-- Logo/Brand -->
				<div class="flex-shrink-0 flex items-center ml-4 lg:ml-0">
					<div class="flex items-center">
						<div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
							<span class="text-white font-bold text-sm">IT</span>
						</div>
						<h1 class="text-xl font-bold text-gray-900 hidden sm:block">
							Issues Tracker
						</h1>
					</div>
				</div>
			</div>

			<!-- User menu -->
			<div class="flex items-center space-x-4">
				<!-- Notifications (placeholder for future) -->
				<button class="p-2 text-gray-400 hover:text-gray-500 hidden sm:block">
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5z"/>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19c-5 0-8-3-8-6s3-6 8-6 8 3 8 6-3 6-8 6z"/>
					</svg>
				</button>

				<!-- User dropdown -->
				<div class="relative">
					<button
						on:click={() => showUserMenu = !showUserMenu}
						on:keydown={handleKeydown}
						class="flex items-center space-x-3 p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
						aria-expanded={showUserMenu}
						aria-haspopup="true"
					>
						<div class="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
							<span class="text-sm font-medium text-blue-600">
								{$authStore.user?.full_name?.charAt(0) || 'U'}
							</span>
						</div>
						<div class="hidden md:block text-left">
							<div class="text-sm font-medium text-gray-900">
								{$authStore.user?.full_name || 'User'}
							</div>
							<div class="text-xs text-gray-500">
								{$authStore.user?.role || 'USER'}
							</div>
						</div>
						<svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
						</svg>
					</button>

					{#if showUserMenu}
						<div class="absolute right-0 mt-2 w-56 rounded-lg shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50" role="menu">
							<div class="py-1">
								<!-- User info -->
								<div class="px-4 py-3 text-sm text-gray-700 border-b border-gray-200">
									<div class="font-medium">{$authStore.user?.full_name}</div>
									<div class="text-xs text-gray-500 mt-1">{$authStore.user?.email}</div>
									<div class="mt-2">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
											{$authStore.user?.role}
										</span>
									</div>
								</div>
								
								<!-- Menu items -->
								<a href="/dashboard" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors" role="menuitem">
									<svg class="h-4 w-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
									</svg>
									Dashboard
								</a>
								
								<a href="/issues" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors" role="menuitem">
									<svg class="h-4 w-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
									</svg>
									My Issues
								</a>

								<div class="border-t border-gray-200"></div>
								
								<button
									on:click={handleLogout}
									class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
									role="menuitem"
								>
									<svg class="h-4 w-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
									</svg>
									Sign out
								</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</nav>

{#if showUserMenu}
	<button 
		class="fixed inset-0 z-40" 
		on:click={() => showUserMenu = false}
		on:keydown={(e) => e.key === 'Escape' && (showUserMenu = false)}
		aria-label="Close menu"
	></button>
{/if}