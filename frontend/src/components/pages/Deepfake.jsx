import { useState } from "react";
import { FiUpload, FiX, FiSearch, FiVideo } from "react-icons/fi";

export default function Deepfake() {
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const handleVideoUpload = (e) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("video/")) {
      setVideo({
        file,
        name: file.name,
        url: URL.createObjectURL(file),
      });
      setResults([]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("video/")) {
      setVideo({
        file,
        name: file.name,
        url: URL.createObjectURL(file),
      });
      setResults([]);
    }
  };

  const handleCheck = () => {
    if (!video) return;
    setLoading(true);
    setResults([]);

    // Giả lập API
    setTimeout(() => {
      const fakeResults = [
        { timestamp: "00:00–00:05", label: "REAL", start: 0, end: 5 },
        { timestamp: "00:05–00:10", label: "FAKE", start: 5, end: 10 },
        { timestamp: "00:10–00:15", label: "REAL", start: 10, end: 15 },
      ];
      setResults(fakeResults);
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="p-6 w-full mx-auto h-[calc(100vh-100px)] flex flex-col">
      <h1 className="text-2xl font-bold mb-4">Deepfake Detection</h1>
      <p className="text-gray-600 mb-6">
        Upload a video to analyze and detect deepfake segments. Each result is labeled as <strong>REAL</strong> or <strong>FAKE</strong> and includes a playable segment preview.
      </p>

      <div className="flex flex-1 gap-6">
        {/* Left: Upload & Preview */}
        <div className="w-full md:w-1/2 flex flex-col">
          {/* Upload Zone */}
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50 mb-4 relative"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
          >
            {!video ? (
              <div className="text-center">
                <FiUpload size={48} className="text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Drag & drop a video or click to upload</p>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleVideoUpload}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <span className="truncate">{video.name}</span>
                <button
                  onClick={() => {
                    URL.revokeObjectURL(video.url);
                    setVideo(null);
                    setResults([]);
                  }}
                  className="p-1 rounded-full hover:bg-gray-200"
                >
                  <FiX size={18} />
                </button>
              </div>
            )}
          </div>

          {/* Preview Video */}
          {video && (
            <div className="mb-4">
              <p className="text-sm text-gray-500 mb-2">Preview:</p>
              <video src={video.url} controls className="w-full rounded shadow" />
            </div>
          )}

          {/* Check Button */}
          <div>
            <button
              disabled={!video || loading}
              onClick={handleCheck}
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-md flex items-center gap-2 transition disabled:opacity-50"
            >
              <FiSearch size={18} />
              {loading ? "Analyzing..." : "Check Deepfake"}
            </button>
          </div>
        </div>

        {/* Right: Results */}
        <div className="w-full md:w-1/2 overflow-y-auto max-h-[calc(100vh-220px)] pr-1">
            <h2 className="text-xl font-semibold mb-4">Detection Results:</h2>
            {results.length > 0 ? (
            <div className="grid grid-cols-1 gap-4">
            {results.map((res, idx) => (
                <div
                key={idx}
                className={`border-l-4 p-4 rounded shadow bg-white ${
                    res.label === "FAKE" ? "border-red-500" : "border-green-500"
                }`}
                >
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Segment: {res.timestamp}</span>
                    <span
                    className={`px-2 py-0.5 text-xs rounded-full font-semibold ${
                        res.label === "FAKE"
                        ? "bg-red-500 text-white"
                        : "bg-green-500 text-white"
                    }`}
                    >
                    {res.label}
                    </span>
                </div>

                <div className="relative">
                    <video
                    src={video.url}
                    controls
                    className="w-full rounded"
                    onLoadedMetadata={(e) => {
                        e.currentTarget.currentTime = res.start;
                    }}
                    />
                    <div className="absolute top-2 right-2 bg-white bg-opacity-80 text-xs px-2 py-0.5 rounded shadow flex items-center gap-1">
                    <FiVideo size={14} />
                    {res.timestamp}
                    </div>
                </div>
                </div>
            ))}
            </div>
            ) : (
            <p className="text-gray-500">No results found. Please check the video.</p>
            )}
   
        </div>
      </div>
    </div>
  );
}
