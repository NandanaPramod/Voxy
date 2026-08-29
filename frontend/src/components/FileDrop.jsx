import { useRef, useState } from "react";
import { Upload, FileAudio, X } from "lucide-react";

const ACCEPTED = "audio/*";

function formatSize(bytes) {
  if (!bytes && bytes !== 0) return "";
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileDrop({ file, onFile, onClear }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (files) => {
    const f = files?.[0];
    if (f) onFile(f);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={`relative rounded-2xl border-2 border-dashed transition-all p-8 sm:p-10 text-center ${
        dragging ? "border-brand bg-brand/5 shadow-glow" : "border-line bg-panel/50"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files);
          e.target.value = "";
        }}
      />

      {!file ? (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex flex-col items-center gap-3 w-full"
        >
          <div className="w-14 h-14 rounded-2xl bg-panel2 border border-line flex items-center justify-center">
            <Upload className="w-7 h-7 text-brand" />
          </div>
          <div>
            <p className="font-display font-semibold text-lg text-white">
              Drop a call recording here
            </p>
            <p className="text-sm text-slate-400 mt-1">
              or <span className="text-brand underline">browse files</span> — MP3, WAV, M4A, OGG
            </p>
          </div>
          <p className="text-xs text-slate-600 mt-1">Max 50 MB · audio only</p>
        </button>
      ) : (
        <div className="flex items-center gap-4 text-left">
          <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/30 flex items-center justify-center shrink-0">
            <FileAudio className="w-6 h-6 text-brand" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-medium text-white truncate">{file.name}</p>
            <p className="text-xs text-slate-400">
              {formatSize(file.size)} · {(file.type || "audio").replace("audio/", "").toUpperCase()}
            </p>
          </div>
          <button
            type="button"
            onClick={onClear}
            className="w-9 h-9 rounded-lg border border-line flex items-center justify-center text-slate-400 hover:text-danger hover:border-danger/50 transition-colors"
            aria-label="Remove file"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
