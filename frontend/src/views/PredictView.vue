<template>
  <div class="cricket-view">
    <div class="mode-selector">
      <button @click="mode = 'predict'" :class="{ active: mode === 'predict' }">
        Predict
      </button>
      <button @click="mode = 'train'" :class="{ active: mode === 'train' }">
        Train
      </button>
    </div>

    <h1>{{ mode === 'predict' ? 'Is your ball Cricket-Ready?' : 'Training Tool' }}</h1>
    <p>{{ modeDescription }}</p>

    <CameraComponent
      :is-loading="isLoading" 
      :loading-text="loadingText"
      :glow-class="glowClass"
      @captured="handleCapture"
      @error="handleError"
      ref="camera" />

    <!-- Prediction Results -->
    <div v-if="mode === 'predict' && predictionResult" class="result-container" ref="resultContainer">
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

    <!-- Training Labels -->
    <div v-if="mode === 'train' && capturedData && !submitted" class="label-container">
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
    <div v-if="mode === 'train' && submitted" class="success-container">
      <h3>✓ Thank you!</h3>
      <p>Your training data has been submitted successfully.</p>
      <button @click="reset" class="action-btn primary">Take Another Photo</button>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button @click="retry" class="retry-btn">Retry</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import CameraComponent from '@/components/CameraComponent.vue'

type Mode = 'predict' | 'train'
type PredictionResult = { prediction: 'match_ready' | 'not_match_ready', confidence: number }

const mode = ref<Mode>('predict')
const isLoading = ref(false)
const error = ref<string | null>(null)
const predictionResult = ref<PredictionResult | null>(null)
const submitted = ref(false)
const capturedData = ref<{ canvas: HTMLCanvasElement, imageDataUrl: string } | null>(null)
const camera = ref<InstanceType<typeof CameraComponent>>()
const resultContainer = ref<HTMLElement>()

const modeDescription = computed(() => 
  mode.value === 'predict' 
    ? 'Take a photo and we will determine if your ball is match ready.'
    : 'Help improve our classifier by taking photos and labeling them.'
)

const loadingText = computed(() => 
  mode.value === 'predict' ? 'Analyzing...' : 'Submitting...'
)

const glowClass = computed(() => {
  if (mode.value === 'predict' && predictionResult.value) {
    return predictionResult.value.prediction === 'match_ready' ? 'match-ready' : 'not-match-ready'
  }
  return ''
})

const scrollToResult = async () => {
	await nextTick()
	if (resultContainer.value) {
		resultContainer.value.scrollIntoView({
			behavior: 'smooth',
			block: 'start'
		})
	}
}

const handleCapture = (canvas: HTMLCanvasElement, imageDataUrl: string) => {
  capturedData.value = { canvas, imageDataUrl }
  
  if (mode.value === 'predict') {
    sendPrediction(canvas)
  }
}

const handleError = (message: string) => {
  error.value = message
}

const sendPrediction = async (canvas: HTMLCanvasElement) => {
  try {
    isLoading.value = true
    error.value = null
    
    const blob = await new Promise<Blob>((resolve) => {
      canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', 0.8)
    })
    
    const formData = new FormData()
    formData.append('image', blob, 'captured-image.jpg')
    
    const response = await fetch('https://192.168.1.95:8445/predict', {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    predictionResult.value = await response.json()

	await scrollToResult()
    
  } catch (err: any) {
    console.error('Prediction error:', err)
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      error.value = 'Backend service unavailable. Please try again later.'
    } else {
      error.value = 'Failed to analyze image. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

const submitLabel = async (label: string) => {
  if (!capturedData.value) return
  
  try {
    isLoading.value = true
    error.value = null
    
    const blob = await new Promise<Blob>((resolve) => {
      capturedData.value!.canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', 0.8)
    })
    
    const formData = new FormData()
    formData.append('image', blob, 'training-image.jpg')
    formData.append('label', label)
    
    const response = await fetch('https://192.168.1.95:8445/training', {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    submitted.value = true
    
  } catch (err) {
    console.error('Training error:', err)
    error.value = 'Failed to submit training data. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const reset = () => {
  capturedData.value = null
  predictionResult.value = null
  submitted.value = false
  error.value = null
  isLoading.value = false
  camera.value?.reset()
}

const retry = () => {
  if (mode.value === 'predict' && capturedData.value) {
    sendPrediction(capturedData.value.canvas)
  } else {
    error.value = null
  }
}

const retryPrediction = () => {
  if (capturedData.value) {
    sendPrediction(capturedData.value.canvas)
  }
}
</script>

<style scoped>
html {
	scroll-behavior: smooth;
}
.cricket-view {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  min-height: 100vh;
}

.mode-selector {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.mode-selector button {
  padding: 10px 20px;
  font-size: 16px;
  font-weight: bold;
  border: 2px solid #2E7D32;
  background: white;
  color: #2E7D32;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-selector button.active {
  background: #2E7D32;
  color: white;
}

.result-container, .label-container, .success-container {
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

.action-buttons, .label-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn, .label-btn {
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

.action-btn.primary, .label-btn.match-ready {
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  color: white;
  box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
}

.action-btn.secondary {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  box-shadow: 0 2px 10px rgba(108, 117, 125, 0.3);
}

.label-btn.not-match-ready {
  background: linear-gradient(135deg, #C62828, #b71c1c);
  color: white;
  box-shadow: 0 2px 10px rgba(198, 40, 40, 0.3);
}

.retake-btn, .retry-btn {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 44px;
}

.error-container {
  margin: 20px 0;
  padding: 15px;
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  border: 2px solid #f5c6cb;
  border-radius: 15px;
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
  .cricket-view {
    padding: 15px 25px;
  }
  
  h1 {
    font-size: 1.5em;
  }

  p {
	font-size: 1em;
  }
  
  .action-buttons, .label-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn, .label-btn {
    width: 200px;
  }
}
</style>