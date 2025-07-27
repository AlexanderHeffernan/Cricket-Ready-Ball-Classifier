<template>
	<div class="loading-overlay" :class="{ 'complete': complete }">
		<div class="slide left-slide"></div>
		<div class="slide right-slide"></div>
		<div class="loading-icon">
			<LoadingAnimation />
		</div>
	</div>
</template>

<script setup lang="ts">
import LoadingAnimation from './LoadingAnimation.vue';
defineProps<{ complete: boolean }>();
</script>

<style scoped>
.loading-overlay {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 1000;
}

.loading-overlay.complete {
  pointer-events: none;
}

.loading-overlay .loading-icon {
	opacity: 1;
	transition: opacity 0.5s ease;
}

.loading-overlay.complete .loading-icon {
	opacity: 0;
}

.loading-overlay .slide {
	position: absolute;
	top: 0;
	width: 50%;
	height: 100%;
	transition: transform 0.5s ease 0.5s, opacity 0.5s ease 1s;
	background-color: white;
	opacity: 1;
}

.loading-overlay .left-slide {
	left: 0;
}

.loading-overlay .right-slide {
	right: 0;
}

.loading-overlay.complete .left-slide {
	transform: translateX(-100%);
	opacity: 0;
}

.loading-overlay.complete .right-slide {
	transform: translateX(100%);
	opacity: 0;
}
</style>