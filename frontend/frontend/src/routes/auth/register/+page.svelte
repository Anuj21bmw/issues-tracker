<script>
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';
	
	let email = '';
	let password = '';
	let confirmPassword = '';
	let fullName = '';
	let showPassword = false;
	let showConfirmPassword = false;
	
	$: passwordsMatch = password === confirmPassword;
	$: isValid = email && password && fullName && passwordsMatch && password.length >= 6;
	
	async function handleSubmit() {
		if (!isValid) {
			toastStore.add({
				type: 'error',
				message: 'Please fill in all fields correctly'
			});
			return;
		}
		
		try {
			await authStore.register({
				email,
				password,
				full_name: fullName,
				role: 'REPORTER'
			});
			toastStore.add({
				type: 'success',
				message: 'Registration successful! Please login.'
			});
		} catch (error) {
			toastStore.add({
				type: 'error',
				message: error.message
			});
		}
	}
	
	function handleKeydown(event) {
		if (event.key === 'Enter' && isValid) {
			handleSubmit();
		}
	}
</script>

<svelte:head>
	<title>Register - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div class="text-center">
			<div class="mx-auto h-12 w-12 bg-blue-600 rounded-xl flex items-center justify-center">
				<svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
				</svg>
			</div>
			<h2 class="mt-6 text-3xl font-bold text-gray-900">
				Create your account
			</h2>
			<p class="mt-2 text-sm text-gray-600">
				Or 
				<a href="/auth/login" class="font-medium text-blue-600 hover:text-blue-500 transition-colors">
					sign in to your existing account
				</a>
			</p>
		</div>

		<div class="card">
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				<div>
					<label for="fullName" class="label">Full name</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</div>
						<input
							id="fullName"
							name="fullName"
							type="text"
							autocomplete="name"
							required
							bind:value={fullName}
							on:keydown={handleKeydown}
							class="input pl-10"
							placeholder="Enter your full name"
						/>
					</div>
				</div>

				<div>
					<label for="email" class="label">Email address</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
							</svg>
						</div>
						<input
							id="email"
							name="email"
							type="email"
							autocomplete="email"
							required
							bind:value={email}
							on:keydown={handleKeydown}
							class="input pl-10"
							placeholder="Enter your email"
						/>
					</div>
				</div>

				<div>
					<label for="password" class="label">Password</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
							</svg>
						</div>
						<input
							id="password"
							name="password"
							type={showPassword ? 'text' : 'password'}
							autocomplete="new-password"
							required
							bind:value={password}
							on:keydown={handleKeydown}
							class="input pl-10 pr-10"
							placeholder="Create a password"
						/>
						<button
							type="button"
							class="absolute inset-y-0 right-0 pr-3 flex items-center"
							on:click={() => showPassword = !showPassword}
						>
							<svg class="h-5 w-5 text-gray-400 hover:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								{#if showPassword}
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
								{:else}
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								{/if}
							</svg>
						</button>
					</div>
					{#if password && password.length < 6}
						<p class="mt-1 text-sm text-red-600">
							Password must be at least 6 characters long
						</p>
					{/if}
				</div>

				<div>
					<label for="confirmPassword" class="label">Confirm password</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
							</svg>
						</div>
						<input
							id="confirmPassword"
							name="confirmPassword"
							type={showConfirmPassword ? 'text' : 'password'}
							autocomplete="new-password"
							required
							bind:value={confirmPassword}
							on:keydown={handleKeydown}
							class="input pl-10 pr-10"
							placeholder="Confirm your password"
						/>
						<button
							type="button"
							class="absolute inset-y-0 right-0 pr-3 flex items-center"
							on:click={() => showConfirmPassword = !showConfirmPassword}
						>
							<svg class="h-5 w-5 text-gray-400 hover:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								{#if showConfirmPassword}
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
								{:else}
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								{/if}
							</svg>
						</button>
					</div>
					{#if confirmPassword && !passwordsMatch}
						<p class="mt-1 text-sm text-red-600">
							Passwords do not match
						</p>
					{/if}
				</div>

				<div>
					<button
						type="submit"
						disabled={$authStore.loading || !isValid}
						class="btn-primary w-full flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if $authStore.loading}
							<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
							Creating account...
						{:else}
							<svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
							</svg>
							Create account
						{/if}
					</button>
				</div>

				<div class="text-xs text-gray-500 text-center">
					By creating an account, you agree to our Terms of Service and Privacy Policy.
				</div>
			</form>
		</div>
	</div>
</div>
