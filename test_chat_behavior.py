"""
Comprehensive test script for Linux AI Buddy assistant behavior.
Validates all requirements:
1. "Best Linux for gaming?" -> a gaming distro
2. "Which Linux is good for a 2 GB old laptop?" -> a lightweight distro
3. "Best Linux for ethical hacking?" -> Kali Linux
4. "What is Fedora?" -> an explanation of Fedora, not the quiz result
5. "Why did you recommend my result?" -> uses my real quiz result
6. "Hello" -> greeting back, then a Linux question
7. "How are you?" -> a friendly answer, then a Linux offer
8. "Thank you" and "Bye" -> polite replies
9. "Vanakkam" -> a Tamil greeting reply in Tamil script
10. "Tell me about a movie" -> a polite one-line Linux-only reply with an offer
"""

import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chat_advisor import process_chat_message

def run_tests():
    mock_saved_quiz = {
        "best_match": {
            "id": "linux-mint",
            "name": "Linux Mint",
            "match_percentage": 94,
            "reasons": ["Familiar Windows-like interface with Cinnamon desktop", "Gentle learning curve"]
        },
        "profile": {
            "ram": "4GB - 8GB",
            "purpose": "General use",
            "experience": "Beginner"
        }
    }

    print("--- 1. Best Linux for gaming? ---")
    res1 = process_chat_message("Best Linux for gaming?", quiz_result=mock_saved_quiz)
    print("Rec:", res1["recommendation"]["name"] if res1["recommendation"] else None)
    print("Reply:", res1["reply"][:140], "...")
    assert res1["recommendation"]["name"] in ["Ubuntu", "Pop!_OS", "Manjaro", "Fedora"], "Gaming failed"

    print("\n--- 2. Which Linux is good for a 2 GB old laptop? ---")
    res2 = process_chat_message("Which Linux is good for a 2 GB old laptop?", quiz_result=mock_saved_quiz)
    print("Rec:", res2["recommendation"]["name"] if res2["recommendation"] else None)
    print("Reply:", res2["reply"][:140], "...")
    assert res2["recommendation"]["name"] in ["Puppy Linux", "Lubuntu", "Linux Mint", "Zorin OS"], "2GB laptop failed"
    # Ensure it didn't just dump the quiz result (Linux Mint 94%)
    assert "Puppy Linux" in res2["recommendation"]["name"] or "Lubuntu" in res2["recommendation"]["name"], "Expected lightweight distro for 2GB"

    print("\n--- 3. Best Linux for ethical hacking? ---")
    res3 = process_chat_message("Best Linux for ethical hacking?", quiz_result=mock_saved_quiz)
    print("Rec:", res3["recommendation"]["name"] if res3["recommendation"] else None)
    print("Reply:", res3["reply"][:140], "...")
    assert res3["recommendation"]["name"] == "Kali Linux", "Hacking must recommend Kali Linux"

    print("\n--- 4. What is Fedora? ---")
    res4 = process_chat_message("What is Fedora?", quiz_result=mock_saved_quiz)
    print("Rec:", res4["recommendation"]["name"] if res4["recommendation"] else None)
    print("Reply:", res4["reply"])
    assert "fedora" in res4["reply"].lower() and "gnome" in res4["reply"].lower(), "Fedora inquiry failed"
    # Ensure it did NOT output the user's quiz result
    assert "94%" not in res4["reply"] and "Based on your quiz result" not in res4["reply"], "Fedora returned quiz result!"

    print("\n--- 5. Why did you recommend my result? ---")
    res5 = process_chat_message("Why did you recommend my result?", quiz_result=mock_saved_quiz)
    print("Reply:", res5["reply"])
    assert "Linux Mint" in res5["reply"] and "94%" in res5["reply"], "Quiz result inquiry failed"

    print("\n--- 6. Hello ---")
    res6 = process_chat_message("Hello")
    print("Reply:", res6["reply"])
    assert "hello" in res6["reply"].lower() and "linux" in res6["reply"].lower()

    print("\n--- 7. How are you? ---")
    res7 = process_chat_message("How are you?")
    print("Reply:", res7["reply"])
    assert "well" in res7["reply"].lower()

    print("\n--- 8. Thank you & Bye ---")
    res8a = process_chat_message("Thank you")
    res8b = process_chat_message("Bye")
    print("Thanks:", res8a["reply"])
    print("Bye:", res8b["reply"])
    assert "welcome" in res8a["reply"].lower()
    assert "goodbye" in res8b["reply"].lower()

    print("\n--- 9. Vanakkam ---")
    res9 = process_chat_message("Vanakkam")
    print("Reply:", res9["reply"])
    assert "வணக்கம்" in res9["reply"]

    print("\n--- 10. Tell me about a movie ---")
    res10 = process_chat_message("Tell me about a movie")
    print("Reply:", res10["reply"])
    assert "I'm your Linux OS assistant" in res10["reply"] or "specialized exclusively" in res10["reply"] or "cannot answer questions about movies" in res10["reply"]

    print("\n================ ALL 10 TESTS PASSED SUCCESSFULLY! ================")

if __name__ == "__main__":
    run_tests()
