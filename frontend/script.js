document.addEventListener('DOMContentLoaded', function () {
    const background = document.getElementById('background');
    const fadeOverlay = document.getElementById('fade-overlay');
    const prevBgButton = document.getElementById('prev-bg-button');
    const nextBgButton = document.getElementById('next-bg-button');
    const audioElement = document.getElementById('background-music');
    const playOverlay = document.getElementById('play-overlay');
    const playButton = document.getElementById('play-button');
    const musicButton = document.getElementById('music-button');
    const feedButton = document.getElementById('feed-button');
    const diaryButton = document.getElementById('diary-button');
    const modal = document.getElementById('upload-modal');
    const closeModalButton = document.querySelector('.close-button');
    const closeDiaryModalButton = document.querySelector('.diary-close-button');
    const fileInput = document.getElementById('file-input');
    const previewImage = document.getElementById('preview-image');
    const previewContainer = document.getElementById('preview-container');
    const diaryModal = document.getElementById('diary-modal');
    let audioContext;
    let gainNode;
    let audioInitialized = false;
    let isMusicPlaying = true;

    const backgrounds = [
        { img: 'assets/backgrounds/beach.png', music: 'assets/music/beach.wav' },
        { img: 'assets/backgrounds/club.webp', music: 'assets/music/bearclub.wav' },
        { img: 'assets/backgrounds/mountains.webp', music: 'assets/music/mountains.wav' },
        { img: 'assets/backgrounds/mystical.webp', music: 'assets/music/mystical.wav' }
    ];
    let currentBgIndex = 0;

    const updateBackgroundAndMusic = async () => {
        await fadeOut();
        background.src = backgrounds[currentBgIndex].img;
        audioElement.src = backgrounds[currentBgIndex].music;
        if (isMusicPlaying) {
            audioElement.play().catch((e) => console.log('Autoplay prevented:', e));
        } else {
            audioElement.pause();
        }
        resetVolume();
        fadeIn();
    };

    const initializeAudio = () => {
        if (!audioInitialized) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            gainNode = audioContext.createGain();
            const track = audioContext.createMediaElementSource(audioElement);
            track.connect(gainNode).connect(audioContext.destination);
            audioInitialized = true;
        }
    };

    const playAudio = () => {
        if (audioContext && audioContext.state === 'suspended') {
            audioContext.resume();
        }
        audioElement.play().catch((e) => console.log('Autoplay prevented:', e));
    };

    const toggleMusic = () => {
        if (isMusicPlaying) {
            audioElement.pause();
            musicButton.src = 'assets/icons/musicmute.png';
        } else {
            audioElement.play().catch((e) => console.log('Autoplay prevented:', e));
            musicButton.src = 'assets/icons/music.png';
        }
        isMusicPlaying = !isMusicPlaying;
    };

    const fadeOut = async () => {
        if (audioInitialized) {
            gainNode.gain.setValueAtTime(gainNode.gain.value, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 1);
        }
        fadeOverlay.style.backgroundColor = await getAverageColor(backgrounds[currentBgIndex].img);
        fadeOverlay.style.opacity = 1;
        return new Promise(resolve => setTimeout(resolve, 1000));
    };

    const fadeIn = () => {
        fadeOverlay.style.opacity = 0;
    };

    const resetVolume = () => {
        if (audioInitialized) {
            gainNode.gain.setValueAtTime(1, audioContext.currentTime);
        }
    };

    const getAverageColor = (imgSrc) => {
        return new Promise((resolve) => {
            const img = new Image();
            img.src = imgSrc;
            img.crossOrigin = "Anonymous";
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const context = canvas.getContext('2d');
                context.drawImage(img, 0, 0, img.width, img.height);
                const imageData = context.getImageData(0, 0, img.width, img.height);
                const data = imageData.data;
                let r = 0, g = 0, b = 0;
                for (let i = 0; i < data.length; i += 4) {
                    r += data[i];
                    g += data[i + 1];
                    b += data[i + 2];
                }
                r = Math.floor(r / (data.length / 4));
                g = Math.floor(g / (data.length / 4));
                b = Math.floor(b / (data.length / 4));
                resolve(`rgb(${r},${g},${b})`);
            };
        });
    };

    prevBgButton.addEventListener('click', async function () {
        currentBgIndex = (currentBgIndex - 1 + backgrounds.length) % backgrounds.length;
        fadeOverlay.style.backgroundColor = await getAverageColor(backgrounds[currentBgIndex].img);
        updateBackgroundAndMusic();
    });

    nextBgButton.addEventListener('click', async function () {
        currentBgIndex = (currentBgIndex + 1) % backgrounds.length;
        fadeOverlay.style.backgroundColor = await getAverageColor(backgrounds[currentBgIndex].img);
        updateBackgroundAndMusic();
    });

    playButton.addEventListener('click', function () {
        initializeAudio();
        playAudio();
        playOverlay.style.display = 'none';
    });

    musicButton.addEventListener('click', toggleMusic);

    feedButton.addEventListener('click', function () {
        modal.style.display = 'block';
    });

    closeModalButton.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    fileInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        handleFile(file);
    });

    const handleFile = (file) => {
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                previewImage.classList.add('has-image');
                const label = document.querySelector('#preview-container label');
                if (label) {
                    label.replaceWith(...label.childNodes);
                }
                addAnalyseButton();
                addClearButton();
            };
            reader.readAsDataURL(file);
        } else {
            clearImage();
        }
    };

    const addAnalyseButton = () => {
        const analyseButton = document.createElement('button');
        analyseButton.classList.add('analyse-button');
        analyseButton.textContent = 'Analyse';
        previewContainer.appendChild(analyseButton);
    };

    const addClearButton = () => {
        const clearButton = document.createElement('button');
        clearButton.classList.add('clear-button');
        clearButton.textContent = 'Clear Image';
        clearButton.addEventListener('click', clearImage);
        previewContainer.appendChild(clearButton);
    };

    const clearImage = () => {
        previewImage.src = 'assets/icons/camera.png';
        previewImage.classList.remove('has-image');
        const label = document.createElement('label');
        label.htmlFor = 'file-input';
        label.appendChild(previewImage);
        previewContainer.appendChild(label);
        removeAnalyseButton();
        removeClearButton();
    };

    const removeAnalyseButton = () => {
        const analyseButton = document.querySelector('.analyse-button');
        if (analyseButton) {
            analyseButton.remove();
        }
    };

    const removeClearButton = () => {
        const clearButton = document.querySelector('.clear-button');
        if (clearButton) {
            clearButton.remove();
        }
    };

    // Drag drop functionality
    previewContainer.addEventListener('dragover', function (e) {
        e.preventDefault();
        previewContainer.classList.add('dragging');
    });

    previewContainer.addEventListener('dragleave', function () {
        previewContainer.classList.remove('dragging');
    });

    previewContainer.addEventListener('drop', function (e) {
        e.preventDefault();
        previewContainer.classList.remove('dragging');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    document.addEventListener('keydown', async function (event) {
        if (event.key === 'ArrowLeft') {
            currentBgIndex = (currentBgIndex - 1 + backgrounds.length) % backgrounds.length;
            fadeOverlay.style.backgroundColor = await getAverageColor(backgrounds[currentBgIndex].img);
            updateBackgroundAndMusic();
        } else if (event.key === 'ArrowRight') {
            currentBgIndex = (currentBgIndex + 1) % backgrounds.length;
            fadeOverlay.style.backgroundColor = await getAverageColor(backgrounds[currentBgIndex].img);
            updateBackgroundAndMusic();
        }
    });

    updateBackgroundAndMusic();

    // Add event listener for the diary button to open the diary modal
    diaryButton.addEventListener('click', function () {
        diaryModal.style.display = 'block';
    });

    // Add event listener to close the modal
    closeDiaryModalButton.addEventListener('click', function () {
        diaryModal.style.display = 'none';
    });

    // Close the modal when clicking outside of it
    window.addEventListener('click', function (event) {
        if (event.target === diaryModal) {
            diaryModal.style.display = 'none';
        }
    });

});
