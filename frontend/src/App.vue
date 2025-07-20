<template>
	<div>
		<div class="loading-overlay" :class="{ 'complete': isImageLoaded }">
			<div class="slide left-slide"></div>
			<div class="slide right-slide"></div>
			<div class="loading-icon"><LoadingAnimation /></div>
		</div>
		<div class="background-image"></div>
		<div class="background-overlay"></div>
		<div class="app-container">
			<router-view v-on:camera-ready="onCameraReady"/>
		</div>
	</div>
</template>

<script setup lang="ts">
import LoadingAnimation from '@/components/LoadingAnimation.vue';
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
:root {
  --primary-green: #2E7D32;
  --secondary-green: #4CAF50;
  --accent-red: #C62828;
  --background: #F8F9FA;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: var(--background);
  min-height: 100vh;
  min-height: 100dvh;
}

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

.slide {
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

h1 {
  color: var(--primary-green);
  text-align: center;
  margin-top: 20px;
}

p {
  color: #333;
  text-align: center;
  margin: 10px 0;
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
</style>