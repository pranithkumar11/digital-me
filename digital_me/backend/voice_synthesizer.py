"""
voice_synthesizer.py - Neural Text-to-Speech Engine for Digital Me
Features:
- Edge-TTS neural speech generation producing natural .mp3 audio
- Smart markdown and symbol cleansing for clean spoken vocalization
- Content-hash audio caching to avoid redundant synthesis latency
- Resilient asynchronous execution with fallback
"""

import os
import sys
import re
import hashlib
import asyncio
from typing import Dict, Any, Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

DEFAULT_VOICE = os.getenv("DIGITAL_ME_VOICE", "en-US-ChristopherNeural")

AVAILABLE_VOICES = {
    "en-US-ChristopherNeural": "Christopher (US Male - Confident & Warm)",
    "en-IN-PrabhatNeural": "Prabhat (India Male - Professional & Crisp)",
    "en-US-GuyNeural": "Guy (US Male - Natural & Dynamic)",
    "en-GB-RyanNeural": "Ryan (UK Male - Clear & Articulate)",
    "en-IN-NeerjaNeural": "Neerja (India Female - Warm & Melodious)"
}


def clean_text_for_speech(raw_text: str) -> str:
    """
    Strips markdown formatting, citations, URLs, code blocks,
    and special characters so the synthesized speech sounds conversational and natural.
    """
    if not raw_text:
        return ""

    text = raw_text

    # 1. Remove code blocks ```...```
    text = re.sub(r"```[\s\S]*?```", " [code snippet omitted] ", text)

    # 2. Remove inline code `...`
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # 3. Convert markdown links [Label](url) to just Label
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # 4. Remove markdown headers (e.g. ### Header -> Header)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # 5. Remove bold / italic markers (**bold**, *italic*, _text_)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # 6. Remove bullet indicators and blockquotes
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s+", "", text, flags=re.MULTILINE)

    # 7. Remove emojis and non-standard unicode symbols that cause TTS glitches
    text = re.sub(r"[^\w\s.,!?:;'\-\"\/()%]", "", text)

    # 8. Clean up multiple spaces and newlines into natural pauses
    text = re.sub(r"\n+", ". ", text)
    text = re.sub(r"\.\s*\.+", ".", text)
    text = re.sub(r"\s+", " ", text).strip()

    # 9. Cap length for speech to ensure responsiveness (first ~550 chars / 3-4 sentences)
    if len(text) > 650:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        clipped = []
        cur_len = 0
        for s in sentences:
            if cur_len + len(s) > 550 and len(clipped) >= 2:
                break
            clipped.append(s)
            cur_len += len(s)
        text = " ".join(clipped)

    return text


class VoiceSynthesizer:
    def __init__(self, cache_dir: str = AUDIO_CACHE_DIR, default_voice: str = DEFAULT_VOICE):
        self.cache_dir = cache_dir
        self.default_voice = default_voice
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_filename(self, text: str, voice: str) -> str:
        """Compute MD5 hash identifier for audio file."""
        key = f"{text}|{voice}".encode("utf-8")
        hash_digest = hashlib.md5(key).hexdigest()[:16]
        return f"speech_{hash_digest}.mp3"

    async def _synthesize_async(self, text: str, voice: str, out_path: str) -> bool:
        """Invoke Edge-TTS Communicate coroutine and save to mp3."""
        import edge_tts
        communicate = edge_tts.Communicate(text, voice=voice, rate="+0%", pitch="+0Hz")
        await communicate.save(out_path)
        return True

    def synthesize(self, raw_text: str, voice: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize speech from input text.
        Returns metadata including audio filename, relative URL, duration, and status.
        """
        chosen_voice = voice if (voice and voice in AVAILABLE_VOICES) else self.default_voice
        clean_text = clean_text_for_speech(raw_text)

        if not clean_text:
            return {
                "success": False,
                "error": "Input text was empty after normalization",
                "audio_url": None,
                "filename": None
            }

        filename = self._get_cache_filename(clean_text, chosen_voice)
        filepath = os.path.join(self.cache_dir, filename)

        # 1. Return immediately if cached
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return {
                "success": True,
                "cached": True,
                "filename": filename,
                "audio_url": f"/api/audio/{filename}",
                "voice": chosen_voice,
                "clean_text": clean_text
            }

        # 2. Run Edge-TTS synthesis
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                # Running in an active event loop (e.g. some ASGI or nested runners)
                import nest_asyncio
                nest_asyncio.apply()

            loop.run_until_complete(self._synthesize_async(clean_text, chosen_voice, filepath))

            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return {
                    "success": True,
                    "cached": False,
                    "filename": filename,
                    "audio_url": f"/api/audio/{filename}",
                    "voice": chosen_voice,
                    "clean_text": clean_text
                }
            else:
                return {
                    "success": False,
                    "error": "Audio file was not generated or empty",
                    "audio_url": None,
                    "filename": None
                }

        except Exception as e:
            print(f"[!] Edge-TTS synthesis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_url": None,
                "filename": None,
                "tip": "Speech synthesis requires network access to Edge-TTS neural service."
            }

    def get_audio_path(self, filename: str) -> Optional[str]:
        """Return safe path to cached audio file if it exists."""
        safe_name = os.path.basename(filename)
        path = os.path.join(self.cache_dir, safe_name)
        if os.path.exists(path) and os.path.isfile(path):
            return path
        return None

    def list_voices(self) -> Dict[str, str]:
        """Return available neural voices."""
        return AVAILABLE_VOICES


# Singleton instance
_synth_instance: Optional[VoiceSynthesizer] = None


def get_voice_synthesizer() -> VoiceSynthesizer:
    global _synth_instance
    if _synth_instance is None:
        _synth_instance = VoiceSynthesizer()
    return _synth_instance


if __name__ == "__main__":
    print("[*] Testing Voice Synthesizer...")
    synth = get_voice_synthesizer()
    sample = "Hello! I am Pranith Kumar Dupuguntla. Welcome to my AI Digital Twin."
    print(f"Synthesizing: '{sample}'")
    res = synth.synthesize(sample)
    print("Result:", res)
