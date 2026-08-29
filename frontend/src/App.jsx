import { useState, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import StepIndicator from "@/components/StepIndicator";
import Home from "@/pages/Home";
import UploadPage from "@/pages/UploadPage";
import AnalyzingPage from "@/pages/AnalyzingPage";
import ResultsPage from "@/pages/ResultsPage";
import { analyzeAudio } from "@/lib/api";

export default function App() {
  // Flow state machine: home → upload → analyzing → results
  const [step, setStep] = useState("home");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const goHome = () => {
    setError(null);
    setFile(null);
    setResult(null);
    setStep("home");
  };

  const goUpload = () => {
    setError(null);
    setStep("upload");
  };

  const handleFile = (f) => {
    setError(null);
    setFile(f);
  };

  const clearFile = () => {
    setFile(null);
    setError(null);
  };

  const runAnalyze = useCallback(async () => {
    if (!file) return;
    setError(null);
    setAnalyzing(true);
    setStep("analyzing");
    try {
      const res = await analyzeAudio(file);
      setResult(res);
      setStep("results");
    } catch (e) {
      setError(e?.message || "Analysis failed. Please try again.");
      setStep("upload");
    } finally {
      setAnalyzing(false);
    }
  }, [file]);

  const analyzeAnother = () => {
    setError(null);
    setFile(null);
    setResult(null);
    setStep("upload");
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <StepIndicator current={step} />

      <main className="flex-1">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            {step === "home" && <Home onStart={goUpload} />}

            {step === "upload" && (
              <UploadPage
                file={file}
                onFile={handleFile}
                onClear={clearFile}
                onAnalyze={runAnalyze}
                onBack={goHome}
                analyzing={analyzing}
                error={error}
              />
            )}

            {step === "analyzing" && (
              <AnalyzingPage fileName={file?.name} />
            )}

            {step === "results" && result && (
              <ResultsPage
                result={result}
                file={file}
                onAgain={analyzeAnother}
                onHome={goHome}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
}
