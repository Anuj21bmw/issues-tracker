<script>
	let apiStatus = 'Loading...';
	let demoAccounts = [];

	// Test backend connection
	async function checkBackend() {
		try {
			const response = await fetch('http://localhost:8000/api/demo');
			const data = await response.json();
			apiStatus = 'Connected ✅';
			demoAccounts = data.demo_accounts || [];
		} catch (error) {
			apiStatus = 'Connection Failed ❌';
		}
	}

	// Check backend on load
	checkBackend();
</script>

<svelte:head>
	<title>Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
	<div class="container mx-auto px-4 py-16">
		<div class="text-center mb-12">
			<h1 class="text-5xl font-bold text-gray-900 mb-4">
				Issues & <span class="text-blue-600">Insights</span> Tracker
			</h1>
			<p class="text-xl text-gray-600 mb-8">
				A modern, production-ready platform for tracking issues and insights
			</p>
			
			<!-- Backend Status -->
			<div class="card max-w-md mx-auto mb-8">
				<h3 class="text-lg font-semibold mb-2">Backend Status</h3>
				<p class="text-gray-600">{apiStatus}</p>
			</div>
		</div>

		<!-- Demo Accounts -->
		{#if demoAccounts.length > 0}
			<div class="max-w-4xl mx-auto">
				<h2 class="text-2xl font-bold text-center mb-8">Demo Accounts</h2>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					{#each demoAccounts as account}
						<div class="card">
							<h3 class="font-semibold text-lg mb-2">{account.role}</h3>
							<p class="text-sm text-gray-600 mb-2">Email: {account.email}</p>
							<p class="text-sm text-gray-600">Password: {account.password}</p>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- API Links -->
		<div class="text-center mt-12">
			<div class="space-x-4">
				<a href="http://localhost:8000/api/docs" target="_blank" class="btn-primary">
					API Documentation
				</a>
				<a href="http://localhost:8000/health" target="_blank" class="btn-outline">
					Health Check
				</a>
			</div>
		</div>

		<!-- Quick Test -->
		<div class="max-w-md mx-auto mt-12">
			<div class="card">
				<h3 class="text-lg font-semibold mb-4">Quick Backend Test</h3>
				<button on:click={checkBackend} class="btn-primary w-full">
					Test Backend Connection
				</button>
			</div>
		</div>
	</div>
</div>
