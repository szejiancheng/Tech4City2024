document.addEventListener('DOMContentLoaded', function () {
    const background = document.getElementById('background');
    const prevBgButton = document.getElementById('prev-bg-button');
    const nextBgButton = document.getElementById('next-bg-button');
    const audioElement = document.getElementById('background-music');
    const playOverlay = document.getElementById('play-overlay');
    const playButton = document.getElementById('play-button');
    let audioContext;
    let audioInitialized = false;

    const backgrounds = [
        { img: 'assets/backgrounds/beach.png', music: 'assets/music/beach.wav' },
        { img: 'assets/backgrounds/club.webp', music: 'assets/music/bearclub.wav' },
        { img: 'assets/backgrounds/mountains.webp', music: 'assets/music/mountains.wav' },
        { img: 'assets/backgrounds/mystical.webp', music: 'assets/music/mystical.wav' }
    ];
    let currentBgIndex = 0;

    const updateBackgroundAndMusic = () => {
        background.src = backgrounds[currentBgIndex].img;
        audioElement.src = backgrounds[currentBgIndex].music;
        playAudio();
    };

    const initializeAudio = () => {
        if (!audioInitialized) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const track = audioContext.createMediaElementSource(audioElement);
            track.connect(audioContext.destination);
            audioInitialized = true;
        }
    };

    const playAudio = () => {
        if (audioContext && audioContext.state === 'suspended') {
            audioContext.resume();
        }
        audioElement.play().catch((e) => console.log('Autoplay prevented:', e));
    };

    prevBgButton.addEventListener('click', function () {
        currentBgIndex = (currentBgIndex - 1 + backgrounds.length) % backgrounds.length;
        updateBackgroundAndMusic();
    });

    nextBgButton.addEventListener('click', function () {
        currentBgIndex = (currentBgIndex + 1) % backgrounds.length;
        updateBackgroundAndMusic();
    });

    // Initialize audio context and play audio on play button click
    playButton.addEventListener('click', function () {
        initializeAudio();
        playAudio();
        playOverlay.style.display = 'none';
    });

    // Load the first background and music initially
    updateBackgroundAndMusic();
});
