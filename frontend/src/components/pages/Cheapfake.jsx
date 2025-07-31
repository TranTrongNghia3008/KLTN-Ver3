import { useState } from "react";
import { FiUpload, FiX, FiSearch } from "react-icons/fi";

export default function Cheapfake() {
  const [image, setImage] = useState(null);
  const [caption, setCaption] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [evidenceLinks, setEvidenceLinks] = useState([]);

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setImage({
        file,
        url: URL.createObjectURL(file),
      });
      setResult(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setImage({
        file,
        url: URL.createObjectURL(file),
      });
      setResult(null);
    }
  };

  const handleCheck = () => {
    if (!image || !caption.trim()) return;

    setLoading(true);
    setResult(null);

    // Giả lập gọi API
    setTimeout(() => {
      // Kết quả giả lập
      const isFake = Math.random() > 0.5;
      const links = [
        "https://www.snopes.com/fact-check/trump-rally-arrested-tweet/",
        "https://www.reuters.com/article/world/fact-check-trump-did-not-tweet-about-arresting-ticketholders-who-failed-to-atte-idUSKBN23U2JY/",
        "https://www.teenvogue.com/story/tiktok-teens-fake-tickets-trump-tulsa-rally",
      ];
      setResult(isFake ? "Not out of context" : "Out of context");
      setEvidenceLinks(links);
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Cheapfake Detection</h1>
      <p className="text-gray-600 mb-6">
        This tool helps you verify if an image and its accompanying caption are potentially misleading or out of context.
        Upload an image, provide a related caption, and the system will assess the integrity of the content and suggest sources.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Image Upload Section */}
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex flex-col items-center justify-center relative bg-gray-50 min-h-[70vh]"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          {!image ? (
            <>
              <FiUpload size={48} className="text-gray-400 mb-2" />
              <p className="text-gray-500">Drag & drop an image or click to upload</p>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
            </>
          ) : (
            <div className="relative w-full">
              <img src={image.url} alt="Uploaded" className="rounded-lg w-full object-contain max-h-96" />
              <button
                onClick={() => setImage(null)}
                className="absolute top-2 right-2 bg-white rounded-full p-1 shadow hover:bg-gray-100"
              >
                <FiX size={20} />
              </button>
            </div>
          )}
        </div>

        {/* Caption + Action Section */}
        <div className="flex flex-col gap-4">
          <label className="font-medium text-gray-700">Caption</label>
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            rows={6}
            placeholder="Enter the caption describing this image..."
            className="border border-gray-300 rounded p-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            onClick={handleCheck}
            disabled={!image || !caption.trim() || loading}
            className="bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2 flex items-center gap-2 justify-center transition disabled:opacity-50"
          >
            <FiSearch size={18} />
            {loading ? "Checking..." : "Check"}
          </button>

          {/* Result */}
          {result && (
            <div
              className={`mt-4 p-4 rounded text-white ${
                result === "Out of context" ? "bg-red-500" : "bg-green-500"
              }`}
            >
              <strong>Result:</strong> {result}
            </div>
          )}

          {/* Evidence Links */}
          {result && evidenceLinks.length > 0 && (
            <div className="mt-4">
              <p className="font-medium text-gray-700 mb-2">Related Sources:</p>
              <ul className="list-disc list-inside text-blue-600 underline space-y-1">
                {evidenceLinks.map((link, idx) => (
                  <li key={idx}>
                    <a href={link} target="_blank" rel="noopener noreferrer">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
