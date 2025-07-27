<template>
	<div>
		<LoadingOverlay :complete="isImageLoaded" />
		<BackgroundImage @image-loaded="onImageLoaded" />
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
import BackgroundImage from '@/components/BackgroundImage.vue';
import { ref } from 'vue';

const imageReady = ref(false);
const cameraReady = ref(false);
const isImageLoaded = ref(false);

function checkLoadingDone() {
	if (imageReady.value && cameraReady.value) {
		isImageLoaded.value = true;
	}
}

function onImageLoaded() {
	imageReady.value = true;
	checkLoadingDone();
}

function onCameraReady() {
	cameraReady.value = true;
	checkLoadingDone();
}
</script>

<style>
@import "@/styles/global.css";

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