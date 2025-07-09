<template>
  <div class="background-image"></div>
  <div class="background-overlay"></div>
  <div class="app-container">
    <router-view/>
  </div>
</template>

<style>
:root {
  --primary-green: #2E7D32;
  --secondary-green: #4CAF50;
  --accent-red: #C62828;
  --background: #F8F9FA;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: var(--background);
  min-height: 100vh;
  min-height: 100dvh;
}

/* Fixed background image using a div instead of CSS background */
.background-image {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  height: 100lvh;
  background-image: url('./assets/background.jpg');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  z-index: 0;
}

/* White gradient overlay */
.background-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, 
    rgba(255, 255, 255, 1) 0%,
    rgba(255, 255, 255, 0.8) 25%,
    rgba(255, 255, 255, 0.4) 40%,
    rgba(255, 255, 255, 0) 50%
  );
  z-index: 1;
  pointer-events: none;
}

.app-container {
  position: relative;
  z-index: 2;
  min-height: 100vh;
}

h1 {
  color: var(--primary-green);
  text-align: center;
  margin-top: 20px;
}

p {
  color: #333;
  text-align: center;
  margin: 10px 0;
}
</style>