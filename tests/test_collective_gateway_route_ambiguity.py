"""An unauthenticated 401 cannot establish that a gateway route exists.

This is a pure source-level negative test: no listening socket, database,
credential, provider request, or host access is involved.
"""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from rezon.collective_http import _Handler


def _anonymous_get(path: str):
    # Exercise the real route ordering, but reject authentication before any
    # store access.  A live host or bearer token is deliberately unnecessary.
    handler = object.__new__(_Handler)
    handler.path = path
    handler._identity = Mock(return_value=None)
    handler._json = Mock()
    handler.server = SimpleNamespace(store=Mock())

    handler._dispatch("GET")
    handler._identity.assert_called_once_with(method="GET", path=path)
    handler.server.store.readable.assert_not_called()
    handler._json.assert_called_once_with(401, {"error": "unauthorized"})
    return handler._json.call_args.args


class RouteAmbiguityTests(unittest.TestCase):
    def test_unauthenticated_readyz_401_is_indistinguishable_from_missing_route_401(self):
        # A caller who has not authenticated sees the same response regardless
        # of whether readiness is implemented. HTTP 401 cannot be interpreted
        # as route presence, store readiness, or authorization to activate.
        registered = _anonymous_get("/readyz")
        unregistered = _anonymous_get("/__rezon_route_intentionally_absent")
        self.assertEqual(registered, unregistered)
        self.assertEqual(registered, (401, {"error": "unauthorized"}))


if __name__ == "__main__":
    unittest.main()
