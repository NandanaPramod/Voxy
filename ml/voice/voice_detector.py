"""
ml/voice/voice_detector.py

Hackathon prototype: heuristic-based voice authenticity risk scorer.

IMPORTANT: This is NOT a scientifically validated deepfake/synthetic-voice
detector. It uses simple acoustic features (spectral flatness, MFCC
variability, zero-crossing rate) as weak proxies for "unnaturalness" in
audio. It is intended as an MVP signal for the Voxy hackathon project,
not a production-grade authentication system.
"""

import numpy as np
import librosa


def _safe_mean(x):
    """Return the mean of an array, guarding against empty/NaN arrays."""
    if x is None or len(x) == 0:
        return 0.0
    val = np.nanmean(x)
    return float(val) if np.isfinite(val) else 0.0


def analyze_voice(audio_path: str) -> dict:
    """
    Analyze an audio file and return a heuristic voice authenticity risk score.

    Args:
        audio_path: Path to an audio file (wav, mp3, flac, etc.)

    Returns:
        dict with:
            - voice_risk (int): 0-100 risk score (higher = more likely synthetic)
            - prediction (str): one of
                "LIKELY_HUMAN", "POSSIBLE_SYNTHETIC",
                "HIGH_SYNTHETIC_RISK", "UNKNOWN"
    """
    try:
        # --- Load audio safely ---
        y, sr = librosa.load(audio_path, sr=None, mono=True)

        if y is None or len(y) == 0:
            return {"voice_risk": 50, "prediction": "UNKNOWN"}

        # Trim silence so long pauses don't skew the features
        y_trimmed, _ = librosa.effects.trim(y, top_db=25)
        if len(y_trimmed) < sr * 0.2:  # too short (<200ms) to be meaningful
            y_trimmed = y

        # --- Feature 1: Spectral flatness ---
        # Synthetic voices often have unnaturally flat/noisy spectra
        # (closer to 1 = more noise-like, closer to 0 = more tonal/human-like)
        flatness = librosa.feature.spectral_flatness(y=y_trimmed)
        flatness_mean = _safe_mean(flatness)

        # --- Feature 2: MFCC variability ---
        # Natural human speech has organic variation frame-to-frame;
        # synthetic speech can be unnaturally smooth (low variance) OR
        # erratic (very high variance) depending on the generator.
        mfccs = librosa.feature.mfcc(y=y_trimmed, sr=sr, n_mfcc=13)
        mfcc_std = _safe_mean(np.std(mfccs, axis=1))

        # --- Feature 3: Zero-crossing rate ---
        # Unnatural buzziness/artifacts in synthetic audio often show up
        # as an unusually high or low ZCR compared to natural speech norms.
        zcr = librosa.feature.zero_crossing_rate(y_trimmed)
        zcr_mean = _safe_mean(zcr)

        # --- Combine into a 0-100 risk score ---
        # These thresholds/weights are heuristic, tuned by eyeballing
        # a handful of sample clips - not derived from a trained model.

        # Normalize each feature to a rough 0-1 "suspicion" contribution
        flatness_score = np.clip(flatness_mean * 4, 0, 1)          # typical range ~0-0.3
        mfcc_score = np.clip(1 - (mfcc_std / 40), 0, 1)            # low variance -> higher risk
        zcr_score = np.clip(abs(zcr_mean - 0.08) * 8, 0, 1)        # deviation from typical speech ZCR

        risk = (
            0.40 * flatness_score +
            0.35 * mfcc_score +
            0.25 * zcr_score
        ) * 100

        voice_risk = int(np.clip(round(risk), 0, 100))

        # --- Map score to prediction label ---
        if voice_risk < 35:
            prediction = "LIKELY_HUMAN"
        elif voice_risk < 65:
            prediction = "POSSIBLE_SYNTHETIC"
        else:
            prediction = "HIGH_SYNTHETIC_RISK"

        return {"voice_risk": voice_risk, "prediction": prediction}

    except Exception as e:
        # Any failure (bad file, unsupported format, corrupt audio, etc.)
        # -> safe fallback so the rest of the pipeline never crashes.
        print(f"[voice_detector] analyze_voice failed for '{audio_path}': {e}")
        return {"voice_risk": 50, "prediction": "UNKNOWN"}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python voice_detector.py <audio_file_path>")
        sys.exit(1)
    result = analyze_voice(sys.argv[1])
    print(result)