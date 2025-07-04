<template>
  <div class="predict-view">
    <h1>Is your ball Cricket-Ready?</h1>
    <p>
      Take a photo with the camera below and we will determine for you
      whether your ball is match ready, or if it's better to be saved for the nets.
    </p>
    
    <!-- Camera Container with Overlay -->
    <div class="camera-container">
      <video ref="cameraStream" id="camera-stream" 

             muted 
             playsinline
             webkit-playsinline="true"
             x-webkit-airplay="deny"
             preload="auto"
             :class="{ 'hidden': capturedImageSrc }"></video>
      
      <!-- Captured Image Overlay -->
      <div v-if="capturedImageSrc" class="captured-overlay"
           :class="{ 'loading': isLoading, 'match-ready': predictionResult?.prediction === 'match_ready', 'not-match-ready': predictionResult?.prediction === 'not_match_ready' }">
        <img :src="capturedImageSrc" alt="Captured Image" class="captured-image-overlay">
        
        <!-- Loading Spinner -->
        <div v-if="isLoading" class="loading-spinner">
          <div class="spinner"></div>
          <p>Analyzing...</p>
        </div>
      </div>
      
      <!-- Invisible overlay to block video interactions -->
      <div class="video-blocker" v-if="!capturedImageSrc"></div>
      
      <!-- Glow Effect -->
      <div class="glow-effect" 
           :class="{ 'match-ready': predictionResult?.prediction === 'match_ready', 'not-match-ready': predictionResult?.prediction === 'not_match_ready' }">
      </div>
    </div>
    
    <canvas ref="cameraCanvas" id="camera-canvas" style="display: none;"></canvas>
    
    <!-- Capture Button -->
    <div class="capture-container" v-if="!predictionResult">
      <button @click="capturePhoto" id="capture-button" :disabled="isLoading">
        {{ isLoading ? 'Analyzing...' : 'Capture' }}
      </button>
    </div>
    
    <!-- Result Display -->
    <div v-if="predictionResult" class="result-container">
      <h2>Result:</h2>
      <div class="prediction-result">
        <p class="prediction-text"
           :class="predictionResult.prediction === 'match_ready' ? 'match-ready' : 'not-match-ready'">
          Your ball is: <strong>{{ predictionResult.prediction === 'match_ready' ? 'Match Ready' : 'Not Match Ready' }}</strong>
        </p>
        <p class="confidence-text">
          Confidence: {{ Math.round(predictionResult.confidence * 100) }}%
        </p>
      </div>
      
      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="takeAnotherPhoto" class="action-btn primary">Take Another Photo</button>
        <button @click="retryAnalysis" class="action-btn secondary">Retry Analysis</button>
      </div>
    </div>
    
    <!-- Error Display -->
    <div v-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button @click="retryAnalysis" class="retry-btn">Retry</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'

const cameraStream = ref<HTMLVideoElement>()
const cameraCanvas = ref<HTMLCanvasElement>()
const capturedImageSrc = ref<string | null>(null)
const isLoading = ref(false)
const predictionResult = ref<{prediction: string, confidence: number} | null>(null)
const error = ref<string | null>(null)
const currentStream = ref<MediaStream | null>(null)

onMounted(() => {
  initializeCamera()
})

const initializeCamera = async () => {
  try {
    // Check if we're on localhost or HTTPS
    const isSecureContext = location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1'
    
    if (!isSecureContext) {
      error.value = 'Camera access requires HTTPS. Please use https:// or access via localhost.'
      return
    }

    // Check if getUserMedia is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      error.value = 'Camera access not supported in this browser.'
      return
    }

    // Request camera with rear-facing preference
    const constraints = {
      video: {
        facingMode: { ideal: 'environment' }, // Prefer rear camera
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    }

    const stream = await navigator.mediaDevices.getUserMedia(constraints)
    currentStream.value = stream
    
    if (cameraStream.value) {
      cameraStream.value.srcObject = stream
      
      // Aggressively remove all control-related attributes
      cameraStream.value.removeAttribute('controls')
      cameraStream.value.removeAttribute('controlsList')
      cameraStream.value.setAttribute('playsinline', 'true')
      cameraStream.value.setAttribute('webkit-playsinline', 'true')
      cameraStream.value.setAttribute('x-webkit-airplay', 'deny')
      cameraStream.value.setAttribute('disablePictureInPicture', 'true')
      
      // Wait for the video to be ready before playing
      await new Promise((resolve) => {
        cameraStream.value!.onloadedmetadata = () => {
          resolve(true)
        }
      })
      
      // Use nextTick to ensure DOM is updated
      await nextTick()
      
      // Play the video
      try {
        await cameraStream.value.play()
        
        // After playing, hide any controls that might have appeared
        setTimeout(() => {
          if (cameraStream.value) {
            cameraStream.value.removeAttribute('controls')
            cameraStream.value.style.pointerEvents = 'none'
          }
        }, 100)
        
      } catch (playError) {
        console.warn('Autoplay failed, user interaction required:', playError)
      }
    }
    
  } catch (err: any) {
    console.error('Error accessing camera:', err)
    
    if (err.name === 'NotAllowedError') {
      error.value = 'Camera access denied. Please allow camera permissions and refresh the page.'
    } else if (err.name === 'NotFoundError') {
      error.value = 'No camera found on this device.'
    } else if (err.name === 'NotSupportedError') {
      error.value = 'Camera access requires HTTPS connection.'
    } else if (err.name === 'OverconstrainedError') {
      // Try with front camera if rear camera fails
      try {
        const fallbackConstraints = {
          video: {
            facingMode: 'user',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        }
        const fallbackStream = await navigator.mediaDevices.getUserMedia(fallbackConstraints)
        currentStream.value = fallbackStream
        
        if (cameraStream.value) {
          cameraStream.value.srcObject = fallbackStream
          cameraStream.value.removeAttribute('controls')
          cameraStream.value.setAttribute('playsinline', 'true')
          cameraStream.value.setAttribute('webkit-playsinline', 'true')
          await cameraStream.value.play()
        }
      } catch (fallbackErr) {
        error.value = 'Failed to access camera. Please check permissions and try again.'
      }
    } else {
      error.value = 'Failed to access camera. Please check permissions and try again.'
    }
  }
}

const capturePhoto = async () => {
  if (cameraStream.value && cameraCanvas.value) {
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
    
    // Display the captured image overlay
    capturedImageSrc.value = imageDataUrl
    
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
    const response = await fetch('https://192.168.1.95:8445/predict', {
      method: 'POST',
      body: formData,
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

const takeAnotherPhoto = () => {
  // Reset all states
  capturedImageSrc.value = null
  predictionResult.value = null
  error.value = null
  isLoading.value = false
}

const retryAnalysis = async () => {
  if (cameraCanvas.value) {
    await sendImageForPrediction(cameraCanvas.value)
  }
}

// Cleanup on unmount
onUnmounted(() => {
  if (currentStream.value) {
    currentStream.value.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
:root {
  --cricket-brown: #795548;
  --cricket-red: #C62828;
  --primary-green: #2E7D32;
  --secondary-green: #4CAF50;
  --background: #F8F9FA;
}

.predict-view {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  background-color: var(--background);
  min-height: 100vh;
}

.camera-container {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

#camera-stream {
  width: 100%;
  max-width: 400px;
  aspect-ratio: 1/1;
  border: 4px solid var(--cricket-brown);
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 
    0 0 20px rgba(121, 85, 72, 0.3),
    inset 0 0 20px rgba(0, 0, 0, 0.1);
  background-color: #f5f5f5;
  transition: all 0.3s ease;
  /* Safari-specific fixes */
  -webkit-appearance: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: transparent;
  pointer-events: none;
}

/* Invisible overlay to block all video interactions */
.video-blocker {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  background: transparent;
  border-radius: 50%;
  pointer-events: all;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* Ultra-aggressive CSS to hide ALL video controls for Safari */
#camera-stream::-webkit-media-controls,
#camera-stream::-webkit-media-controls-panel,
#camera-stream::-webkit-media-controls-play-button,
#camera-stream::-webkit-media-controls-start-playback-button,
#camera-stream::-webkit-media-controls-overlay-play-button,
#camera-stream::-webkit-media-controls-enclosure,
#camera-stream::-webkit-media-controls-timeline,
#camera-stream::-webkit-media-controls-current-time-display,
#camera-stream::-webkit-media-controls-time-remaining-display,
#camera-stream::-webkit-media-controls-mute-button,
#camera-stream::-webkit-media-controls-volume-slider,
#camera-stream::-webkit-media-controls-fullscreen-button {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
  pointer-events: none !important;
  -webkit-appearance: none !important;
}

/* Additional Safari-specific hiding */
#camera-stream::-webkit-media-controls-overlay-enclosure {
  display: none !important;
}

#camera-stream::-webkit-media-controls-start-playback-button {
  display: none !important;
}

/* For Firefox */
#camera-stream::-moz-media-controls {
  display: none !important;
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
  transition: all 0.5s ease;
  border: 4px solid var(--cricket-brown);
  box-shadow: 
    0 0 20px rgba(121, 85, 72, 0.3),
    inset 0 0 20px rgba(0, 0, 0, 0.1);
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  box-shadow: 0 0 30px var(--secondary-green), 0 0 60px var(--secondary-green);
  animation: pulse-green 2s ease-in-out infinite;
}

.glow-effect.not-match-ready {
  opacity: 1;
  box-shadow: 0 0 30px var(--cricket-red), 0 0 60px var(--cricket-red);
  animation: pulse-red 2s ease-in-out infinite;
}

@keyframes pulse-green {
  0%, 100% { box-shadow: 0 0 30px var(--secondary-green), 0 0 60px var(--secondary-green); }
  50% { box-shadow: 0 0 40px var(--secondary-green), 0 0 80px var(--secondary-green); }
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 30px var(--cricket-red), 0 0 60px var(--cricket-red); }
  50% { box-shadow: 0 0 40px var(--cricket-red), 0 0 80px var(--cricket-red); }
}

.capture-container {
  margin: 20px 0;
}

#capture-button {
  padding: 15px 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, var(--secondary-green), var(--primary-green));
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
  text-transform: uppercase;
  letter-spacing: 1px;
  /* Better mobile touch target */
  min-height: 44px;
  min-width: 44px;
  /* Re-enable pointer events for button */
  pointer-events: auto;
}

#capture-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

#capture-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.result-container {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 15px;
  border: 2px solid #dee2e6;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.prediction-text {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
}

.prediction-text.match-ready {
  color: var(--primary-green);
}

.prediction-text.not-match-ready {
  color: var(--cricket-red);
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
  /* Better mobile touch target */
  min-height: 44px;
  pointer-events: auto;
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--secondary-green), var(--primary-green));
  color: white;
  box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
}

.action-btn.secondary {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  box-shadow: 0 2px 10px rgba(108, 117, 125, 0.3);
}

.action-btn.secondary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.4);
}

.error-container {
  margin: 20px 0;
  padding: 15px;
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  border: 2px solid #f5c6cb;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(198, 40, 40, 0.2);
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: var(--cricket-red);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  /* Better mobile touch target */
  min-height: 44px;
  pointer-events: auto;
}

.retry-btn:hover {
  background: #b71c1c;
  transform: translateY(-1px);
}

h1 {
  color: var(--primary-green);
  font-size: 2.5em;
  margin-bottom: 15px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

p {
  color: #555;
  font-size: 1.1em;
  line-height: 1.6;
  margin-bottom: 30px;
}

/* Responsive design */
@media (max-width: 768px) {
  .predict-view {
    padding: 15px;
  }
  
  #camera-stream {
    max-width: 350px;
  }
  
  h1 {
    font-size: 2em;
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