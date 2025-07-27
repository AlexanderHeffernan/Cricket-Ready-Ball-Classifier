<template>
	<div>
		<div class="background-image"></div>
		<div class="background-overlay"></div>
	</div>
</template>

<script setup lang="ts">
import { onMounted, defineEmits } from 'vue';
import backgroundImg from '@/assets/background.jpg';

const emit = defineEmits(['image-loaded']);

onMounted(() => {
	const img = new window.Image();
	img.src = backgroundImg;
	img.onload = () => {
		document.documentElement.style.setProperty('--background-img', `url(${backgroundImg})`);
		emit('image-loaded');
	};
});
</script>

<style scoped>
.background-image {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100vh;
	height: 100lvh;
	background-image: var(--background-img);
	background-size: cover;
	background-position: center center;
	background-repeat: no-repeat;
	z-index: 0;
}

.background-overlay {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background: linear-gradient(to bottom,
			rgba(255, 255, 255, 1) 0%,
			rgba(255, 255, 255, 0.8) 25%,
			rgba(255, 255, 255, 0.4) 40%,
			rgba(255, 255, 255, 0) 50%);
	z-index: 1;
	pointer-events: none;
}
</style>