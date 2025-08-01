<template>
    <div class="last-update-indicator" :class="{ hidden: hidden }">
        <div class="update-text">
            <span style="font-weight: bold">Last updated: <span style="font-size:11px;">(NZ time)</span></span> <br/>{{  buildDate  }}
        </div>
        <span class="eye-icon" @click="toggleHidden" title="Hide">
          <!-- Eye icon -->
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </span>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const buildDate = __BUILD_DATE__ || 'n/a';
const STORAGE_KEY = 'lastUpdateHidden';

const hidden = ref(true);

onMounted(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved !== null) {
        hidden.value = saved === 'true';
    }
});

function toggleHidden() {
    hidden.value = !hidden.value;
    localStorage.setItem(STORAGE_KEY, hidden.value.toString());
}
</script>

<style scoped>
.last-update-indicator {
    position: fixed;
    right: 16px;
    bottom: 16px;
    background: rgba(46, 125, 50, 0.9);
    padding: 6px 14px;
    border-radius: 16px;
    z-index: 9999;
    box-shadow: 0 2px 8px rgba(46, 125, 50, 0.08);
    display: flex;
    align-items: center;
    gap: 10px;
    height: 42px;
    box-sizing: border-box;
    transition: opacity 0.3s ease;
}

.last-update-indicator.hidden {
    opacity: 0.5;
}

.last-update-indicator.hidden:hover {
    opacity: 1;
}

.last-update-indicator .update-text {
    color: #fff;
    font-size: 13px;
    width: 140px;
    max-width: 140px;
    transition: max-width 0.3s ease, opacity 0.3s ease, margin 0.3s;
    opacity: 1;
    margin-right: 0;
    white-space: nowrap;
    overflow: hidden;
}

.last-update-indicator.hidden .update-text {
    max-width: 0;
    opacity: 0;
    margin-right: -10px;
}

.eye-icon {
    display: flex;
    cursor: pointer;
    transition: opacity 0.3s ease;
}

.eye-icon:hover {
    opacity: 0.8;
}
</style>