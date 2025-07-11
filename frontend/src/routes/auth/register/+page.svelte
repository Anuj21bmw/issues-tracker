<script>
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';
	
	let email = '';
	let password = '';
	let confirmPassword = '';
	let fullName = '';
	
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
					<input
						id="fullName"
						name="fullName"
						type="text"
						autocomplete="name"
						required
						bind:value={fullName}
						class="input"
						placeholder="Enter your full name"
					/>
				</div>

				<div>
					<label for="email" class="label">Email address</label>
					<input
						id="email"
						name="email"
						type="email"
						autocomplete="email"
						required
						bind:value={email}
						class="input"
						placeholder="Enter your email"
					/>
				</div>

				<div>
					<label for="password" class="label">Password</label>
					<input
						id="password"
						name="password"
						type="password"
						autocomplete="new-password"
						required
						bind:value={password}
						class="input"
						placeholder="Create a password"
					/>
					{#if password && password.length < 6}
						<p class="mt-1 text-sm text-red-600">
							Password must be at least 6 characters long
						</p>
					{/if}
				</div>

				<div>
					<label for="confirmPassword" class="label">Confirm password</label>
					<input
						id="confirmPassword"
						name="confirmPassword"
						type="password"
						autocomplete="new-password"
						required
						bind:value={confirmPassword}
						class="input"
						placeholder="Confirm your password"
					/>
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
							Create account
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
