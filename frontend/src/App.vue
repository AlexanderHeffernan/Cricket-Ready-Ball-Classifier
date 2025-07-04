<template>
  <nav>
    <ul>
      <li><router-link to="/">Predict</router-link></li>
      <li><router-link to="/training">Training Tool</router-link></li>
    </ul>
  </nav>
  <router-view/>
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