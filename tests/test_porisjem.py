import numpy as np

from logenesis.porisjem import PostMapperSentry, SentryFlags


def test_post_mapper_sentry_accepts_tuple_vector() -> None:
    sentry = PostMapperSentry()
    vector = (0.2, 0.1, 0.1, -1.0, 1.2)

    safe_vec, safe_urgency = sentry.audit(vector, urgency=0.8, flags=SentryFlags())

    assert isinstance(safe_vec, tuple)
    assert 0.0 < safe_urgency <= 0.8
    assert len(safe_vec) == 5


def test_post_mapper_sentry_handles_short_vectors_without_crashing() -> None:
    sentry = PostMapperSentry()
    short_vector = np.array([0.1, 0.2, 0.3])

    safe_vec, safe_urgency = sentry.audit(short_vector, urgency=0.6, flags=SentryFlags())

    assert isinstance(safe_vec, tuple)
    assert len(safe_vec) == 3
    assert np.isclose(safe_urgency, 0.6)
