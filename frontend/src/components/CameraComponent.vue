<template>
	<!-- Camera Capture Component -->
	<div class="camera-capture">
		<div class="camera-container">
			<!-- Live Camera Stream-->
			<video
				ref="cameraStream"
				id="camera-stream"
				muted
				playsinline
				webkit-playsinline="true"
				x-website-airplay="deny"
				preload="auto"
				:class="{ 'hidden': capturedImageSrc }"
				aria-label="Live camera stream"
			></video>

			<!-- Captured Image Overlay -->
			<div v-if="capturedImageSrc" class="captured-overlay">
				<img :src="capturedImageSrc" alt="Captured Image" class="captured-image-overlay">
			</div>

			<!-- Loading/Error Overlay-->
			<div class="overlay" :class="{ 'loading': isLoading, 'error': error }">
				<LoadingAnimation v-if="isLoading"/>
				<div v-if="error" class="error-content">
					<div class="error-icon">❌</div>
					<p class="error-message">{{ error }}</p>
				</div>
			</div>

			<!-- Glow Effect -->
			<div class="glow-effect" v-if="glowClass" :class="glowClass"></div>
		</div>

		<!-- Hidden Canvas for Capturing Photo -->
		<canvas ref="cameraCanvas" style="display: none;"></canvas>

		<!-- Capture/Retry Buttons -->
		<div class="capture-container" v-if="!capturedImageSrc || error">
			<!-- Capture Button -->
			<button
				v-if="!error"
				@click="capturePhoto"
				class="capture button"
				:disabled="isLoading"
				aria-label="Capture photo"
			>
				Capture Photo
			</button>

			<!-- Retry Button -->
			<button 
				v-else 
				@click="$emit('retry')" 
				class="retry button"
			>
				Retry
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
// Imports
import { ref, onMounted, onUnmounted } from 'vue';
import LoadingAnimation from './LoadingAnimation.vue';

// Props
withDefaults(defineProps<{
	isLoading?: boolean;
	glowClass?: string;
	error?: string | null;
}>(), {
	isLoading: false,
	glowClass: ''
});

// Emits
const emit = defineEmits<{
	captured: [canvas: HTMLCanvasElement, imageDataUrl: string];
	cameraError: [message: string];
	retry: [];
	ready: [];
}>();

// Refs
const cameraStream = ref<HTMLVideoElement>();
const cameraCanvas = ref<HTMLCanvasElement>();
const capturedImageSrc = ref<string | null>(null);
const currentStream = ref<MediaStream | null>(null);

// Lifecycle: Mount/Unmount
onMounted(() => {
	initializeCamera();
	cameraStream.value?.addEventListener('playing', () => emit('ready'));
});

onUnmounted(() => currentStream.value?.getTracks().forEach(track => track.stop()));

/**
 * Initialize the camera stream.
 * Handles errors and sets up the video element.
 */
const initializeCamera = async () => {
	try {
		// Check for HTTPS or localhost
		if (location.protocol !== 'https:' && location.hostname !== 'localhost')
			return emit('cameraError', 'Camera access requires HTTPS or localhost.');

		// Check for getUserMedia support
		if (!navigator.mediaDevices?.getUserMedia)
			return emit('cameraError', 'Camera not supported in this browser.');

		// Request camera access
		const stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: { ideal: 'environment' } }
		});

		// Set the video stream to the video element
		currentStream.value = stream;
		if (!cameraStream.value) { return; }

		cameraStream.value.srcObject = stream;
		cameraStream.value.setAttribute('playsinline', 'true');
		await cameraStream.value.play();
	} catch (error) {
		const err = error as Error
		const errorMessages: Record<string, string> = {
			'NotAllowedError': 'Camera access denied. Please allow permissions.',
			'NotFoundError': 'No camera found.',
			'NotSupportedError': 'Camera requires HTTPS.'
		}
		console.error('Camera initialization error:', error)
		emit('cameraError', errorMessages[err.name] || `Failed to access camera: ${err.message}`)
	}
}

/**
 * Capture a photo from the camera stream.
 * Crops the image to a circular shape and emits the captured data.
 */
const capturePhoto = async () => {
	// Ensure camera and canvas are available
	if (!cameraStream.value || !cameraCanvas.value) { return; }

	// Get the canvas context
	const canvas = cameraCanvas.value, video = cameraStream.value;
	const ctx = canvas.getContext('2d');
	if (!ctx) { return; }

	// Circular crop logic
	const rect = video.getBoundingClientRect();
	const radius = Math.min(video.videoWidth / rect.width, video.videoHeight / rect.height) * Math.min(rect.width, rect.height) / 2;
	const size = radius * 2;
	canvas.width = canvas.height = size;

	ctx.clearRect(0, 0, size, size);
	ctx.save();
	ctx.beginPath();
	ctx.arc(size / 2, size / 2, radius, 0, 2 * Math.PI);
	ctx.clip();
	ctx.drawImage(
		video,
		video.videoWidth / 2 - radius,
		video.videoHeight / 2 - radius,
		size, size, 0, 0, size, size
	);
	ctx.restore();

	// Convert canvas to data URL and emit
	const imageDataUrl = canvas.toDataURL('image/png');
	capturedImageSrc.value = imageDataUrl;
	emit('captured', canvas, imageDataUrl);
}

/**
 * Reset the camera and captured image.
 */
const reset = () => capturedImageSrc.value = null;

defineExpose({ reset });
</script>

<style scoped>
.camera-capture {
	display: flex;
	align-items: center;
	flex-direction: column;
}

.camera-container {
	position: relative;
	display: block;
	margin-bottom: 20px;
	width: 100%;
	max-width: 400px;
	aspect-ratio: 1/1;
	border-radius: 50%;
}

.camera-container > * {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	box-sizing: border-box;
}

#camera-stream {
	border: 4px solid white;
	border-radius: 50%;
	object-fit: cover;
	pointer-events: none;
}

#camera-stream.hidden {
	opacity: 0;
	visibility: hidden;
}

.captured-overlay {
	border: 4px solid white;
	border-radius: 50%;
	overflow: hidden;
	z-index: 20;
}

.captured-image-overlay {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.glow-effect {
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
	0%, 100% { box-shadow: 0 0 30px #4CAF50, 0 0 60px #4CAF50; }
	50% { box-shadow: 0 0 40px #4CAF50, 0 0 80px #4CAF50; }
}

@keyframes pulse-red {
	0%, 100% { box-shadow: 0 0 30px #C62828, 0 0 60px #C62828; }
	50% { box-shadow: 0 0 40px #C62828, 0 0 80px #C62828; }
}

.overlay {
	backdrop-filter: blur(8px);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 30;
	background: rgba(255, 255, 255, 1);
	opacity: 0;
	transform: scale(0.5) rotate(-15deg);
	transition: all 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.overlay.loading {
	background: rgba(255, 255, 255, 0.5);
	opacity: 1;
	transform: scale(1) rotate(0deg);
}

.overlay.error {
	background: rgba(220, 53, 69, 0.7);
	opacity: 1;
	transform: scale(1) rotate(0deg);
	z-index: 40;
}

.error-content {
	text-align: center;
	padding: 20px;
	max-width: 280px;
	opacity: 1;
	transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s;
}

.error-message {
	font-size: 20px;
	font-weight: 700;
	margin: 0;
	line-height: 1.4;
	color: #ffffff;
	text-shadow: 0 4px 8px rgba(0, 0, 0, 0.8), 
				0 0 20px rgba(255, 255, 255, 0.3);
	letter-spacing: 0.5px;
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

.button {
	padding: 15px 30px;
	font-size: 18px;
	font-weight: bold;
	color: white;
	border: none;
	border-radius: 50px;
	cursor: pointer;
	transition: all 0.3s ease;
	text-transform: uppercase;
	letter-spacing: 1px;
	min-height: 44px;
}

.button:disabled {
	background: #cccccc;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.button.capture {
	background: linear-gradient(135deg, #4CAF50, #2E7D32);
	box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.button.capture:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.button.retry {
	background: linear-gradient(135deg, #C62828, #B71C1C);
	box-shadow: 0 4px 15px rgba(198, 40, 40, 0.3);
}

.button.retry:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(198, 40, 40, 0.4);
	background: linear-gradient(135deg, #D32F2F, #C62828);
}
</style>