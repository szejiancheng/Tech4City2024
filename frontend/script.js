document.addEventListener("DOMContentLoaded", function () {
  const background = document.getElementById("background");
  const fadeOverlay = document.getElementById("fade-overlay");
  const prevBgButton = document.getElementById("prev-bg-button");
  const nextBgButton = document.getElementById("next-bg-button");
  const audioElement = document.getElementById("background-music");
  const playOverlay = document.getElementById("play-overlay");
  const playButton = document.getElementById("play-button");
  const musicButton = document.getElementById("music-button");
  const feedButton = document.getElementById("feed-button");
  const diaryButton = document.getElementById("diary-button");
  const modal = document.getElementById("upload-modal");
  const closeModalButton = document.querySelector(".close-button");
  const closeDiaryModalButton = document.querySelector(".diary-close-button");
  const fileInput = document.getElementById("file-input");
  const previewImage = document.getElementById("preview-image");
  const previewContainer = document.getElementById("preview-container");
  const diaryModal = document.getElementById("diary-modal");
  const usernameModal = document.getElementById("username-modal");
  const usernameInput = document.getElementById("username");
  const submitButton = document.getElementById("submit-button");
  const usernameDisplay = document.getElementById("username-display");
  const changeUserButton = document.getElementById("change-user-button");
  const diaryPrevButton = document.getElementById("diary-prev-button");
  const diaryNextButton = document.getElementById("diary-next-button");
  let audioContext;
  let gainNode;
  let audioInitialized = false;
  let isMusicPlaying = true;
  let currentFile;
  let imageId; // Store the image_id from the backend
  let diaryResults = [];
  let currentDiaryIndex = 0;

  const backgrounds = [
    { img: "assets/backgrounds/beach.png", music: "assets/music/beach.wav" },
    { img: "assets/backgrounds/club.webp", music: "assets/music/bearclub.wav" },
    {
      img: "assets/backgrounds/mountains.webp",
      music: "assets/music/mountains.wav",
    },
    {
      img: "assets/backgrounds/mystical.webp",
      music: "assets/music/mystical.wav",
    },
  ];
  let currentBgIndex = 0;

  const updateBackgroundAndMusic = async () => {
    await fadeOut();
    background.src = backgrounds[currentBgIndex].img;
    audioElement.src = backgrounds[currentBgIndex].music;
    if (isMusicPlaying) {
      audioElement.play().catch((e) => console.log("Autoplay prevented:", e));
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
    if (audioContext && audioContext.state === "suspended") {
      audioContext.resume();
    }
    audioElement.play().catch((e) => console.log("Autoplay prevented:", e));
  };

  const toggleMusic = () => {
    if (isMusicPlaying) {
      audioElement.pause();
      musicButton.src = "assets/icons/musicmute.png";
    } else {
      audioElement.play().catch((e) => console.log("Autoplay prevented:", e));
      musicButton.src = "assets/icons/music.png";
    }
    isMusicPlaying = !isMusicPlaying;
  };

  const fadeOut = async () => {
    if (audioInitialized) {
      gainNode.gain.setValueAtTime(
        gainNode.gain.value,
        audioContext.currentTime
      );
      gainNode.gain.exponentialRampToValueAtTime(
        0.001,
        audioContext.currentTime + 1
      );
    }
    fadeOverlay.style.backgroundColor = await getAverageColor(
      backgrounds[currentBgIndex].img
    );
    fadeOverlay.style.opacity = 1;
    return new Promise((resolve) => setTimeout(resolve, 1000));
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
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const context = canvas.getContext("2d");
        context.drawImage(img, 0, 0, img.width, img.height);
        const imageData = context.getImageData(0, 0, img.width, img.height);
        const data = imageData.data;
        let r = 0,
          g = 0,
          b = 0;
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

  prevBgButton.addEventListener("click", async function () {
    currentBgIndex =
      (currentBgIndex - 1 + backgrounds.length) % backgrounds.length;
    fadeOverlay.style.backgroundColor = await getAverageColor(
      backgrounds[currentBgIndex].img
    );
    updateBackgroundAndMusic();
  });

  nextBgButton.addEventListener("click", async function () {
    currentBgIndex = (currentBgIndex + 1) % backgrounds.length;
    fadeOverlay.style.backgroundColor = await getAverageColor(
      backgrounds[currentBgIndex].img
    );
    updateBackgroundAndMusic();
  });

  playButton.addEventListener("click", function () {
    initializeAudio();
    playAudio();
    playOverlay.style.display = "none";

    const storedUsername = localStorage.getItem("username");
    if (!storedUsername) {
      usernameModal.style.display = "block";
    }
  });

  musicButton.addEventListener("click", toggleMusic);

  feedButton.addEventListener("click", function () {
    modal.style.display = "block";
  });

  closeModalButton.addEventListener("click", function () {
    modal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  fileInput.addEventListener("change", function (event) {
    const file = event.target.files[0];
    handleFile(file);
  });

  const handleFile = (file) => {
    if (file) {
      currentFile = file;
      const reader = new FileReader();
      reader.onload = function (e) {
        previewImage.src = e.target.result;
        previewImage.classList.add("has-image");
        const label = document.querySelector("#preview-container label");
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
    const analyseButton = document.createElement("button");
    analyseButton.classList.add("analyse-button");
    analyseButton.textContent = "Analyse";
    analyseButton.addEventListener("click", sendAnalyseRequest);
    previewContainer.appendChild(analyseButton);
  };

  const addClearButton = () => {
    const clearButton = document.createElement("button");
    clearButton.classList.add("clear-button");
    clearButton.textContent = "Clear Image";
    clearButton.addEventListener("click", clearImage);
    previewContainer.appendChild(clearButton);
  };

  const clearImage = () => {
    previewImage.src = "assets/icons/camera.png";
    previewImage.classList.remove("has-image");
    const label = document.createElement("label");
    label.htmlFor = "file-input";
    label.appendChild(previewImage);
    previewContainer.appendChild(label);
    removeAnalyseButton();
    removeClearButton();
  };

  const removeAnalyseButton = () => {
    const analyseButton = document.querySelector(".analyse-button");
    if (analyseButton) {
      analyseButton.remove();
    }
  };

  const removeClearButton = () => {
    const clearButton = document.querySelector(".clear-button");
    if (clearButton) {
      clearButton.remove();
    }
  };

  previewContainer.addEventListener("dragover", function (e) {
    e.preventDefault();
    previewContainer.classList.add("dragging");
  });

  previewContainer.addEventListener("dragleave", function () {
    previewContainer.classList.remove("dragging");
  });

  previewContainer.addEventListener("drop", function (e) {
    e.preventDefault();
    previewContainer.classList.remove("dragging");
    const file = e.dataTransfer.files[0];
    handleFile(file);
  });

  document.addEventListener("keydown", async function (event) {
    if (event.key === "ArrowLeft") {
      currentBgIndex =
        (currentBgIndex - 1 + backgrounds.length) % backgrounds.length;
      fadeOverlay.style.backgroundColor = await getAverageColor(
        backgrounds[currentBgIndex].img
      );
      updateBackgroundAndMusic();
    } else if (event.key === "ArrowRight") {
      currentBgIndex = (currentBgIndex + 1) % backgrounds.length;
      fadeOverlay.style.backgroundColor = await getAverageColor(
        backgrounds[currentBgIndex].img
      );
      updateBackgroundAndMusic();
    }
  });

  updateBackgroundAndMusic();

  diaryButton.addEventListener("click", async function () {
    await fetchDiaryResults();
    diaryModal.style.display = "block";
  });

  closeDiaryModalButton.addEventListener("click", function () {
    diaryModal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === diaryModal) {
      diaryModal.style.display = "none";
    }
  });

  usernameInput.addEventListener("input", function () {
    if (usernameInput.value.trim() !== "") {
      submitButton.style.display = "block";
    } else {
      submitButton.style.display = "none";
    }
  });

  submitButton.addEventListener("click", function () {
    const username = usernameInput.value.trim();
    if (username) {
      localStorage.setItem("username", username);
      usernameDisplay.textContent = `welcome, ${username}`;
      usernameModal.style.display = "none";
    }
  });

  changeUserButton.addEventListener("click", function () {
    usernameModal.style.display = "block";
  });

  diaryPrevButton.addEventListener("click", function () {
    if (currentDiaryIndex > 0) {
      currentDiaryIndex--;
      displayDiaryResult(diaryResults[currentDiaryIndex]);
    }
  });

  diaryNextButton.addEventListener("click", function () {
    if (currentDiaryIndex < diaryResults.length - 1) {
      currentDiaryIndex++;
      displayDiaryResult(diaryResults[currentDiaryIndex]);
    }
  });

  // Checks the cache to see if there is a username
  const storedUsername = localStorage.getItem("username");
  if (storedUsername) {
    usernameDisplay.textContent = `welcome, ${storedUsername}`;
  }

  // API request for Analyse (POST)
  const sendAnalyseRequest = async () => {
    const username = localStorage.getItem("username");
    if (!username || !currentFile) {
      alert("Username or image not available");
      return;
    }

    // Create a FormData object
    const formData = new FormData();
    formData.append("user_id", username);
    formData.append("file", currentFile);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
        // mode: 'no-cors'  // Setting the mode to 'no-cors'
      });
      console.log("Response received:", response);

      if (response.ok) {
        const data = await response.json();
        console.log("Response JSON:", data);

        if (data && data[0] && data[0].image_id) {
          console.log("if");
          imageId = data[0].image_id; // Store the image_id
          updateDiaryModal(data);
          diaryModal.style.display = "block";
        } else {
          console.log("else");
          console.error("Unexpected response structure:", data);
          alert("Unexpected response structure.");
        }
      } else {
        console.error("Analysis request failed:", response.statusText);
        alert("Analysis request failed.");
      }
    } catch (error) {
      console.error("Error during analysis request:", error);
      alert("Error during analysis request.");
    }
  };

  // Fetch diary results (GET)
  const fetchDiaryResults = async () => {
    const username = localStorage.getItem("username");
    if (!username) {
      alert("Username not available");
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/results/${username}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      console.log(response);

      if (response.ok) {
        const data = await response.json();
        diaryResults = data;
        currentDiaryIndex = diaryResults.length - 1;
        if (diaryResults.length > 0) {
          displayDiaryResult(diaryResults[currentDiaryIndex]);
        } else {
          displayEmptyDiary();
        }
      } else {
        console.error("Failed to fetch diary results:", response.statusText);
        alert("Failed to fetch diary results.");
        displayEmptyDiary();
      }
    } catch (error) {
      console.error("Error fetching diary results:", error);
      alert("Error fetching diary results.");
      displayEmptyDiary();
    }
  };

  const displayEmptyDiary = () => {
    const diaryPreviewImage = document.getElementById("diary-preview-image");
    const diaryEmptyMessage = document.getElementById("diary-empty-message");
    const diaryResultsContainer = document.getElementById(
      "diary-results-container"
    );

    diaryPreviewImage.src = "assets/icons/camera.png";
    diaryPreviewImage.classList.remove("has-image");
    diaryEmptyMessage.style.display = "block";
    diaryResultsContainer.innerHTML = "";
  };

  // Edit the diary modal with the analyze results
  const updateDiaryModal = (results) => {
    const diaryPreviewImage = document.getElementById("diary-preview-image");
    const diaryEmptyMessage = document.getElementById("diary-empty-message");
    const diaryResultsContainer = document.getElementById(
      "diary-results-container"
    );

    // Update preview image
    diaryPreviewImage.src = URL.createObjectURL(currentFile);
    diaryPreviewImage.classList.add("has-image");
    diaryEmptyMessage.style.display = "none";

    // Clear previous results
    diaryResultsContainer.innerHTML = "";

    // Append result timestamp
    const resultTimestamp = document.createElement("p");
    resultTimestamp.textContent = `Result Timestamp: ${results[0].result_timestamp}`;
    diaryResultsContainer.appendChild(resultTimestamp);

    // Create table for results
    const table = document.createElement("table");
    const headerRow = document.createElement("tr");
    const classificationHeader = document.createElement("th");
    classificationHeader.textContent = "Classification Result";
    const confidenceHeader = document.createElement("th");
    confidenceHeader.textContent = "Confidence Score";
    headerRow.appendChild(classificationHeader);
    headerRow.appendChild(confidenceHeader);
    table.appendChild(headerRow);

    results.forEach((result) => {
      const row = document.createElement("tr");
      row.addEventListener("click", () => selectLabel(result.result_id));

      const classificationCell = document.createElement("td");
      classificationCell.textContent = result.label_name;
      const confidenceCell = document.createElement("td");
      confidenceCell.textContent = result.confidence_score.toFixed(2);

      row.appendChild(classificationCell);
      row.appendChild(confidenceCell);
      table.appendChild(row);
    });

    diaryResultsContainer.appendChild(table);
  };

  const displayDiaryResult = (result) => {
    const diaryPreviewImage = document.getElementById("diary-preview-image");
    const diaryEmptyMessage = document.getElementById("diary-empty-message");
    const diaryResultsContainer = document.getElementById(
      "diary-results-container"
    );
    console.log("displayDiaryResult", result);

    // change image
    const contentType = 'image/png'; // Example content type

    diaryPreviewImage.src = `data:${contentType};base64,${result.image.image_data}`;;
    diaryPreviewImage.classList.add("has-image");
    diaryEmptyMessage.style.display = "none";

    diaryResultsContainer.innerHTML = "";

    const resultTimestamp = document.createElement("p");
    resultTimestamp.textContent = `Result Timestamp: ${result.result.result_timestamp}`;
    diaryResultsContainer.appendChild(resultTimestamp);

    // show the selected choice
    const label = document.createElement("p");
    label.textContent = `Selected Label: ${result.result.label_name}`;
    diaryResultsContainer.appendChild(label);
  };

  const selectLabel = async (resultId) => {
    const username = localStorage.getItem("username");
    if (!username || !imageId || !resultId) {
      alert("Missing data to select label");
      return;
    }

    const payload = {
      user_id: username,
      image_id: imageId,
      result_id: resultId,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/select", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        console.log("Label selected successfully");
        alert("Label selected successfully");
        await fetchDiaryResults(); // Refresh diary results after selecting a label
      } else {
        console.error("Label selection failed:", response.statusText);
        alert("Label selection failed.");
      }
    } catch (error) {
      console.error("Error during label selection:", error);
      alert("Error during label selection.");
    }
  };
});
