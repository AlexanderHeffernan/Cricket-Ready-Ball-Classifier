<template>
    <div class="view">
        <h1>Training Tool</h1>
        <p>Help improve our classifier by taking photos and labeling them.</p>

        <CameraComponent :is-loading="isLoading" :error="error" :show-retry="!!error"
			@captured="handleCapture" @cameraError="handleError" @ready="emitCameraReady" @retry="retry" ref="camera" />

        <!-- Training Labels -->
		<div v-if="capturedData && !submitted" class="container">
			<h3>Is this ball match-ready?</h3>
			<div class="label-buttons">
				<button @click="submitLabel('match_ready')" class="btn positive">
					✓ Match Ready
				</button>
				<button @click="submitLabel('not_match_ready')" class="btn negative">
					✗ Not Match Ready
				</button>
			</div>
			<button @click="reset" class="btn">Retake Photo</button>
		</div>

		<!-- Training Success -->
		<div v-if="submitted" class="container success-container">
			<h3>✓ Thank you!</h3>
			<p>Your training data has been submitted successfully.</p>
			<button @click="reset" class="btn">Take Another Photo</button>
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
.label-buttons {
	display: flex;
	gap: 10px;
	justify-content: center;
	flex-wrap: wrap;
}

.success-container {
	background: linear-gradient(135deg, #e8f5e8, #c8e6c8);
	color: #2E7D32;
	border: 2px solid #4CAF50;
}

@media (max-width: 768px) {
	.label-buttons {
		flex-direction: column;
		align-items: center;
	}

	.label-btn {
		width: 200px;
	}
}
</style>