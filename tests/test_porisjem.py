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


def test_post_mapper_sentry_sanitizes_nan_and_inf_values() -> None:
    sentry = PostMapperSentry()
    vector = np.array([np.nan, np.inf, -np.inf, 0.2, 0.4])

    safe_vec, safe_urgency = sentry.audit(vector, urgency=0.7, flags=SentryFlags())

    assert isinstance(safe_vec, tuple)
    assert np.isfinite(np.array(safe_vec)).all()
    assert 0.0 <= safe_urgency <= 0.7


def test_porisjem_system_sanitize_signal_accepts_none_flags() -> None:
    from logenesis.porisjem import PorisjemSystem

    system = PorisjemSystem()
    safe_vec, safe_urgency = system.sanitize_signal((0.1, 0.1, 0.1), urgency=0.5, flags=None)

    assert isinstance(safe_vec, tuple)
    assert np.isclose(safe_urgency, 0.5)
