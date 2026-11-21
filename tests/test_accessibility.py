"""Accessibility: voice, Urdu, low-literacy UI and weak-connection handling."""

URDU_TEXT = "میرے پاس رلیف ادائیگی کی درخواست ہے، ماہانہ آمدنی 12000 روپے ہے"


def test_voice_intake_returns_spoken_prompt_and_saves_progress(client, headers):
    response = client.post(
        "/api/ai/voice/intake",
        headers=headers("citizen"),
        json={"transcript": URDU_TEXT, "language": "ur"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case"]["intake_channel"] == "voice"
    assert body["spoken_prompt"]
    assert body["language"] == "ur"
    assert body["simulated"] is True


def test_urdu_explanation_is_available(client, headers):
    case_id = client.get("/api/cases", headers=headers("citizen")).json()[0]["id"]
    explanation = client.get(f"/api/cases/{case_id}/explain", headers=headers("citizen")).json()
    assert any("\u0600" <= char <= "\u06ff" for char in explanation["simple_urdu"])


def test_low_literacy_ui_is_served(client):
    index = client.get("/")
    assert index.status_code == 200
    assert "PROTOTYPE" in index.text
    js = client.get("/static/app.js")
    assert js.status_code == 200
    assert "SpeechRecognition" in js.text
    assert "localStorage" in js.text
    assert "speechSynthesis" in js.text


def test_voice_led_completion_markers_are_served(client):
    js = client.get("/static/app.js").text
    for marker in (
        "function startMic",
        "function askForVoiceField",
        "function continueVoiceCompletion",
        "function extractSingleClaimField",
        "function fillSingleClaimField",
        "voiceAsk",
        "voiceAllDone",
        "stopActiveRecognition(true)",
    ):
        assert marker in js, marker


def test_urdu_recognition_error_is_not_blamed_on_internet(client):
    js = client.get("/static/app.js").text
    for marker in (
        "URDU_RECOGNITION_LOCALES = ['ur-PK', 'ur', 'ur-IN']",
        "function tryNextUrduRecognitionLocale",
        "state.lang === 'ur' && navigator.onLine && tryNextUrduRecognitionLocale()",
        "micTryingLocale",
        "Your internet is online",
        "آپ کا انٹرنیٹ چل رہا ہے",
    ):
        assert marker in js, marker


def test_bilingual_numbers_and_urdu_district_markers_are_served(client):
    js = client.get("/static/app.js").text
    for marker in (
        "function normaliseDigits(text)",
        r"[\u0660-\u0669]",
        r"[\u06F0-\u06F9]",
        "function cleanExtractedName(value)",
        "function cleanExtractedDistrict(value)",
        "رہائش|ضلع|شہر",
        r"\d{5}[-\s]?\d{7}[-\s]?\d",
        "میرا نام Aisha Khatoon ہے۔ شناختی نمبر 11111-2222233-3۔",
    ):
        assert marker in js, marker


def test_weak_connection_endpoint_accepts_small_payload(client, headers):
    response = client.post(
        "/api/ai/voice/intake",
        headers=headers("citizen"),
        json={"transcript": "need payment", "language": "ur"},
    )
    assert response.status_code == 200
    assert response.json()["case"]["status"] in {"needs_info", "human_review"}


def test_rag_supports_urdu_questions(client, headers):
    response = client.post(
        "/api/ai/rag", headers=headers("citizen"), json={"question": "آمدنی کی حد کیا ہے؟"}
    )
    assert response.status_code == 200
    assert response.json()["sources"]
