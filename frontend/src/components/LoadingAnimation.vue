<template>
    <svg class="loading-animation" width="150" height="150" viewBox="0 0 150 150">
        <g transform="translate(45, 30)">
            <!-- Wickets -->
            <rect x="15" y="10" width="6" height="65" rx="3" ry="3" fill="#000"/>
            <rect x="27" y="10" width="6" height="65" rx="3" ry="3" fill="#000"/>
            <rect x="39" y="10" width="6" height="65" rx="3" ry="3" fill="#000"/>
            <g id="bat-group">
                <!-- Bat blade (white fill, black outline) -->
                <rect 
                    x="55" y="0" width="60" height="16" rx="3" ry="3" 
                    fill="#fff" stroke="#000" stroke-width="5"
                />
                <!-- Handle (white fill, black outline), positioned to touch blade -->
                <rect 
                    x="40" y="4.5" width="18" height="7" rx="2" ry="2" 
                    fill="#fff" stroke="#000" stroke-width="5"
                />
            </g>
            <!-- Ball -->
            <circle id="ball" cx="1" cy="37" r="7" fill="#fff" stroke="#000" stroke-width="5"/>
        </g>
    </svg>
</template>

<style scoped>
.loading-animation {
    transform: scale(2.0);
}
#bat-group {
    transform-box: fill-box;
    transform-origin: 5px 5px;
    animation: bat-swing 1.5s infinite;
}

@keyframes bat-swing {
    0%   { transform: translate(8px, 15px) rotate(135deg); }
    45%  { transform: translate(8px, 15px) rotate(135deg); }
    55%  { transform: translate(8px, 15px) rotate(110deg); }
    60%  { transform: translate(8px, 15px) rotate(145deg); }
    70%  { transform: translate(8px, 15px) rotate(135deg); }
    100% { transform: translate(8px, 15px) rotate(135deg); }
}

#ball {
    transform-box: fill-box;
    animation: ball-hit 1.5s infinite;
}

@keyframes ball-hit {
    0%   { transform: translate(50px, 70px) scale(0);  }
    30%  { transform: translate(0, 0) scale(1); }
    45%  { transform: translate(0, 0) scale(1); }
    55%  { transform: translate(3px, 5px) scale(1); }
    100%  { transform: translate(-15px, -35px) scale(0); }
}
</style>