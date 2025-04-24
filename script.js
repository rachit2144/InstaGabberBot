async function download() {
    const url = document.getElementById('reelUrl').value.trim();
    const format = document.querySelector('input[name="format"]:checked').value;
    const message = document.getElementById('message');
  
    if (!url) {
      message.textContent = "⚠️ Please enter a reel URL.";
      return;
    }
  
    message.textContent = "⏳ Processing...";
  
    try {
      const response = await fetch("http://localhost:5000/download", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ url, format })
      });
  
      if (!response.ok) {
        throw new Error("Download failed");
      }
  
      const blob = await response.blob();
      const fileUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = fileUrl;
      a.download = `reel.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      message.textContent = "✅ Download started!";
    } catch (err) {
      console.error(err);
      message.textContent = "❌ Failed to download. Please try again.";
    }
  }
  