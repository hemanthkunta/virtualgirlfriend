#!/usr/bin/env python3
"""Benchmark the main Virtual Girlfriend AI pipeline stages.

This script measures a small, repeatable slice of the app:
- core module initialization
- personality prompt generation
- Ollama response latency when the local server is available
- fallback text-to-speech synthesis latency
- video watermark blur latency
- audio/video merge latency
"""

from __future__ import annotations

import glob
import json
import os
import statistics
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Dict, Optional

from src.expression_mapper import ExpressionMapper
from src.ollama_interface import ConversationManager, OllamaInterface
from src.personality_engine import PersonalityEngine
from src.tts_engine import TextToSpeechEngine
from src.video_processor import LipSyncEngine, VideoProcessor


ROOT = Path(__file__).resolve().parent
FACIAL_EXPRESSION_DIR = ROOT / "facialexpressions"
OUTPUT_DIR = ROOT / "processed_videos"
SAMPLE_TTS_TEXT = "Hello there, this is a benchmark synthesis test."
SAMPLE_CHAT_MESSAGE = "Hey babe, I missed you today."


@dataclass
class BenchmarkResult:
    name: str
    status: str
    seconds: float
    detail: str = ""


def timed(name: str, func: Callable[[], str]) -> BenchmarkResult:
    start = time.perf_counter()
    try:
        detail = func()
        return BenchmarkResult(name=name, status="ok", seconds=time.perf_counter() - start, detail=detail)
    except Exception as exc:  # pragma: no cover - benchmark must continue on failure
        return BenchmarkResult(name=name, status="error", seconds=time.perf_counter() - start, detail=str(exc))


def mean(values):
    return statistics.mean(values) if values else 0.0


def pick_sample_video() -> Optional[Path]:
    candidates = sorted(FACIAL_EXPRESSION_DIR.glob("*.mp4"))
    return candidates[0] if candidates else None


def run_benchmark() -> Dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    results.append(timed("init_personality_engine", lambda: "initialized" if PersonalityEngine() else ""))
    results.append(timed("init_expression_mapper", lambda: f"{len(ExpressionMapper().expression_map)} emotion groups"))
    results.append(timed("init_tts_engine", lambda: "pyttsx3 fallback" if TextToSpeechEngine(provider="pyttsx3") else ""))
    results.append(timed("init_video_processor", lambda: "initialized" if VideoProcessor() else ""))
    results.append(timed("init_lipsync_engine", lambda: "initialized" if LipSyncEngine() else ""))

    personality_engine = PersonalityEngine()
    expression_mapper = ExpressionMapper()
    tts_engine = TextToSpeechEngine(provider="pyttsx3")
    video_processor = VideoProcessor()
    lipsync_engine = LipSyncEngine()

    results.append(
        timed(
            "generate_personality_prompt",
            lambda: str(
                len(
                    personality_engine.generate_personality_prompt(
                        SAMPLE_CHAT_MESSAGE,
                        ["Hi", "How was your day?"],
                        persona="girlfriend",
                    )
                )
            ),
        )
    )

    ollama = OllamaInterface(model_name=os.getenv("OLLAMA_MODEL", "mistral"))
    conversation_mgr = ConversationManager(ollama)
    if ollama.check_connection():
        results.append(
            timed(
                "ollama_generate_response",
                lambda: conversation_mgr.generate_response(
                    user_message=SAMPLE_CHAT_MESSAGE,
                    system_prompt=personality_engine.generate_personality_prompt(SAMPLE_CHAT_MESSAGE, []),
                    temperature=0.7,
                )[:80],
            )
        )
    else:
        results.append(BenchmarkResult("ollama_generate_response", "skipped", 0.0, "Ollama server unavailable"))

    tts_output = f"benchmark_tts_{int(time.time())}.wav"
    results.append(
        timed(
            "tts_synthesis",
            lambda: f"{tts_engine.synthesize(SAMPLE_TTS_TEXT, tts_output)[0]}",
        )
    )

    sample_video = pick_sample_video()
    if sample_video:
        blurred_output = OUTPUT_DIR / "benchmark_blur.mp4"
        merged_output = OUTPUT_DIR / "benchmark_merged.mp4"

        results.append(
            timed(
                "video_blur_watermark",
                lambda: str(video_processor.blur_watermark(str(sample_video), str(blurred_output))),
            )
        )

        audio_path = Path(tts_engine.synthesize(SAMPLE_TTS_TEXT, f"benchmark_merge_{int(time.time())}.wav")[0])
        results.append(
            timed(
                "merge_audio_video",
                lambda: str(lipsync_engine.merge_audio_video(str(sample_video), str(audio_path), str(merged_output))),
            )
        )
    else:
        results.append(BenchmarkResult("video_blur_watermark", "skipped", 0.0, "No facial expression MP4 files found"))
        results.append(BenchmarkResult("merge_audio_video", "skipped", 0.0, "No facial expression MP4 files found"))

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": [asdict(result) for result in results],
        "success_count": sum(1 for result in results if result.status == "ok"),
        "error_count": sum(1 for result in results if result.status == "error"),
        "skipped_count": sum(1 for result in results if result.status == "skipped"),
        "average_ok_seconds": mean([result.seconds for result in results if result.status == "ok"]),
    }
    return payload


def main() -> int:
    report = run_benchmark()

    print("\n=== Virtual Girlfriend AI Benchmark ===")
    print(f"Generated at: {report['generated_at']}")
    print()

    for item in report["results"]:
        print(f"{item['name']}: {item['status']} ({item['seconds']:.3f}s) {item['detail']}")

    print()
    print(f"Success: {report['success_count']}")
    print(f"Errors: {report['error_count']}")
    print(f"Skipped: {report['skipped_count']}")
    print(f"Average ok time: {report['average_ok_seconds']:.3f}s")

    output_path = ROOT / "benchmark_results.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved report to: {output_path}")

    return 0 if report["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())