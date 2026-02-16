from app.services.link_utils import hash_link, normalize_link


def test_normalize_removes_query_and_fragment():
    url = "https://www.linkedin.com/posts/abc?trk=test#section"
    assert normalize_link(url) == "https://www.linkedin.com/posts/abc"


def test_hash_is_deterministic_for_same_normalized_url():
    a = normalize_link("https://x.com/p/1?foo=1")
    b = normalize_link("https://x.com/p/1?bar=2#x")
    assert a == b
    assert hash_link(a) == hash_link(b)
