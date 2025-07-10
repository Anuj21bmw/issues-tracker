<script>
	import { onMount } from 'svelte';
	import { toastStore } from '$lib/stores/toast';
	
	export let toast;
	
	let visible = false;
	
	onMount(() => {
		setTimeout(() => {
			visible = true;
		}, 50);
	});
	
	function getColorClasses(type) {
		switch (type) {
			case 'success':
				return 'bg-green-50 border-green-200 text-green-800';
			case 'error':
				return 'bg-red-50 border-red-200 text-red-800';
			case 'warning':
				return 'bg-yellow-50 border-yellow-200 text-yellow-800';
			default:
				return 'bg-blue-50 border-blue-200 text-blue-800';
		}
	}
	
	function handleClose() {
		visible = false;
		setTimeout(() => {
			toastStore.remove(toast.id);
		}, 300);
	}
</script>

<div 
	class="fixed top-4 right-4 z-50 max-w-sm w-full transform transition-all duration-300 ease-in-out {
		visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
	}"
>
	<div class="rounded-lg border shadow-lg p-4 {getColorClasses(toast.type)}">
		<div class="flex items-start">
			<div class="flex-1">
				<p class="text-sm font-medium">
					{toast.message}
				</p>
			</div>
			<div class="ml-4 flex-shrink-0">
				<button
					on:click={handleClose}
					class="inline-flex rounded-md p-1.5 hover:bg-black hover:bg-opacity-10 transition-colors"
				>
					<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
		</div>
	</div>
</div>
