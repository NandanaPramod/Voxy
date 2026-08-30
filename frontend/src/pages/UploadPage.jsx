import { motion } from "framer-motion";
import { ArrowLeft, ScanLine, AlertCircle } from "lucide-react";
import FileDrop from "@/components/FileDrop";

export default function UploadPage({ file, onFile, onClear, onAnalyze, onBack, analyzing, error }) {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-10 pb-6">
      <button
        onClick={onBack}
        className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="font-display font-bold text-3xl sm:text-4xl text-white">
          Upload a call recording
        </h1>
        <p className="text-slate-400 mt-2">
          Choose an audio file of the call you want Voxy to analyze.
        </p>
      </motion.div>

      <div className="mt-6">
        <FileDrop file={file} onFile={onFile} onClear={onClear} />
      </div>

      {error && (
        <div className="mt-4 flex items-center gap-2 text-sm text-danger border border-danger/40 bg-danger/10 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="mt-6 flex flex-col sm:flex-row items-center gap-4 justify-between">
        <p className="text-xs text-slate-500">
          By analyzing, you confirm you have the right to process this audio.
        </p>
        <button
          onClick={onAnalyze}
          disabled={!file || analyzing}
          className="voxy-btn-primary w-full sm:w-auto"
        >
          <ScanLine className="w-5 h-5" />
          Analyze Call
        </button>
      </div>
    </div>
  );
}
