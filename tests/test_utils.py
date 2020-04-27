"""Contains tests for lib.utils."""

import unittest
from unittest.mock import MagicMock

from discord import HTTPException

from lib import utils
from tests import helpers

# any strings should be fine here as long as they are shorter than 2000 characters,
# aren't precisely "cancel", and don't start with "@" or ","
_test_strings = ("hello world", "hello, world")


class TestGetPlayer(unittest.TestCase):
    """Tests for utils.get_player."""

    def setUp(self):
        """Set the tests up."""
        self.game = helpers.MockGame(
            seating_order=[helpers.MockPlayer(), helpers.MockPlayer()]
        )

    def test_get_player(self):
        """Test that get_player finds the correct player."""
        self.assertEqual(
            self.game.seating_order[0],
            utils.get_player(self.game, self.game.seating_order[0].member.id),
        )
        self.assertNotEqual(
            self.game.seating_order[0],
            utils.get_player(self.game, self.game.seating_order[1].member.id),
        )

    def test_get_player_storyteller(self):
        """Test that get_player finds storytellers."""
        self.assertEqual(
            self.game.storytellers[0],
            utils.get_player(self.game, self.game.storytellers[0].member.id),
        )

    def test_get_player_bad_input(self):
        """Test that get_player raises an exception if no player is found."""
        with self.assertRaises(ValueError) as cm:
            utils.get_player(self.game, -1)

        self.assertEqual(str(cm.exception), "player not found")


class TestGetInput(unittest.IsolatedAsyncioTestCase):
    """Tests for utils.get_input."""

    def setUp(self):
        """Set the tests up."""
        self.call_text = "text"
        self.context = helpers.MockContext()

    async def test_get_input(self):
        """Test that get_input returns the input's content."""

        for content in _test_strings:
            with self.subTest(content=content):
                self.context.reset_mock()
                self.context.bot.wait_for.return_value = helpers.MockMessage(
                    content=content
                )
                out = await utils.get_input(self.context, self.call_text)
                self.assertEqual(content, out)
                self.context.bot.wait_for.assert_called_once()
                self.context.send.assert_called_with(self.call_text)

    async def test_get_input_cancel(self):
        """Test that get_input raises an exception if cancelled."""
        self.context.bot.wait_for.return_value = helpers.MockMessage(content="cancel")
        with self.assertRaises(ValueError) as cm:
            await utils.get_input(self.context, self.call_text)

        self.assertEqual(str(cm.exception), "cancelled")

    async def test_get_input_command_called(self):
        """Test that get_input raises an exception if another command is called."""
        for prefix in self.context.bot.command_prefix:
            with self.subTest(prefix=prefix):
                self.context.bot.wait_for.return_value = helpers.MockMessage(
                    content=f"{prefix}hello world"
                )
                with self.assertRaises(ValueError) as cm:
                    await utils.get_input(self.context, self.call_text)

                self.assertEqual(str(cm.exception), "command called")


def _raise_if_longer(text: str, n: int = 2000):
    """Raise an HTTPException if the message is too long."""
    if len(text) > n:
        e = HTTPException(response=MagicMock(), message="")
        e.code = 50035
        raise e


class TestSafeSend(unittest.IsolatedAsyncioTestCase):
    """Tests for utils.safe_send."""

    def setUp(self):
        """Set the tests up."""
        self.context = helpers.MockContext()

        # we want .send to raise an error if the message is too long
        # because safe_send doesn't manually check message length
        self.context.send.side_effect = _raise_if_longer

    async def test_safe_send(self):
        """Test that safe_send properly sends a message."""
        for content in _test_strings:
            with self.subTest(content=content):
                await utils.safe_send(self.context, content)
                self.context.send.assert_called_with(content)

    @unittest.skip("Not yet implemented.")
    async def test_safe_send_long(self):
        """Test that safe_send properly sends long messages.

        This is hard to implement because safe_send is checking for HTTP errors, not for
        the actual length, so it's hard to dynamically determine what it should've been
        called with.
        """
        long_test_strings = (
            "A" * 2001,
            "A" * 12000,
            "A" * 1800 + "B" * 1800,
        )
        for content in long_test_strings:
            with self.subTest(content=content):
                await utils.safe_send(self.context, content)
                self.assertIn(
                    content[: len(content) // 2], self.context.send.call_args_list
                )
