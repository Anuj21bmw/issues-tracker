<script>
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';
	
	let email = '';
	let password = '';
	let passwordElement;
	let showDemoAccounts = false;
	
	async function handleSubmit() {
		if (!email || !password) {
			toastStore.add({
				type: 'error',
				message: 'Please fill in all fields'
			});
			return;
		}

		try {
			await authStore.login(email, password);
			toastStore.add({
				type: 'success',
				message: 'Login successful!'
			});
		} catch (error) {
			toastStore.add({
				type: 'error',
				message: error.message
			});
		}
	}
	
	function quickLogin(role) {
		const accounts = {
			admin: { email: 'admin@example.com', password: 'admin123' },
			maintainer: { email: 'maintainer@example.com', password: 'maintainer123' },
			reporter: { email: 'reporter@example.com', password: 'reporter123' }
		};
		
		const account = accounts[role];
		email = account.email;
		password = account.password;
		handleSubmit();
	}

	function togglePasswordVisibility() {
		if (passwordElement) {
			const currentType = passwordElement.type;
			passwordElement.type = currentType === 'password' ? 'text' : 'password';
		}
	}
</script>

<svelte:head>
	<title>Sign In - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen flex">
	<!-- Left side - Branding -->
	<div class="hidden lg:flex lg:w-1/2 bg-blue-600 flex-col justify-center items-center text-white p-12">
		<div class="max-w-md">
			<div class="h-16 w-16 bg-white/20 rounded-2xl flex items-center justify-center mb-8">
				<span class="text-2xl font-bold">IT</span>
			</div>
			<h1 class="text-4xl font-bold mb-4">Welcome Back</h1>
			<p class="text-xl text-blue-100 mb-8">
				Sign in to access your issue tracking dashboard and stay on top of your team's progress.
			</p>
			<div class="space-y-4 text-blue-100">
				<div class="flex items-center">
					<svg class="h-5 w-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
					</svg>
					Track and manage issues efficiently
				</div>
				<div class="flex items-center">
					<svg class="h-5 w-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
					</svg>
					Real-time collaboration tools
				</div>
				<div class="flex items-center">
					<svg class="h-5 w-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
					</svg>
					Comprehensive analytics and insights
				</div>
			</div>
		</div>
	</div>

	<!-- Right side - Login form -->
	<div class="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24">
		<div class="mx-auto w-full max-w-sm lg:w-96">
			<div>
				<div class="lg:hidden flex items-center justify-center mb-8">
					<div class="h-12 w-12 bg-blue-600 rounded-xl flex items-center justify-center">
						<span class="text-white font-bold">IT</span>
					</div>
				</div>
				<h2 class="text-3xl font-bold text-gray-900">Sign in to your account</h2>
				<p class="mt-2 text-sm text-gray-600">
					Don't have an account?
					<a href="/auth/register" class="font-medium text-blue-600 hover:text-blue-500 transition-colors">
						Sign up for free
					</a>
				</p>
			</div>

			<div class="mt-8">
				<form on:submit|preventDefault={handleSubmit} class="space-y-6">
					<div>
						<label for="email" class="block text-sm font-medium text-gray-700">
							Email address
						</label>
						<div class="mt-1">
							<input
								id="email"
								name="email"
								type="email"
								autocomplete="email"
								required
								bind:value={email}
								class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
								placeholder="Enter your email"
							/>
						</div>
					</div>

					<div>
						<label for="password" class="block text-sm font-medium text-gray-700">
							Password
						</label>
						<div class="mt-1 relative">
							<input
								bind:this={passwordElement}
								id="password"
								name="password"
								type="password"
								autocomplete="current-password"
								required
								bind:value={password}
								class="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
								placeholder="Enter your password"
							/>
							<button
								type="button"
								class="absolute inset-y-0 right-0 pr-3 flex items-center"
								on:click={togglePasswordVisibility}
								aria-label="Toggle password visibility"
							>
								<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
							</button>
						</div>
					</div>

					<div class="flex items-center justify-between">
						<div class="flex items-center">
							<input
								id="remember-me"
								name="remember-me"
								type="checkbox"
								class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<label for="remember-me" class="ml-2 block text-sm text-gray-900">
								Remember me
							</label>
						</div>

						<div class="text-sm">
							<button
								type="button"
								on:click={() => showDemoAccounts = !showDemoAccounts}
								class="font-medium text-blue-600 hover:text-blue-500"
							>
								Demo accounts
							</button>
						</div>
					</div>

					<div>
						<button
							type="submit"
							disabled={$authStore.loading || !email || !password}
							class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
						>
							{#if $authStore.loading}
								<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
								Signing in...
							{:else}
								Sign in
							{/if}
						</button>
					</div>

					<!-- Demo Accounts (collapsible) -->
					{#if showDemoAccounts}
						<div class="mt-6 p-4 bg-gray-50 rounded-lg border">
							<h4 class="text-sm font-medium text-gray-900 mb-3">Demo Accounts (Development Only):</h4>
							<div class="space-y-2">
								<button
									type="button"
									on:click={() => quickLogin('admin')}
									class="w-full text-left p-2 text-xs bg-white rounded border hover:bg-gray-50 transition-colors"
								>
									<strong class="text-blue-600">Admin:</strong> admin@example.com
								</button>
								<button
									type="button"
									on:click={() => quickLogin('maintainer')}
									class="w-full text-left p-2 text-xs bg-white rounded border hover:bg-gray-50 transition-colors"
								>
									<strong class="text-indigo-600">Maintainer:</strong> maintainer@example.com
								</button>
								<button
									type="button"
									on:click={() => quickLogin('reporter')}
									class="w-full text-left p-2 text-xs bg-white rounded border hover:bg-gray-50 transition-colors"
								>
									<strong class="text-green-600">Reporter:</strong> reporter@example.com
								</button>
							</div>
						</div>
					{/if}
				</form>
			</div>
		</div>
	</div>
</div>