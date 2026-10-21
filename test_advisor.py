"""
Unit and Integration Test Suite for Linux Distribution Advisor.
Validates the algorithmic scoring logic, edge case handling, database storage,
and Flask HTTP endpoints.
"""

import unittest
import json
import os
from app import app
from recommender import calculate_recommendation
from distro_data import DISTRIBUTIONS, get_all_distros, get_distro_by_id
from database import init_db, save_recommendation, get_recent_recommendations

class TestDistroAdvisor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_distro_catalog_integrity(self):
        """Verify all distributions have required fields, valid percentages, and unique IDs."""
        distros = get_all_distros()
        self.assertGreaterEqual(len(distros), 10)
        
        ids = set()
        for d in distros:
            self.assertIn("id", d)
            self.assertIn("name", d)
            self.assertIn("min_ram_gb", d)
            self.assertIn("rec_ram_gb", d)
            self.assertIn("primary_purposes", d)
            self.assertIn("pros", d)
            self.assertIn("cons", d)
            self.assertNotIn(d["id"], ids, f"Duplicate distro ID: {d['id']}")
            ids.add(d["id"])

    def test_low_hardware_recommends_lightweight_distro(self):
        """A system with <2GB RAM and low CPU should recommend Lubuntu or Puppy Linux."""
        profile = {
            "ram": "<2GB",
            "storage": "<20GB",
            "cpu": "Older / Low-end Dual Core (Atom, Celeron, Core 2 Duo)",
            "experience": "Beginner",
            "prev_experience": "None / First time",
            "purpose": "General use",
            "preference": "Lightweight"
        }
        res = calculate_recommendation(profile)
        best = res["best_match"]
        self.assertIn(best["id"], ["lubuntu", "puppy-linux", "linux-mint"])
        self.assertGreaterEqual(best["match_percentage"], 80)
        self.assertEqual(len(res["alternatives"]), 2)

    def test_gaming_profile(self):
        """Gamers with modern hardware should receive Pop!_OS, Manjaro, or Ubuntu."""
        profile = {
            "ram": "16GB+",
            "storage": "100GB+",
            "cpu": "High-end Multi-core (Intel i7/i9, AMD Ryzen 7/9)",
            "experience": "Intermediate",
            "prev_experience": "Dual boot or casual user",
            "purpose": "Gaming",
            "preference": "Easy to use"
        }
        res = calculate_recommendation(profile)
        best = res["best_match"]
        self.assertIn(best["id"], ["pop-os", "manjaro", "ubuntu", "fedora"])
        self.assertGreaterEqual(best["match_percentage"], 85)

    def test_beginner_security_warning(self):
        """A complete beginner selecting Security must trigger an educational advisory warning."""
        profile = {
            "ram": "8GB - 16GB",
            "storage": "50GB - 100GB",
            "cpu": "Mid-range Quad Core (Intel i3/i5, AMD Ryzen 3/5)",
            "experience": "Beginner",
            "prev_experience": "None / First time",
            "purpose": "Security",
            "preference": "Easy to use"
        }
        res = calculate_recommendation(profile)
        self.assertIsNotNone(res.get("advisory_warning"))
        self.assertIn("Kali Linux", res["advisory_warning"])

    def test_advanced_customizer(self):
        """An advanced user who wants cutting-edge/customization should match Arch, Manjaro, or openSUSE."""
        profile = {
            "ram": "16GB+",
            "storage": "100GB+",
            "cpu": "High-end Multi-core (Intel i7/i9, AMD Ryzen 7/9)",
            "experience": "Advanced",
            "prev_experience": "Daily driver / Server experience",
            "purpose": "Programming",
            "preference": "Customizable"
        }
        res = calculate_recommendation(profile)
        best = res["best_match"]
        self.assertIn(best["id"], ["arch-linux", "manjaro", "fedora", "opensuse-tumbleweed", "debian"])

    def test_flask_endpoints(self):
        """Test Flask routes and JSON API endpoint."""
        client = app.test_client()

        # GET /
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Linux Distribution", resp.data)

        # GET /distros
        resp = client.get("/distros")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Explore All", resp.data)

        # GET /distro/<id>
        resp = client.get("/distro/linux-mint")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Linux Mint", resp.data)

        # GET /compare
        resp = client.get("/compare?d1=linux-mint&d2=ubuntu&d3=fedora")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Side-by-Side Comparison", resp.data)

        # GET /guide
        resp = client.get("/guide")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Beginner", resp.data)

        # POST /api/recommend
        api_payload = {
            "ram": "4GB - 8GB",
            "storage": "20GB - 50GB",
            "cpu": "Mid-range Quad Core",
            "experience": "Beginner",
            "prev_experience": "None / First time",
            "purpose": "General use",
            "preference": "Easy to use"
        }
        resp = client.post("/api/recommend", data=json.dumps(api_payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("best_match", data["data"])
        self.assertIn("match_percentage", data["data"]["best_match"])
        self.assertGreater(data["data"]["best_match"]["match_percentage"], 75)
        self.assertEqual(len(data["data"]["alternatives"]), 2)

    def test_voice_keyword_matching(self):
        """Test voice transcript to option keyword mapping."""
        from voice_engine import match_voice_to_option

        # RAM tests
        self.assertEqual(match_voice_to_option("ram", "I have eight gb of memory"), "4GB - 8GB")
        self.assertEqual(match_voice_to_option("ram", "about 8 gigabytes"), "4GB - 8GB")
        self.assertEqual(match_voice_to_option("ram", "less than 2 gigabytes"), "<2GB")
        self.assertEqual(match_voice_to_option("ram", "more than sixteen gb"), "16GB+")

        # Purpose tests
        self.assertEqual(match_voice_to_option("purpose", "mainly coding and software"), "Programming")
        self.assertEqual(match_voice_to_option("purpose", "I love gaming with steam"), "Gaming")
        self.assertEqual(match_voice_to_option("purpose", "ethical hacking and security"), "Security")
        self.assertEqual(match_voice_to_option("purpose", "office work and word documents"), "Office")
        self.assertEqual(match_voice_to_option("purpose", "school homework education"), "Education")
        self.assertEqual(match_voice_to_option("purpose", "casual web browsing"), "General use")

        # Experience tests
        self.assertEqual(match_voice_to_option("experience", "I am a total beginner"), "Beginner")
        self.assertEqual(match_voice_to_option("experience", "intermediate computer user"), "Intermediate")
        self.assertEqual(match_voice_to_option("experience", "advanced power user terminal"), "Advanced")

        # Preference tests
        self.assertEqual(match_voice_to_option("preference", "easy to use and simple"), "Easy to use")
        self.assertEqual(match_voice_to_option("preference", "super lightweight and fast"), "Lightweight")
        self.assertEqual(match_voice_to_option("preference", "rock solid stability"), "Rock-solid stability")

        # Unmatched speech
        self.assertIsNone(match_voice_to_option("purpose", "apple pie recipe"))

    def test_transcribe_endpoint_validation(self):
        """Test that /transcribe requires audio upload and returns 400 if missing."""
        client = app.test_client()
        resp = client.post("/transcribe", data={})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("No audio file", data["error"])

    def test_chat_advisor_unrelated_query(self):
        """Chat advisor must reject unrelated questions politely."""
        from chat_advisor import is_linux_related, process_chat_message

        self.assertFalse(is_linux_related("What is the capital of France?"))
        self.assertFalse(is_linux_related("Give me a recipe for chocolate pizza"))
        self.assertFalse(is_linux_related("Who won the soccer match yesterday?"))

        res = process_chat_message("What is the capital of France?")
        self.assertIsNone(res["recommendation"])
        self.assertIn("I'm your Linux OS assistant. I can only help with Linux distributions and Linux-related questions. Ask me something about Linux!", res["reply"])

    def test_chat_advisor_spec_extraction_and_recommendation(self):
        """Chat advisor must extract hardware and goals and recommend a distro."""
        from chat_advisor import process_chat_message

        # Test gaming + 16GB RAM
        res = process_chat_message("I want to do gaming and have 16gb ram")
        self.assertIsNotNone(res["recommendation"])
        self.assertIn(res["recommendation"]["name"], ["Ubuntu", "Pop!_OS", "Manjaro", "Fedora"])
        self.assertGreaterEqual(res["recommendation"]["match_percentage"], 85)

        # Test old laptop with 2GB RAM
        res_old = process_chat_message("I have an old laptop with 2GB RAM and dual core cpu")
        self.assertIsNotNone(res_old["recommendation"])
        self.assertIn(res_old["recommendation"]["name"], ["Lubuntu", "Linux Mint", "Zorin OS", "Puppy Linux"])

    def test_api_chat_advisor_endpoint(self):
        """Test Flask HTTP POST /api/chat_advisor route."""
        client = app.test_client()

        # Valid Linux query
        payload = {"message": "I want a distro for coding in Python on 8GB RAM", "context": {}}
        resp = client.post("/api/chat_advisor", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["data"]["recommendation"])

        # Unrelated query
        unrelated_payload = {"message": "What is the capital of Spain?", "context": {}}
        resp = client.post("/api/chat_advisor", data=json.dumps(unrelated_payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIsNone(data["data"]["recommendation"])
        self.assertIn("I'm your Linux OS assistant. I can only help with Linux distributions and Linux-related questions. Ask me something about Linux!", data["data"]["reply"])

    def test_chat_advisor_five_scenarios(self):
        """Verify the 5 required chat advisor scenarios without hardcoding Zorin OS."""
        from chat_advisor import process_chat_message

        mock_saved_quiz = {
            "best_match": {
                "id": "linux-mint",
                "name": "Linux Mint",
                "match_percentage": 94,
                "reasons": ["Familiar Windows-like interface", "Gentle learning curve"]
            },
            "profile": {
                "ram": "4GB - 8GB",
                "purpose": "General use",
                "experience": "Beginner"
            }
        }

        # 1. Best Linux for gaming? -> Gaming distro (Ubuntu / Pop!_OS), not Zorin OS
        res_gaming = process_chat_message("Best Linux for gaming?", quiz_result=mock_saved_quiz)
        self.assertIsNotNone(res_gaming["recommendation"])
        self.assertIn(res_gaming["recommendation"]["name"], ["Ubuntu", "Pop!_OS", "Manjaro", "Fedora"])
        self.assertNotEqual(res_gaming["recommendation"]["name"], "Zorin OS")

        # 2. Which Linux is good for a 2 GB old laptop? -> Lightweight distro (Puppy Linux / Lubuntu)
        res_light = process_chat_message("Which Linux is good for a 2 GB old laptop?", quiz_result=mock_saved_quiz)
        self.assertIsNotNone(res_light["recommendation"])
        self.assertIn(res_light["recommendation"]["name"], ["Puppy Linux", "Lubuntu"])
        self.assertNotEqual(res_light["recommendation"]["name"], "Zorin OS")

        # 3. Best Linux for ethical hacking? -> Kali Linux
        res_hack = process_chat_message("Best Linux for ethical hacking?", quiz_result=mock_saved_quiz)
        self.assertIsNotNone(res_hack["recommendation"])
        self.assertEqual(res_hack["recommendation"]["name"], "Kali Linux")

        # 4. What is Fedora? -> Explains Fedora without repeating quiz result
        res_fedora = process_chat_message("What is Fedora?", quiz_result=mock_saved_quiz)
        self.assertIn("fedora", res_fedora["reply"].lower())
        self.assertNotIn("94%", res_fedora["reply"])
        self.assertNotIn("Based on your quiz result", res_fedora["reply"])

        # 5. Why did you recommend my result? -> Explains the user's actual saved quiz result
        res_why = process_chat_message("Why did you recommend my result?", quiz_result=mock_saved_quiz)
        self.assertIn("Linux Mint", res_why["reply"])
        self.assertIn("94%", res_why["reply"])

if __name__ == "__main__":
    unittest.main()
