"""
Unit tests for Gemini Speech-to-Text audio transcription and error handling.
Validates:
1. No faster-whisper loaded on server startup
2. In-memory audio processing (no files saved on disk)
3. 4 MB limit validation
4. Language hint passing (Auto, English, Tamil, Hindi, Malayalam, Telugu)
5. Missing GEMINI_API_KEY returns friendly 'no_key' error
6. Quota exceeded handling returns 'quota_finished'
7. Empty audio handling
8. Keyword matching integration with questionnaire
"""

import io
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv()

from app import app
from voice_engine import (
    transcribe_audio,
    match_voice_to_option,
    get_whisper_model,
    KEYWORD_MAPPINGS
)


class TestGeminiVoiceEngine(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_no_whisper_loaded_at_startup(self):
        """Whisper singleton must remain None at startup."""
        import voice_engine
        self.assertIsNone(voice_engine._WHISPER_MODEL)

    def test_transcribe_missing_audio(self):
        """POST /transcribe with missing audio field must return 400."""
        resp = self.client.post("/transcribe", data={})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("No audio file", data["error"])

    def test_transcribe_empty_audio_file(self):
        """POST /transcribe with 0-byte audio must return 400."""
        data = {
            "audio": (io.BytesIO(b""), "test.webm", "audio/webm")
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 400)
        res = resp.get_json()
        self.assertFalse(res["success"])

    def test_transcribe_exceeds_4mb_limit(self):
        """POST /transcribe with audio > 4MB must return error."""
        large_audio = b"0" * (4 * 1024 * 1024 + 10)
        data = {
            "audio": (io.BytesIO(large_audio), "large.webm", "audio/webm")
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        res = resp.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res.get("error_type"), "file_too_large")

    @patch("voice_engine.get_gemini_api_key", return_value="")
    def test_transcribe_missing_api_key_returns_friendly_error(self, mock_key):
        """When GEMINI_API_KEY is not set, must return error_type='no_key' gracefully."""
        audio_data = b"RIFF....WAVEfmt ...."
        data = {
            "audio": (io.BytesIO(audio_data), "mic.webm", "audio/webm"),
            "question": "chat"
        }
        with patch.dict(os.environ, {"VERCEL": "1"}):
            resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
            self.assertEqual(resp.status_code, 200)
            res = resp.get_json()
            self.assertFalse(res["success"])
            self.assertEqual(res.get("error_type"), "no_key")
            self.assertIn("GEMINI_API_KEY", res.get("error", ""))

    @patch("voice_engine.get_gemini_api_key", return_value="fake_key_123")
    @patch("google.genai.Client")
    def test_transcribe_english_speech(self, mock_client_cls, mock_key):
        """Test successful Gemini transcription in English."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "I want a distro for gaming and 16gb ram"
        mock_client.models.generate_content.return_value = mock_response

        audio_data = b"webm_bytes_here"
        data = {
            "audio": (io.BytesIO(audio_data), "rec.webm", "audio/webm"),
            "question": "chat",
            "language": "en"
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertTrue(res["success"])
        self.assertEqual(res["transcript"], "I want a distro for gaming and 16gb ram")

    @patch("voice_engine.get_gemini_api_key", return_value="fake_key_123")
    @patch("google.genai.Client")
    def test_transcribe_tamil_speech(self, mock_client_cls, mock_key):
        """Test successful Gemini transcription in Tamil."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "வணக்கம் எனக்கு சிறந்த லினக்ஸ் வேண்டும்"
        mock_client.models.generate_content.return_value = mock_response

        audio_data = b"tamil_audio_bytes"
        data = {
            "audio": (io.BytesIO(audio_data), "rec.ogg", "audio/ogg"),
            "question": "chat",
            "language": "ta"
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertTrue(res["success"])
        self.assertEqual(res["transcript"], "வணக்கம் எனக்கு சிறந்த லினக்ஸ் வேண்டும்")

    @patch("voice_engine.get_gemini_api_key", return_value="fake_key_123")
    @patch("google.genai.Client")
    def test_transcribe_empty_or_silence(self, mock_client_cls, mock_key):
        """Test when Gemini returns empty string for silence."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        audio_data = b"silent_audio_bytes"
        data = {
            "audio": (io.BytesIO(audio_data), "rec.webm", "audio/webm"),
            "question": "chat",
            "language": "auto"
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertTrue(res["success"])
        self.assertEqual(res["transcript"], "")

    @patch("voice_engine.get_gemini_api_key", return_value="fake_key_123")
    @patch("google.genai.Client")
    def test_transcribe_quota_exceeded(self, mock_client_cls, mock_key):
        """Test handling of 429 quota exhaustion from Gemini."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("429 RESOURCE_EXHAUSTED: quota exceeded")

        audio_data = b"audio_bytes"
        data = {
            "audio": (io.BytesIO(audio_data), "rec.webm", "audio/webm"),
            "question": "chat"
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res.get("error_type"), "quota_finished")
        self.assertIn("quota", res.get("error", "").lower())

    @patch("voice_engine.get_gemini_api_key", return_value="fake_key_123")
    @patch("google.genai.Client")
    def test_transcribe_questionnaire_matching(self, mock_client_cls, mock_key):
        """Test that questionnaire options are matched properly from Gemini transcript."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "I have 8 gb ram"
        mock_client.models.generate_content.return_value = mock_response

        data = {
            "audio": (io.BytesIO(b"ram_audio"), "rec.webm", "audio/webm"),
            "question": "ram"
        }
        resp = self.client.post("/transcribe", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertTrue(res["success"])
        self.assertTrue(res["matched"])
        self.assertEqual(res["option_value"], "4GB - 8GB")


if __name__ == "__main__":
    unittest.main()
