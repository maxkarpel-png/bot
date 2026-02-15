import os
import unittest
from decimal import Decimal
from unittest.mock import patch

from polymarket_bot.config import ConfigError, load_config


class TestConfig(unittest.TestCase):
    def test_live_mode_requires_credentials(self) -> None:
        env = {
            "POLYMARKET_DRY_RUN": "false",
            "POLYMARKET_API_KEY": "",
            "POLYMARKET_API_SECRET": "",
            "POLYMARKET_API_PASSPHRASE": "",
        }
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaises(ConfigError):
                load_config()

    def test_parses_boolean_and_decimals(self) -> None:
        env = {
            "POLYMARKET_DRY_RUN": "Yes",
            "POLYMARKET_MIN_EDGE": "0.015",
            "POLYMARKET_MAX_ORDER_SIZE": "3",
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = load_config()
        self.assertTrue(cfg.dry_run)
        self.assertEqual(cfg.min_edge, Decimal("0.015"))
        self.assertEqual(cfg.max_order_size, Decimal("3"))


if __name__ == "__main__":
    unittest.main()
