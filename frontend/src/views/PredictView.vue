<template>
  <div class="predict-view">
    <h1>Is your ball Cricket-Ready?</h1>
    <p>
      Take a photo with the camera below and we will determine for you
      whether your ball is match ready, or if it's better to be saved for the nets.
    </p>
    <video ref="cameraStream" id="camera-stream" autoplay muted></video>
    <canvas ref="cameraCanvas" id="camera-canvas" style="display: none;"></canvas>
    <div class="capture-container">
      <button ref="captureButton" id="capture-button" :disabled="isLoading">
        {{ isLoading ? 'Analyzing...' : 'Capture' }}
      </button>
    </div>
    <img ref="capturedImage" id="captured-image" alt="Captured Image" style="display: none;">
    
    <!-- Result Display -->
    <div v-if="predictionResult" class="result-container">
      <h2>Result:</h2>
      <div class="prediction-result">
        <p class="prediction-text">
          Your ball is: <strong>{{ predictionResult.prediction === 'match_ready' ? 'Match Ready' : 'Not Match Ready' }}</strong>
        </p>
        <p class="confidence-text">
          Confidence: {{ Math.round(predictionResult.confidence * 100) }}%
        </p>
      </div>
    </div>
    
    <!-- Error Display -->
    <div v-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const cameraStream = ref<HTMLVideoElement>()
const captureButton = ref<HTMLButtonElement>()
const cameraCanvas = ref<HTMLCanvasElement>()
const capturedImage = ref<HTMLImageElement>()
const isLoading = ref(false)
const predictionResult = ref<{prediction: string, confidence: number} | null>(null)
const error = ref<string | null>(null)

onMounted(() => {
  // Initialize camera
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        if (cameraStream.value) {
          cameraStream.value.srcObject = stream
          cameraStream.value.play()
        }
      })
      .catch((error) => {
        console.error('Error accessing camera:', error)
      })
  }

  // Add capture button event listener
  if (captureButton.value) {
    captureButton.value.addEventListener('click', capturePhoto)
  }
})

const capturePhoto = async () => {
  if (cameraStream.value && cameraCanvas.value && capturedImage.value) {
    const canvas = cameraCanvas.value
    const video = cameraStream.value
    const context = canvas.getContext('2d')
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // Draw the video frame to canvas
    context?.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    // Convert canvas to image data URL
    const imageDataUrl = canvas.toDataURL('image/png')
    
    // Display the captured image
    capturedImage.value.src = imageDataUrl
    capturedImage.value.style.display = 'block'
    
    // Send image to backend for prediction
    await sendImageForPrediction(canvas)
  }
}

const sendImageForPrediction = async (canvas: HTMLCanvasElement) => {
  try {
    isLoading.value = true
    error.value = null
    predictionResult.value = null
    
    // Convert canvas to blob
    const blob = await new Promise<Blob>((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob!)
      }, 'image/jpeg', 0.8)
    })
    
    // Create FormData
    const formData = new FormData()
    formData.append('image', blob, 'captured-image.jpg')
    
    // Send to backend
    const response = await fetch('https://localhost:8445/predict', {
      method: 'POST',
      body: formData,
      // Note: In production, you should handle SSL certificates properly
      // For now, we'll handle the self-signed certificate issue
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    predictionResult.value = result
    
  } catch (err) {
    console.error('Error sending image for prediction:', err)
    error.value = 'Failed to analyze image. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.predict-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

#camera-stream {
  width: 100%;
  max-width: 600px;
  border: 2px solid #ccc;
  border-radius: 8px;
  margin-bottom: 20px;
}

.capture-container {
  margin: 20px 0;
}

#capture-button {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

#capture-button:hover:not(:disabled) {
  background-color: #45a049;
}

#capture-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

#captured-image {
  max-width: 600px;
  width: 100%;
  border: 2px solid #ccc;
  border-radius: 8px;
  margin: 20px 0;
}

.result-container {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.prediction-result {
  margin-top: 10px;
}

.prediction-text {
  font-size: 18px;
  margin-bottom: 10px;
}

.confidence-text {
  font-size: 16px;
  color: #666;
}

.error-container {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}
</style>