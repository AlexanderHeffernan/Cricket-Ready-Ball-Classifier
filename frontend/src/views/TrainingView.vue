<template>
  <div class="training-view">
    <h1>Training Tool</h1>
    <p>
      Help improve our cricket ball classifier by taking photos and labeling them.
      Your contributions will help train our neural network to be more accurate.
    </p>
    
    <!-- Camera Container with Overlay -->
    <div class="camera-container">
      <video ref="cameraStream" id="camera-stream" 
             autoplay 
             muted 
             playsinline
             webkit-playsinline="true"
             x-webkit-airplay="deny"
             preload="auto"
             :class="{ 'hidden': capturedImageSrc }"></video>
      
      <!-- Captured Image Overlay -->
      <div v-if="capturedImageSrc" class="captured-overlay">
        <img :src="capturedImageSrc" alt="Captured Image" class="captured-image-overlay">
      </div>
      
      <!-- Invisible overlay to block video interactions -->
      <div class="video-blocker" v-if="!capturedImageSrc"></div>
    </div>
    
    <canvas ref="cameraCanvas" id="camera-canvas" style="display: none;"></canvas>
    
    <!-- Capture Button -->
    <div class="capture-container" v-if="!capturedImageSrc">
      <button @click="capturePhoto" id="capture-button">
        Capture Photo
      </button>
    </div>
    
    <!-- Label Assignment -->
    <div v-if="capturedImageSrc && !isLoading && !submitted" class="label-container">
      <h3>Is this ball match-ready?</h3>
      <div class="label-buttons">
        <button @click="submitLabel('match_ready')" class="label-btn match-ready">
          ✓ Match Ready
        </button>
        <button @click="submitLabel('not_match_ready')" class="label-btn not-match-ready">
          ✗ Not Match Ready
        </button>
      </div>
      <button @click="retakePhoto" class="retake-btn">
        Retake Photo
      </button>
    </div>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Submitting your training data...</p>
    </div>
    
    <!-- Success Message -->
    <div v-if="submitted" class="success-container">
      <h3>✓ Thank you!</h3>
      <p>Your training data has been submitted successfully.</p>
      <button @click="takeAnotherPhoto" class="action-btn primary">
        Take Another Photo
      </button>
    </div>
    
    <!-- Error Display -->
    <div v-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button @click="retrySubmission" class="retry-btn">Retry</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'

const cameraStream = ref<HTMLVideoElement>()
const cameraCanvas = ref<HTMLCanvasElement>()
const capturedImageSrc = ref<string | null>(null)
const isLoading = ref(false)
const submitted = ref(false)
const error = ref<string | null>(null)
const currentStream = ref<MediaStream | null>(null)
const currentLabel = ref<string | null>(null)

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
    
    if (!context) return
    
    // Get the video element's display dimensions
    const videoRect = video.getBoundingClientRect()
    const videoDisplayWidth = videoRect.width
    const videoDisplayHeight = videoRect.height
    
    // Calculate the circle dimensions (same as CSS)
    const circleSize = Math.min(videoDisplayWidth, videoDisplayHeight)
    const circleRadius = circleSize / 2
    
    // Calculate the scale factor between video display and actual video dimensions
    const scaleX = video.videoWidth / videoDisplayWidth
    const scaleY = video.videoHeight / videoDisplayHeight
    
    // Calculate the center point of the video in actual video coordinates
    const centerX = video.videoWidth / 2
    const centerY = video.videoHeight / 2
    
    // Calculate the actual radius in video coordinates
    const actualRadius = circleRadius * Math.min(scaleX, scaleY)
    
    // Set canvas to be square with the size of the circular crop
    const cropSize = actualRadius * 2
    canvas.width = cropSize
    canvas.height = cropSize
    
    // Clear the canvas
    context.clearRect(0, 0, cropSize, cropSize)
    
    // Create a circular clipping path
    context.save()
    context.beginPath()
    context.arc(cropSize / 2, cropSize / 2, actualRadius, 0, 2 * Math.PI)
    context.clip()
    
    // Draw the circular portion of the video
    context.drawImage(
      video,
      centerX - actualRadius, // source x
      centerY - actualRadius, // source y
      cropSize, // source width
      cropSize, // source height
      0, // destination x
      0, // destination y
      cropSize, // destination width
      cropSize // destination height
    )
    
    context.restore()
    
    // Convert canvas to image data URL
    const imageDataUrl = canvas.toDataURL('image/png')
    
    // Display the captured image overlay
    capturedImageSrc.value = imageDataUrl
  }
}

const submitLabel = async (label: string) => {
  currentLabel.value = label
  await sendTrainingData(label)
}

const sendTrainingData = async (label: string) => {
  try {
    isLoading.value = true
    error.value = null
    
    if (!cameraCanvas.value) {
      throw new Error('No image captured')
    }
    
    // Convert canvas to blob
    const blob = await new Promise<Blob>((resolve) => {
      cameraCanvas.value!.toBlob((blob) => {
        resolve(blob!)
      }, 'image/jpeg', 0.8)
    })
    
    // Create FormData
    const formData = new FormData()
    formData.append('image', blob, 'training-image.jpg')
    formData.append('label', label)
    
    // Send to backend training endpoint
    const response = await fetch('https://192.168.68.58:8445/training', {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('Training data submitted:', result)
    
    submitted.value = true
    
  } catch (err) {
    console.error('Error submitting training data:', err)
    error.value = 'Failed to submit training data. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const retakePhoto = () => {
  capturedImageSrc.value = null
  currentLabel.value = null
  error.value = null
}

const takeAnotherPhoto = () => {
  // Reset all states
  capturedImageSrc.value = null
  currentLabel.value = null
  submitted.value = false
  error.value = null
  isLoading.value = false
}

const retrySubmission = async () => {
  if (currentLabel.value) {
    await sendTrainingData(currentLabel.value)
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

.training-view {
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
  min-height: 44px;
  min-width: 44px;
  pointer-events: auto;
}

#capture-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.label-container {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 15px;
  border: 2px solid #dee2e6;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.label-container h3 {
  color: var(--cricket-brown);
  margin-bottom: 20px;
  font-size: 1.5em;
}

.label-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.label-btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-height: 44px;
  min-width: 150px;
  pointer-events: auto;
}

.label-btn.match-ready {
  background: linear-gradient(135deg, var(--secondary-green), var(--primary-green));
  color: white;
  box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
}

.label-btn.match-ready:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
}

.label-btn.not-match-ready {
  background: linear-gradient(135deg, #C62828, #b71c1c);
  color: white;
  box-shadow: 0 2px 10px rgba(198, 40, 40, 0.3);
}

.label-btn.not-match-ready:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(198, 40, 40, 0.4);
}

.retake-btn {
  padding: 8px 16px;
  font-size: 14px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 44px;
  pointer-events: auto;
}

.retake-btn:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.loading-container {
  margin: 20px 0;
  padding: 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(76, 175, 80, 0.3);
  border-top: 4px solid var(--secondary-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-container {
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(135deg, #e8f5e8, #c8e6c8);
  color: var(--primary-green);
  border: 2px solid var(--secondary-green);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
}

.success-container h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
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
  pointer-events: auto;
  margin-top: 15px;
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
  .training-view {
    padding: 15px;
  }
  
  #camera-stream {
    max-width: 350px;
  }
  
  h1 {
    font-size: 2em;
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