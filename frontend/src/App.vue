<template>
	<div>
		<LoadingOverlay :complete="isImageLoaded" />
		<div class="background-image"></div>
		<div class="background-overlay"></div>
		<div class="app-container">
			<div class="mode-selector">
				<RouterLink to="/" class="mode-link" active-class="active">Predict</RouterLink>
				<RouterLink to="/train" class="mode-link" active-class="active">Train</RouterLink>
			</div>
			<router-view v-on:camera-ready="onCameraReady"/>
		</div>
	</div>
</template>

<script setup lang="ts">
import LoadingOverlay from '@/components/LoadingOverlay.vue';
import { ref, onMounted } from 'vue';
import backgroundImg from '@/assets/background.jpg';

const imageReady = ref(false);
const cameraReady = ref(false);
const isImageLoaded = ref(false);

function checkLoadingDone() {
	if (imageReady.value && cameraReady.value) {
		isImageLoaded.value = true;
		document.documentElement.style.setProperty('--background-img', `url(${backgroundImg})`);
	}
}

function onCameraReady() {
	cameraReady.value = true;
	checkLoadingDone();
}

onMounted(() => {
	// Load background image
	const img = new window.Image();
	img.src = backgroundImg;
	img.onload = () => {
		imageReady.value = true;
		checkLoadingDone();
	};
	// Try to access the camera
	navigator.mediaDevices.getUserMedia({ video: true })
	.then(() => {
		// Don't set cameraReady here!
		// Wait for the camera component to emit "ready"
	})
	.catch(() => {
		cameraReady.value = true; // If camera fails, still proceed
		checkLoadingDone();
	});	
});
</script>

<style>
@import "@/styles/global.css";

/* Fixed background image using a div instead of CSS background */
.background-image {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  height: 100lvh;
  background-image: var(--background-img);;
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  z-index: 0;
}

/* White gradient overlay */
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
    rgba(255, 255, 255, 0) 50%
  );
  z-index: 1;
  pointer-events: none;
}

.app-container {
  position: relative;
  z-index: 2;
  min-height: 100vh;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.6s cubic-bezier(.4,0,.2,1);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-to, .fade-leave-from {
  opacity: 1;
}

.mode-selector {
	display: flex;
	gap: 10px;
	justify-content: center;
	margin-bottom: 20px;
	margin-top: 20px;
}

.mode-selector .mode-link {
	padding: 10px 20px;
	font-size: 16px;
	font-weight: bold;
	border: 2px solid #2E7D32;
	background: white;
	color: #2E7D32;
	border-radius: 25px;
	cursor: pointer;
	transition: all 0.3s ease;
	text-decoration: none;
}

.mode-selector .mode-link.active {
	background: #2E7D32;
	color: white;
}
</style>