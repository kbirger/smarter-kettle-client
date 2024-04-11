from unittest.mock import MagicMock, Mock, PropertyMock
import pytest

from smarter_client.domain.decorators.session import refreshsession


class TestRefreshSession:
    def test_refreshsession_raises_error_when_no_session(self):
        class Test:
            session = None

            @refreshsession
            def test(self):
                pass  # pragma: no cover

        with pytest.raises(ValueError):
            Test().test()

    def test_refresh_session_when_session_expires_in_less_than_30(self):
        class Test:
            session = type('Session', (), {'expires_in': 29})

            def refresh(self):
                self.session.expires_in = 31

            @refreshsession
            def test(self):
                pass

        Test().test()
        assert Test().session.expires_in == 31

    def test_does_not_refresh_session_when_session_expires_in_more_than_30(self):
        class Test:
            session = type('Session', (), {'expires_in': 31})

            refresh = Mock()

            @refreshsession
            def test(self):
                pass

        test = Test()
        test.test()

        assert test.refresh.call_count == 0
