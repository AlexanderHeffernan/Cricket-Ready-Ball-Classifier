<template>
	<div class="camera-capture">
		<div class="camera-container">
			<video ref="cameraStream" id="camera-stream" muted playsinline webkit-playsinline="true"
				x-website-airplay="deny" preload="auto" :class="{ 'hidden': capturedImageSrc }">
			</video>

			<div v-if="capturedImageSrc" class="captured-overlay">
				<img :src="capturedImageSrc" alt="Captured Image" class="captured-image-overlay">
				<div v-if="isLoading" class="loading-spinner">
					<div class="spinner"></div>
					<p>{{ loadingText }}</p>
				</div>
			</div>

			<div v-if="localError" class="error-overlay" :class="{ 'error-animate': showErrorAnimation }">
				<div class="error-content">
					<div class="error-icon">❌</div>
					<p class="error-message">{{ localError }}</p>
				</div>
			</div>

			<div class="glow-effect" v-if="glowClass" :class="glowClass"></div>
		</div>

		<canvas ref="cameraCanvas" style="display: none;"></canvas>

		<div class="capture-container" v-if="!capturedImageSrc || props.error">
			<button v-if="!props.error" @click="capturePhoto" class="capture-button" :disabled="isLoading">
				{{ isLoading ? loadingText : 'Capture Photo' }}
			</button>
			<button v-else @click="$emit('retry')" class="retry-button">
				Retry
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';

interface Props {
	isLoading?: boolean;
	loadingText?: string;
	glowClass?: string;
	error?: string | null;
	showRetry?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	isLoading: false,
	loadingText: 'Processing...',
	glowClass: ''
});

const emit = defineEmits<{
	captured: [canvas: HTMLCanvasElement, imageDataUrl: string];
	error: [message: string];
	retry: [];
}>();

const cameraStream = ref<HTMLVideoElement>();
const cameraCanvas = ref<HTMLCanvasElement>();
const capturedImageSrc = ref<string | null>(null);
const currentStream = ref<MediaStream | null>(null);
const showErrorAnimation = ref(false);
const localError = ref<string | null>(null);
const errorFadeOutTimeout = ref<number | null>(null);

// Watch for error changes to trigger animation with proper fade out
watch(() => props.error, (newError: string | null | undefined) => {
	// Clear any pending fade out timeout
	if (errorFadeOutTimeout.value) {
		clearTimeout(errorFadeOutTimeout.value);
		errorFadeOutTimeout.value = null;
	}

	if (newError) {
		// Set local error immediately
		localError.value = newError;
		// Reset animation state
		showErrorAnimation.value = false;
		// Use setTimeout to ensure DOM element is rendered first
		setTimeout(() => {
			showErrorAnimation.value = true;
		}, 50);
	} else {
		// Start fade out animation but keep local error
		showErrorAnimation.value = false;
		// Clear local error after fade out completes
		errorFadeOutTimeout.value = setTimeout(() => {
			localError.value = null;
		}, 700); // Match the transition duration
	}
});

onMounted(() => {
	initializeCamera();
})

const initializeCamera = async () => {
	try {
		const isSecureContext = location.protocol === 'https:' || location.hostname === 'localhost';
		if (!isSecureContext) {
			emit('error', 'Camera access requires HTTPS or localhost.');
			return;
		}

		if (!navigator.mediaDevices?.getUserMedia) {
			emit('error', 'Camera not supported in this browser.');
			return;
		}

		const stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: { ideal: 'environment' } }
		});

		currentStream.value = stream

		if (cameraStream.value) {
			cameraStream.value.srcObject = stream;
			cameraStream.value.setAttribute('playsinline', 'true');
			await cameraStream.value.play();
		}

	} catch (error: unknown) {
		console.error('Camera initialization error:', error)
		const err = error as Error
		const errorMessages: Record<string, string> = {
			'NotAllowedError': 'Camera access denied. Please allow permissions.',
			'NotFoundError': 'No camera found.',
			'NotSupportedError': 'Camera requires HTTPS.'
		}
		emit('error', errorMessages[err.name] || `Failed to access camera: ${err.message}`)
	}
}

const capturePhoto = async () => {
	if (!cameraStream.value || !cameraCanvas.value) return;

	const canvas = cameraCanvas.value;
	const video = cameraStream.value;
	const context = canvas.getContext('2d');
	if (!context) return;

	// Circular crop logic
	const videoRect = video.getBoundingClientRect();
	const circleSize = Math.min(videoRect.width, videoRect.height);
	const circleRadius = circleSize / 2;

	const scaleX = video.videoWidth / videoRect.width;
	const scaleY = video.videoHeight / videoRect.height;
	const actualRadius = circleRadius * Math.min(scaleX, scaleY);

	const cropSize = actualRadius * 2;
	canvas.width = cropSize;
	canvas.height = cropSize;

	context.clearRect(0, 0, cropSize, cropSize);
	context.save();
	context.beginPath();
	context.arc(cropSize / 2, cropSize / 2, actualRadius, 0, 2 * Math.PI);
	context.clip();

	context.drawImage(
		video,
		video.videoWidth / 2 - actualRadius,
		video.videoHeight / 2 - actualRadius,
		cropSize, cropSize, 0, 0, cropSize, cropSize
	);

	context.restore();

	const imageDataUrl = canvas.toDataURL('image/png');
	capturedImageSrc.value = imageDataUrl;

	emit('captured', canvas, imageDataUrl);
}

const reset = () => {
	capturedImageSrc.value = null;
}

onUnmounted(() => {
	currentStream.value?.getTracks().forEach(track => track.stop());
	if (errorFadeOutTimeout.value) {
		clearTimeout(errorFadeOutTimeout.value);
	}
})

defineExpose({ reset });
</script>

<style scoped>
.camera-container {
	position: relative;
	display: inline-block;
	margin-bottom: 20px;
}

#camera-stream {
	width: 100%;
	max-width: 400px;
	aspect-ratio: 1/1;
	border: 4px solid #795548;
	border-radius: 50%;
	object-fit: cover;
	box-shadow: 0 0 20px rgba(121, 85, 72, 0.3);
	transition: all 0.3s ease;
	pointer-events: none;
}

#camera-stream.hidden {
	opacity: 0;
	visibility: hidden;
}

.captured-overlay {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	border-radius: 50%;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 4px solid #795548;
	box-shadow: 0 0 20px rgba(121, 85, 72, 0.3);
	z-index: 20;
}

.captured-image-overlay {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.loading-spinner {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	color: white;
	text-align: center;
	background: rgba(0, 0, 0, 0.6);
	padding: 20px;
	border-radius: 10px;
}

.spinner {
	width: 40px;
	height: 40px;
	border: 4px solid rgba(255, 255, 255, 0.3);
	border-top: 4px solid white;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 10px;
}

@keyframes spin {
	0% {
		transform: rotate(0deg);
	}

	100% {
		transform: rotate(360deg);
	}
}

.glow-effect {
	position: absolute;
	top: -8px;
	left: -8px;
	right: -8px;
	bottom: -8px;
	border-radius: 50%;
	opacity: 0;
	transition: opacity 0.5s ease;
	pointer-events: none;
}

.glow-effect.match-ready {
	opacity: 1;
	box-shadow: 0 0 30px #4CAF50, 0 0 60px #4CAF50;
	animation: pulse-green 2s ease-in-out infinite;
}

.glow-effect.not-match-ready {
	opacity: 1;
	box-shadow: 0 0 30px #C62828, 0 0 60px #C62828;
	animation: pulse-red 2s ease-in-out infinite;
}

@keyframes pulse-green {

	0%,
	100% {
		box-shadow: 0 0 30px #4CAF50, 0 0 60px #4CAF50;
	}

	50% {
		box-shadow: 0 0 40px #4CAF50, 0 0 80px #4CAF50;
	}
}

@keyframes pulse-red {

	0%,
	100% {
		box-shadow: 0 0 30px #C62828, 0 0 60px #C62828;
	}

	50% {
		box-shadow: 0 0 40px #C62828, 0 0 80px #C62828;
	}
}

.capture-button {
	padding: 15px 30px;
	font-size: 18px;
	font-weight: bold;
	background: linear-gradient(135deg, #4CAF50, #2E7D32);
	color: white;
	border: none;
	border-radius: 50px;
	cursor: pointer;
	transition: all 0.3s ease;
	box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
	text-transform: uppercase;
	letter-spacing: 1px;
	min-height: 44px;
}

.capture-button:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.capture-button:disabled {
	background: #cccccc;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.retry-button {
	padding: 15px 30px;
	font-size: 18px;
	font-weight: bold;
	background: linear-gradient(135deg, #C62828, #B71C1C);
	color: white;
	border: none;
	border-radius: 50px;
	cursor: pointer;
	transition: all 0.3s ease;
	box-shadow: 0 4px 15px rgba(198, 40, 40, 0.3);
	text-transform: uppercase;
	letter-spacing: 1px;
	min-height: 44px;
}

.retry-button:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(198, 40, 40, 0.4);
	background: linear-gradient(135deg, #D32F2F, #C62828);
}

@media (max-width: 768px) {
	#camera-stream {
		max-width: 350px;
	}
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(220, 53, 69, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  opacity: 0;
  transform: scale(0.5) rotate(-15deg);
  backdrop-filter: blur(8px);
  transition: all 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 0 0 rgba(220, 53, 69, 0.4);
}

.error-overlay.error-animate {
  opacity: 1;
  transform: scale(1) rotate(0deg);
  box-shadow: 0 0 50px rgba(220, 53, 69, 0.6), 
              0 0 100px rgba(220, 53, 69, 0.3),
              inset 0 0 50px rgba(255, 255, 255, 0.1);
}

.error-content {
  text-align: center;
  padding: 20px;
  max-width: 280px;
  transform: translateY(30px) scale(0.7);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s;
}

.error-overlay.error-animate .error-content {
  transform: translateY(0) scale(1);
  opacity: 1;
}

.error-message {
  font-size: 20px !important;
  font-weight: 700 !important;
  margin: 0 !important;
  line-height: 1.4 !important;
  color: #ffffff !important;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.8), 
               0 0 20px rgba(255, 255, 255, 0.3) !important;
  letter-spacing: 0.5px !important;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6))
          drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
  animation: dramaticShake 1s ease-in-out;
  transform-origin: center;
}

@keyframes dramaticShake {
  0% { 
    transform: translateX(0) rotate(0deg) scale(0.3); 
    opacity: 0;
  }
  20% { 
    transform: translateX(-10px) rotate(-8deg) scale(0.7); 
    opacity: 0.8;
  }
  40% { 
    transform: translateX(10px) rotate(8deg) scale(1.2); 
    opacity: 1;
  }
  60% { 
    transform: translateX(-5px) rotate(-4deg) scale(0.9); 
  }
  80% { 
    transform: translateX(5px) rotate(4deg) scale(1.1); 
  }
  100% { 
    transform: translateX(0) rotate(0deg) scale(1); 
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
  60% {
    transform: translateY(-4px);
  }
}

</style>