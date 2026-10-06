import pytest
from app.services.youtube_service import YouTubeService


def test_is_valid_youtube_url():
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
    ]
    for url in valid_urls:
        assert YouTubeService.is_valid_url(url) is True, f"Failed for: {url}"


def test_is_invalid_youtube_url():
    invalid_urls = [
        "",
        "https://google.com",
        "https://vimeo.com/12345678",
        "not_a_url",
        "https://youtube.com/watch?v=short",
    ]
    for url in invalid_urls:
        assert YouTubeService.is_valid_url(url) is False, f"Should be invalid: {url}"


def test_extract_video_id():
    test_cases = {
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123": "dQw4w9WgXcQ",
    }
    for url, expected_id in test_cases.items():
        extracted = YouTubeService.extract_video_id(url)
        assert extracted == expected_id, f"Expected {expected_id} but got {extracted} for {url}"
