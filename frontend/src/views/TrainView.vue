<template>
    <div class="train-view">
        <h1>Training Tool</h1>
        <p>Help improve our classifier by taking photos and labeling them.</p>

        <CameraComponent :is-loading="isLoading" :error="error" :show-retry="!!error"
			@captured="handleCapture" @cameraError="handleError" @ready="emitCameraReady" @retry="retry" ref="camera" />

        <!-- Training Labels -->
		<div v-if="capturedData && !submitted" class="label-container">
			<h3>Is this ball match-ready?</h3>
			<div class="label-buttons">
				<button @click="submitLabel('match_ready')" class="label-btn match-ready">
					✓ Match Ready
				</button>
				<button @click="submitLabel('not_match_ready')" class="label-btn not-match-ready">
					✗ Not Match Ready
				</button>
			</div>
			<button @click="reset" class="retake-btn">Retake Photo</button>
		</div>

		<!-- Training Success -->
		<div v-if="submitted" class="success-container">
			<h3>✓ Thank you!</h3>
			<p>Your training data has been submitted successfully.</p>
			<button @click="reset" class="action-btn primary">Take Another Photo</button>
		</div>
    </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import CameraComponent from '@/components/CameraComponent.vue';

const emit = defineEmits(['camera-ready']);

function emitCameraReady() { emit('camera-ready'); }

const isLoading = ref(false);
const error = ref<string | null>(null);
const submitted = ref(false);
const capturedData = ref<{ canvas: HTMLCanvasElement, imageDataUrl: string } | null>(null);
const camera = ref<InstanceType<typeof CameraComponent>>();

const handleCapture = (canvas: HTMLCanvasElement, imageDataUrl: string) => {
	capturedData.value = { canvas, imageDataUrl };
};

const handleError = (message: string) => {
	error.value = message;
};

const submitLabel = async (label: string) => {
	if (!capturedData.value) return;

	try {
		isLoading.value = true;
		error.value = null;

		const blob = await new Promise<Blob>((resolve) => {
			if (capturedData.value) {
				capturedData.value.canvas.toBlob((blob) => {
					if (blob) resolve(blob);
				}, 'image/jpeg', 0.8);
			}
		});

		const formData = new FormData();
		formData.append('image', blob, 'training-image.jpg');
		formData.append('label', label);

		const response = await fetch(`${process.env.VUE_APP_BACKEND_URL}/training`, {
			method: 'POST',
			headers: {
				'ngrok-skip-browser-warning': 'true',
			},
			body: formData,
		});

		if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

		submitted.value = true;

	} catch (e: unknown) {
		console.error('Training error:', error);
		const err = e as Error;
		if (err.name === 'TypeError' && err.message.includes('Load failed')) {
			error.value = 'ERROR: Backend service unavailable. Please try again later.';
		} else {
			error.value = 'ERROR: Failed to submit training data. Please try again.';
		}
	} finally {
		isLoading.value = false;
	}
};

const reset = () => {
	capturedData.value = null;
	submitted.value = false;
	error.value = null;
	isLoading.value = false;
	camera.value?.reset();
};

const retry = async () => {
	error.value = null;
	await new Promise(resolve => setTimeout(resolve, 500));
};

</script>

<style scoped>
html {
	scroll-behavior: smooth;
}

.train-view {
	max-width: 600px;
	margin: 0 auto;
	padding: 20px;
	text-align: center;
	min-height: 100vh;
	box-sizing: border-box;
}

.label-container,
.success-container {
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

.label-buttons {
	display: flex;
	gap: 10px;
	justify-content: center;
	flex-wrap: wrap;
}

.label-btn {
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

.label-btn.match-ready {
	background: linear-gradient(135deg, #4CAF50, #2E7D32);
	color: white;
	box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
}

.label-btn.not-match-ready {
	background: linear-gradient(135deg, #C62828, #b71c1c);
	color: white;
	box-shadow: 0 2px 10px rgba(198, 40, 40, 0.3);
}

.retake-btn {
	padding: 8px 16px;
	background: #6c757d;
	color: white;
	border: none;
	border-radius: 20px;
	cursor: pointer;
	transition: all 0.3s ease;
	min-height: 44px;
}

.success-container {
	background: linear-gradient(135deg, #e8f5e8, #c8e6c8);
	color: #2E7D32;
	border: 2px solid #4CAF50;
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
	.train-view {
		padding: 15px 25px;
	}

	h1 {
		font-size: 1.5em;
	}

	p {
		font-size: 1em;
	}

	.label-buttons {
		flex-direction: column;
		align-items: center;
	}

	.label-btn {
		width: 200px;
	}
}
</style>