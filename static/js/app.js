// SmartMeetingAI Frontend JavaScript - Multiple Reel Generation
class SmartMeetingAI {
  constructor() {
    this.currentFile = null;
    this.isProcessing = false;
    this.statusCheckInterval = null;
    this.reels = [];
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadReels();
    this.updateReelsGallery();
  }

  bindEvents() {
    console.log("Binding events...");

    // File input change
    const videoFileInput = document.getElementById("videoFile");
    if (videoFileInput) {
      videoFileInput.addEventListener("change", (e) => {
        console.log("File input changed:", e.target.files[0]);
        this.handleFileSelect(e.target.files[0]);
      });
    } else {
      console.error("videoFile input not found!");
    }

    // Drag and drop events
    const uploadZone = document.getElementById("uploadZone");
    const fileInput = document.getElementById("videoFile");

    if (!uploadZone) {
      console.error("uploadZone not found!");
      return;
    }

    if (!fileInput) {
      console.error("fileInput not found!");
      return;
    }

    uploadZone.addEventListener("dragover", (e) => {
      console.log("Drag over event triggered");
      e.preventDefault();
      e.stopPropagation();
      uploadZone.classList.add("drag-over");
    });

    uploadZone.addEventListener("dragenter", (e) => {
      console.log("Drag enter event triggered");
      e.preventDefault();
      e.stopPropagation();
      uploadZone.classList.add("drag-over");
    });

    uploadZone.addEventListener("dragleave", (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!uploadZone.contains(e.relatedTarget)) {
        uploadZone.classList.remove("drag-over");
      }
    });

    uploadZone.addEventListener("drop", (e) => {
      console.log("Drop event triggered");
      e.preventDefault();
      e.stopPropagation();
      uploadZone.classList.remove("drag-over");

      const files = e.dataTransfer.files;
      console.log("Dropped files:", files);

      if (files.length > 0) {
        this.handleFileSelect(files[0]);
      }
    });

    // Click to browse functionality
    uploadZone.addEventListener("click", () => {
      console.log("Upload zone clicked");
      fileInput.click();
    });

    // Upload button
    document.getElementById("uploadBtn").addEventListener("click", () => {
      this.uploadFile();
    });

    // Remove file button
    document.getElementById("removeFile").addEventListener("click", () => {
      this.removeFile();
    });

    // Generate button
    document.getElementById("generateBtn").addEventListener("click", () => {
      this.generateReels();
    });

    // Reel count change
    document.getElementById("reelCount").addEventListener("change", (e) => {
      this.updateReelConfigs(parseInt(e.target.value));
    });

    // Modal close
    document.getElementById("modalClose").addEventListener("click", () => {
      this.closeModal();
    });

    // Close modal on outside click
    window.addEventListener("click", (e) => {
      const modal = document.getElementById("reelModal");
      if (e.target === modal) {
        this.closeModal();
      }
    });
  }

  handleFileSelect(file) {
    if (!file) return;

    console.log(
      "Processing file:",
      file.name,
      "Type:",
      file.type,
      "Size:",
      file.size
    );

    if (!this.validateFile(file)) {
      this.showError(
        "Please select a valid video file (MP4, AVI, MOV, MKV, WMV, FLV, WEBM)"
      );
      return;
    }

    // Check file size (2GB limit)
    const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
    if (file.size > maxSize) {
      this.showError("File size must be less than 2GB");
      return;
    }

    this.currentFile = file;
    this.showFilePreview(file);
    document.getElementById("uploadBtn").disabled = false;
    this.showSuccess(`File "${file.name}" selected successfully!`);
  }

  validateFile(file) {
    const allowedTypes = [
      "video/mp4",
      "video/avi",
      "video/mov",
      "video/mkv",
      "video/wmv",
      "video/flv",
      "video/webm",
    ];
    const allowedExtensions = [
      ".mp4",
      ".avi",
      ".mov",
      ".mkv",
      ".wmv",
      ".flv",
      ".webm",
    ];

    // Check MIME type
    const isValidType = allowedTypes.includes(file.type);

    // Check file extension as backup
    const fileName = file.name.toLowerCase();
    const isValidExtension = allowedExtensions.some((ext) =>
      fileName.endsWith(ext)
    );

    return isValidType || isValidExtension;
  }

  showFilePreview(file) {
    const previewContainer = document.getElementById("filePreview");
    const fileName = document.getElementById("fileName");
    const fileSize = document.getElementById("fileSize");

    fileName.textContent = file.name;
    fileSize.textContent = this.formatFileSize(file.size);

    previewContainer.style.display = "block";
    document.getElementById("uploadZone").style.display = "none";

    // Update hidden file input
    const fileInput = document.getElementById("videoFile");
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;

    console.log("File preview shown for:", file.name);
  }

  removeFile() {
    this.currentFile = null;
    document.getElementById("filePreview").style.display = "none";
    document.getElementById("uploadZone").style.display = "block";
    document.getElementById("videoFile").value = "";
    document.getElementById("uploadBtn").disabled = true;

    // Reset drag-over state
    document.getElementById("uploadZone").classList.remove("drag-over");
  }

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  async uploadFile() {
    if (!this.currentFile) return;

    const formData = new FormData();
    formData.append("video", this.currentFile);

    try {
      this.showLoading(true);
      this.isProcessing = true;

      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        this.showReelOptions(result.file_id);
        this.showSuccess("Video uploaded successfully!");
      } else {
        throw new Error(result.message || "Upload failed");
      }
    } catch (error) {
      console.error("Upload error:", error);
      this.showError("Upload failed: " + error.message);
    } finally {
      this.showLoading(false);
      this.isProcessing = false;
    }
  }

  showReelOptions(fileId) {
    console.log("showReelOptions called with fileId:", fileId);
    document.getElementById("progressSection").style.display = "none";
    document.getElementById("reelOptions").style.display = "block";
    document.getElementById("reelsGallery").style.display = "none";
    document.getElementById("generateBtn").setAttribute("data-file-id", fileId);

    // Show poster and blog cards and their empty states
    document.getElementById("posterCard").style.display = "block";
    document.getElementById("blogCard").style.display = "block";
    document.getElementById("posterEmpty").style.display = "block";
    document.getElementById("blogEmpty").style.display = "block";
    document.getElementById("posterSection").style.display = "none";
    document.getElementById("blogSection").style.display = "none";

    // Enable poster/blog buttons and store fileId
    this.posterBlogFileId = fileId;
    const generatePosterBtn = document.getElementById("generatePosterBtn");
    const generateBlogBtn = document.getElementById("generateBlogBtn");
    if (generatePosterBtn) generatePosterBtn.disabled = false;
    if (generateBlogBtn) generateBlogBtn.disabled = false;

    // Bind poster/blog button events (only once)
    if (!this.posterBlogEventsBound) {
      if (generatePosterBtn) {
        generatePosterBtn.addEventListener("click", () =>
          this.handleGeneratePoster()
        );
      }
      if (generateBlogBtn) {
        generateBlogBtn.addEventListener("click", () =>
          this.handleGenerateBlog()
        );
      }
      this.posterBlogEventsBound = true;
    }

    // Initialize with 1 reel configuration
    this.updateReelConfigs(1);
  }

  updateReelConfigs(count) {
    const container = document.getElementById("reelConfigsContainer");
    container.innerHTML = "";

    for (let i = 1; i <= count; i++) {
      const configDiv = document.createElement("div");
      configDiv.className = "reel-config";
      configDiv.innerHTML = `
                <div class="reel-config-header">
                    <h4 class="reel-config-title">Reel ${i}</h4>
                </div>
                <div class="reel-config-options">
                    <div class="config-row">
                        <div class="form-group">
                            <label for="duration${i}">Duration</label>
                            <select id="duration${i}" class="form-select">
                                <option value="30">30 seconds</option>
                                <option value="45">45 seconds</option>
                                <option value="60">60 seconds</option>
                                <option value="90">90 seconds</option>
                                <option value="120">120 seconds</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="style${i}">Style</label>
                            <select id="style${i}" class="form-select">
                                <option value="casual">Casual</option>
                                <option value="professional">Professional</option>
                                <option value="creative">Creative</option>
                                <option value="minimalist">Minimalist</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="caption${i}">Caption (optional)</label>
                        <textarea id="caption${i}" class="form-textarea" placeholder="Enter a caption for this reel..."></textarea>
                    </div>
                    <div class="reel-config-social">
                        <h4>Target Platforms</h4>
                        <div class="platform-grid">
                            <div class="platform-option">
                                <input type="checkbox" id="instagram${i}" class="platform-checkbox" checked>
                                <label for="instagram${i}" class="platform-label">
                                    <i class="fab fa-instagram"></i>
                                    Instagram
                                </label>
                            </div>
                            <div class="platform-option">
                                <input type="checkbox" id="facebook${i}" class="platform-checkbox">
                                <label for="facebook${i}" class="platform-label">
                                    <i class="fab fa-facebook"></i>
                                    Facebook
                                </label>
                            </div>
                            <div class="platform-option">
                                <input type="checkbox" id="linkedin${i}" class="platform-checkbox">
                                <label for="linkedin${i}" class="platform-label">
                                    <i class="fab fa-linkedin"></i>
                                    LinkedIn
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            `;
      container.appendChild(configDiv);
    }

    // Show/hide add button
    const addBtn = document.getElementById("addReelConfigBtn");
    if (count < 4) {
      addBtn.style.display = "block";
      addBtn.onclick = () => {
        const newCount = Math.min(count + 1, 4);
        document.getElementById("reelCount").value = newCount;
        this.updateReelConfigs(newCount);
      };
    } else {
      addBtn.style.display = "none";
    }
  }

  async generateReels() {
    const fileId = document
      .getElementById("generateBtn")
      .getAttribute("data-file-id");
    if (!fileId) return;

    const reelCount = parseInt(document.getElementById("reelCount").value);
    const configs = [];

    for (let i = 1; i <= reelCount; i++) {
      const duration = document.getElementById(`duration${i}`).value;
      const style = document.getElementById(`style${i}`).value;
      const caption = document.getElementById(`caption${i}`).value;

      // Get platform selections
      const platforms = [];
      if (document.getElementById(`instagram${i}`).checked)
        platforms.push("instagram");
      if (document.getElementById(`facebook${i}`).checked)
        platforms.push("facebook");
      if (document.getElementById(`linkedin${i}`).checked)
        platforms.push("linkedin");

      configs.push({
        duration: parseInt(duration),
        style: style,
        caption: caption,
        platforms: platforms,
      });
    }

    try {
      this.isProcessing = true;

      // Show progress section and hide reel options
      console.log("Showing progress section...");
      const progressSection = document.getElementById("progressSection");
      const reelOptions = document.getElementById("reelOptions");
      const reelsGallery = document.getElementById("reelsGallery");

      if (progressSection) {
        progressSection.style.display = "block";
        console.log("Progress section displayed");
      } else {
        console.error("Progress section element not found!");
      }

      if (reelOptions) {
        reelOptions.style.display = "none";
        console.log("Reel options hidden");
      }

      if (reelsGallery) {
        reelsGallery.style.display = "none";
        console.log("Reels gallery hidden");
      }

      const response = await fetch("/generate-reels", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          file_id: fileId,
          configs: configs,
        }),
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        this.startStatusCheck(fileId);
        this.showSuccess("Reel generation started!");
      } else {
        throw new Error(result.message || "Generation failed");
      }
    } catch (error) {
      console.error("Generation error:", error);
      this.showError("Generation failed: " + error.message);
      // Hide progress section on error
      document.getElementById("progressSection").style.display = "none";
      document.getElementById("reelOptions").style.display = "block";
    } finally {
      this.isProcessing = false;
    }
  }

  startStatusCheck(fileId) {
    console.log("startStatusCheck called with fileId:", fileId);

    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
    }

    let checkCount = 0;
    const maxChecks = 30; // Maximum 60 seconds (30 * 2 seconds)

    this.statusCheckInterval = setInterval(async () => {
      checkCount++;
      console.log(
        `Status check ${checkCount}/${maxChecks} for fileId: ${fileId}`
      );

      try {
        const response = await fetch(`/status/${fileId}`);
        if (!response.ok) {
          throw new Error(`Status check failed: ${response.status}`);
        }

        const result = await response.json();
        console.log("Status check result:", result);

        if (result.status === "completed") {
          console.log("Generation completed, handling completion...");
          clearInterval(this.statusCheckInterval);
          this.handleGenerationComplete(result);
        } else if (result.status === "failed") {
          console.log("Generation failed:", result.message);
          clearInterval(this.statusCheckInterval);
          this.showError("Generation failed: " + result.message);
          // Hide progress section on failure
          document.getElementById("progressSection").style.display = "none";
          document.getElementById("reelOptions").style.display = "block";
        } else {
          console.log("Updating progress with status:", result.status);
          this.updateProgress(result);
        }
      } catch (error) {
        console.error("Status check error:", error);
        // Stop checking if there's an error
        clearInterval(this.statusCheckInterval);
        this.showError("Status check failed: " + error.message);
        // Hide progress section on error
        document.getElementById("progressSection").style.display = "none";
        document.getElementById("reelOptions").style.display = "block";
      }

      // Stop checking after max attempts
      if (checkCount >= maxChecks) {
        clearInterval(this.statusCheckInterval);
        this.showError(
          "Generation timed out. Please check the status manually."
        );
        // Hide progress section on timeout
        document.getElementById("progressSection").style.display = "none";
        document.getElementById("reelOptions").style.display = "block";
      }
    }, 2000);
  }

  updateProgress(data) {
    console.log("updateProgress called with data:", data);

    const progressFill = document.getElementById("progressFill");
    const progressText = document.getElementById("progressText");
    const progressStatus = document.getElementById("progressStatus");

    if (!progressFill || !progressText || !progressStatus) {
      console.error("Progress elements not found:", {
        progressFill: !!progressFill,
        progressText: !!progressText,
        progressStatus: !!progressStatus,
      });
      return;
    }

    if (data.progress !== undefined) {
      console.log(`Updating progress to ${data.progress}%`);
      progressFill.style.width = `${data.progress}%`;
      progressText.textContent = `${data.progress}%`;
    }

    if (data.message) {
      console.log(`Updating status message: ${data.message}`);
      progressStatus.textContent = data.message;
    }

    // Log individual reel progress
    if (data.reels) {
      data.reels.forEach((reel) => {
        console.log(`Reel ${reel.id}: ${reel.progress}% - ${reel.message}`);
      });
    }
  }

  handleGenerationComplete(data) {
    console.log("Processing completed, data:", data);

    if (data.reels && data.reels.length > 0) {
      console.log("Found reels in response:", data.reels);

      data.reels.forEach((reel) => {
        console.log("Processing reel:", reel);

        // Add timestamp to make reel names distinguishable
        const timestamp = new Date().toLocaleString();
        const reelData = {
          id: reel.id,
          file_id: data.file_id,
          name: `${reel.id} (${timestamp})`,
          duration: reel.duration,
          style: reel.style,
          url: reel.url,
          thumbnail: reel.thumbnail,
          created_at: new Date().toISOString(),
        };

        console.log("Adding reel to gallery:", reelData);
        this.addReelToGallery(reelData);
      });
    }

    // Hide progress section
    document.getElementById("progressSection").style.display = "none";

    // Show the reels gallery
    this.showReelsGallery();
    this.showSuccess("All reels generated successfully!");
  }

  addReelToGallery(reel) {
    this.reels.push(reel);
    this.saveReels();
    this.updateReelsGallery();
    console.log("Total reels:", this.reels.length);
  }

  updateReelsGallery() {
    const reelsGrid = document.getElementById("reelsGrid");
    const reelsCount = document.getElementById("reelsCount");
    const emptyState = document.getElementById("emptyState");

    if (!reelsGrid || !reelsCount || !emptyState) {
      console.log("Reels gallery elements not found, retrying in 200ms...");
      setTimeout(() => this.updateReelsGallery(), 200);
      return;
    }

    reelsCount.textContent = `${this.reels.length} reel${
      this.reels.length !== 1 ? "s" : ""
    }`;

    if (this.reels.length === 0) {
      reelsGrid.innerHTML = "";
      reelsGrid.appendChild(emptyState);
      emptyState.style.display = "block";
    } else {
      emptyState.style.display = "none";
      reelsGrid.innerHTML = "";

      this.reels.forEach((reel) => {
        const reelCard = this.createReelCard(reel);
        reelsGrid.appendChild(reelCard);
      });
    }
  }

  createReelCard(reel) {
    const card = document.createElement("div");
    card.className = "reel-card";
    card.innerHTML = `
            <div class="reel-thumbnail">
                <img src="${
                  reel.thumbnail || "/static/thumbnails/default.jpg"
                }" alt="Reel thumbnail">
                <div class="reel-overlay">
                    <button class="btn btn-sm btn-primary" onclick="app.previewReel('${
                      reel.id
                    }')">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="app.downloadReel('${
                      reel.id
                    }')">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
            <div class="reel-info">
                <h4>${reel.name}</h4>
                <p>Duration: ${reel.duration}s | Style: ${reel.style}</p>
                <small>${new Date(reel.created_at).toLocaleString()}</small>
            </div>
        `;
    return card;
  }

  previewReel(reelId) {
    const reel = this.reels.find((r) => r.id === reelId);
    if (!reel) return;

    const modal = document.getElementById("reelModal");
    const modalContent = modal.querySelector(".modal-content");

    modalContent.innerHTML = `
            <div class="modal-header">
                <h3>${reel.name}</h3>
                <button class="modal-close" onclick="app.closeModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <video controls width="100%">
                    <source src="${reel.url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="reel-details">
                    <p><strong>Duration:</strong> ${reel.duration} seconds</p>
                    <p><strong>Style:</strong> ${reel.style}</p>
                    <p><strong>Created:</strong> ${new Date(
                      reel.created_at
                    ).toLocaleString()}</p>
                </div>
            </div>
        `;

    modal.style.display = "block";
  }

  downloadReel(reelId) {
    const reel = this.reels.find((r) => r.id === reelId);
    if (!reel) return;

    const link = document.createElement("a");
    link.href = reel.url;
    link.download = `${reel.name}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  closeModal() {
    document.getElementById("reelModal").style.display = "none";
  }

  showReelsGallery() {
    console.log("Showing reels gallery...");
    document.getElementById("progressSection").style.display = "none";
    document.getElementById("reelOptions").style.display = "none";
    document.getElementById("reelsGallery").style.display = "block";

    // Update the gallery with current reels
    this.updateReelsGallery();
  }

  loadReels() {
    const saved = localStorage.getItem("smartMeetingReels");
    if (saved) {
      try {
        this.reels = JSON.parse(saved);
      } catch (e) {
        console.error("Error loading reels:", e);
        this.reels = [];
      }
    }
  }

  saveReels() {
    localStorage.setItem("smartMeetingReels", JSON.stringify(this.reels));
  }

  showLoading(show) {
    document.getElementById("loadingOverlay").style.display = show
      ? "block"
      : "none";
  }

  showSuccess(message) {
    this.showNotification(message, "success");
  }

  showError(message) {
    this.showNotification(message, "error");
  }

  showNotification(message, type) {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.add("show");
    }, 100);

    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }

  async handleGeneratePoster() {
    const fileId = this.posterBlogFileId;
    if (!fileId) return;
    this.showLoading(true);
    try {
      // Always generate transcript first (idempotent)
      const transcriptRes = await fetch("/generate-transcript", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId }),
      });
      const transcriptData = await transcriptRes.json();
      if (!transcriptData.success) throw new Error(transcriptData.message);

      // Now generate poster
      const posterRes = await fetch("/generate-poster", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId }),
      });
      const posterData = await posterRes.json();
      if (!posterData.success) throw new Error(posterData.message);

      // Show poster in UI
      this.showPoster(posterData.poster);
      this.showSuccess("Poster generated successfully!");
    } catch (err) {
      this.showError("Poster generation failed: " + err.message);
    } finally {
      this.showLoading(false);
    }
  }

  async handleGenerateBlog() {
    const fileId = this.posterBlogFileId;
    if (!fileId) return;
    this.showLoading(true);
    try {
      // Always generate transcript first (idempotent)
      const transcriptRes = await fetch("/generate-transcript", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId }),
      });
      const transcriptData = await transcriptRes.json();
      if (!transcriptData.success) throw new Error(transcriptData.message);

      // Now generate blog
      const blogRes = await fetch("/generate-blog", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId }),
      });
      const blogData = await blogRes.json();
      if (!blogData.success) throw new Error(blogData.message);

      // Show blog in UI
      this.showBlog(blogData.blog);
      this.showSuccess("Blog article generated successfully!");
    } catch (err) {
      this.showError("Blog generation failed: " + err.message);
    } finally {
      this.showLoading(false);
    }
  }

  showPoster(poster) {
    const posterSection = document.getElementById("posterSection");
    const posterImage = document.getElementById("posterImage");
    const posterPlaceholder = document.getElementById("posterPlaceholder");
    const downloadPosterBtn = document.getElementById("downloadPosterBtn");
    if (posterSection) posterSection.style.display = "block";
    if (posterPlaceholder) posterPlaceholder.style.display = "none";
    if (posterImage && poster.image_url) {
      posterImage.src = poster.image_url;
      posterImage.style.display = "block";
    }
    if (downloadPosterBtn && poster.image_url) {
      downloadPosterBtn.style.display = "inline-flex";
      downloadPosterBtn.onclick = () => {
        const link = document.createElement("a");
        link.href = poster.image_url;
        link.download = "meeting-poster.jpg";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      };
    }
  }

  showBlog(blog) {
    const blogSection = document.getElementById("blogSection");
    const blogContent = document.getElementById("blogContent");
    const blogEmpty = document.getElementById("blogEmpty");
    if (blogSection) blogSection.style.display = "block";
    if (blogEmpty) blogEmpty.style.display = "none";
    if (blogContent && blog.blog_content) {
      blogContent.innerHTML = blog.blog_content.replace(/\n/g, "<br>");
    }
  }
}

// Initialize the application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    window.app = new SmartMeetingAI();
  }, 100);
});
