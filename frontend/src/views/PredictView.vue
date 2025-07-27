<template>
	<div class="predict-view">
		<h1>Is your ball Cricket-Ready?</h1>
		<p>Take a photo and we will determine if your ball is match ready.</p>

		<CameraComponent :is-loading="isLoading" :glow-class="glowClass" :error="error" :show-retry="!!error"
			@captured="handleCapture" @cameraError="handleError" @retry="retry" @ready="emitCameraReady" ref="camera" />

		<!-- Prediction Results -->
		<div v-if="predictionResult" class="result-container" ref="resultContainer">
			<h2>Result:</h2>
			<div class="prediction-result">
				<p class="prediction-text" :class="predictionResult.prediction">
					Your ball is: <strong>{{ predictionResult.prediction === 'match_ready' ? 'Match Ready' : 'Not Match Ready' }}</strong>
				</p>
				<p class="confidence-text">
					Confidence: {{ Math.round(predictionResult.confidence * 100) }}%
				</p>
			</div>
			<div class="action-buttons">
				<button @click="reset" class="action-btn primary">Take Another Photo</button>
				<button @click="retryPrediction" class="action-btn secondary">Retry Analysis</button>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, defineEmits } from 'vue';
import CameraComponent from '@/components/CameraComponent.vue';

type PredictionResult = { prediction: 'match_ready' | 'not_match_ready', confidence: number };

const emit = defineEmits(['camera-ready']);

function emitCameraReady() { emit('camera-ready'); }

const isLoading = ref(false);
const error = ref<string | null>(null);
const predictionResult = ref<PredictionResult | null>(null);
const submitted = ref(false);
const capturedData = ref<{ canvas: HTMLCanvasElement, imageDataUrl: string } | null>(null);
const camera = ref<InstanceType<typeof CameraComponent>>();
const resultContainer = ref<HTMLElement>();

const glowClass = computed(() => {
	if (predictionResult.value) {
		return predictionResult.value.prediction === 'match_ready' ? 'match-ready' : 'not-match-ready';
	}
	return '';
});

const scrollToResult = async () => {
	await nextTick();
	if (resultContainer.value) {
		resultContainer.value.scrollIntoView({
			behavior: 'smooth',
			block: 'start'
		});
	}
};

const handleCapture = (canvas: HTMLCanvasElement, imageDataUrl: string) => {
	capturedData.value = { canvas, imageDataUrl };
	sendPrediction(canvas);
};

const handleError = (message: string) => {
	error.value = message;
};

const sendPrediction = async (canvas: HTMLCanvasElement) => {
	try {
		isLoading.value = true;
		error.value = null;

		const blob = await new Promise<Blob>((resolve) => {
			canvas.toBlob((blob) => {
				if (blob) resolve(blob)
			}, 'image/jpeg', 0.8);
		});

		const formData = new FormData();
		formData.append('image', blob, 'captured-image.jpg');

		const response = await fetch(`${process.env.VUE_APP_BACKEND_URL}/predict`, {
			method: 'POST',
			headers: {
				'ngrok-skip-browser-warning': 'true',
			},
			body: formData,
		});

		if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

		predictionResult.value = await response.json();

		await scrollToResult();

	} catch (e: unknown) {
		console.error('Prediction error:', error);
		const err = e as Error;
		if (err.name === 'TypeError' && err.message.includes('Load failed')) {
			error.value = 'ERROR: Backend service unavailable. Please try again later.';
		} else {
			error.value = 'ERROR: Failed to analyze image. Please try again.';
		}
	} finally {
		isLoading.value = false;
	}
};

const reset = () => {
	capturedData.value = null;
	predictionResult.value = null;
	submitted.value = false;
	error.value = null;
	isLoading.value = false;
	camera.value?.reset();
};

const retry = async () => {
	error.value = null;
	await new Promise(resolve => setTimeout(resolve, 500));
	if (capturedData.value) {
		sendPrediction(capturedData.value.canvas);
	}
};

const retryPrediction = () => {
	if (capturedData.value) {
		sendPrediction(capturedData.value.canvas);
	}
};
</script>

<style scoped>
html {
	scroll-behavior: smooth;
}

.predict-view {
	max-width: 600px;
	margin: 0 auto;
	padding: 20px;
	text-align: center;
	min-height: 100vh;
	box-sizing: border-box;
}

.result-container {
	margin: 20px 0;
	padding: 20px;
	background-color: #f8f9fa;
	border-radius: 15px;
	border: 2px solid #dee2e6;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
	animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
	from {
		opacity: 0;
		transform: translateY(20px);
	}

	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.prediction-text {
	font-size: 20px;
	font-weight: bold;
	margin-bottom: 10px;
}

.prediction-text.match_ready {
	color: #2E7D32;
}

.prediction-text.not_match_ready {
	color: #C62828;
}

.confidence-text {
	font-size: 16px;
	color: #666;
	margin-bottom: 20px;
}

.action-buttons {
	display: flex;
	gap: 10px;
	justify-content: center;
	flex-wrap: wrap;
}

.action-btn {
	padding: 10px 20px;
	font-size: 14px;
	font-weight: bold;
	border: none;
	border-radius: 25px;
	cursor: pointer;
	transition: all 0.3s ease;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	min-height: 44px;
}

.action-btn.primary {
	background: linear-gradient(135deg, #4CAF50, #2E7D32);
	color: white;
	box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
}

.action-btn.secondary {
	background: linear-gradient(135deg, #6c757d, #495057);
	color: white;
	box-shadow: 0 2px 10px rgba(108, 117, 125, 0.3);
}

h1 {
	color: #2E7D32;
	font-size: 2.5em;
	margin-bottom: 15px;
}

p {
	color: #555;
	font-size: 1.1em;
	line-height: 1.6;
	margin-bottom: 30px;
}

@media (max-width: 768px) {
	.predict-view {
		padding: 15px 25px;
	}

	h1 {
		font-size: 1.5em;
	}

	p {
		font-size: 1em;
	}

	.action-buttons {
		flex-direction: column;
		align-items: center;
	}

	.action-btn {
		width: 200px;
	}
}
</style>