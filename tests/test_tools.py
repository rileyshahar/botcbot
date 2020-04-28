"""Tests for lib.logic.tools."""

from unittest import TestCase

from lib.logic import tools
from lib.logic.Character import Traveler
from tests.helpers import MockContext, MockPlayer
from tests.blns import blns


class TestGenerateGameInfoMessage(TestCase):
    """Tests for tools.generate_game_info_message."""

    def setUp(self):
        """Set the tests up."""
        self.context = MockContext()
        self.order = [
            MockPlayer(),
            MockPlayer(character=Traveler, position=2),
            MockPlayer(dead_votes=-1, position=3),
            MockPlayer(dead_votes=5, position=4),
        ]
        self.order[0].ghost.return_value = False
        self.order[1].ghost.return_value = False
        self.order[2].ghost.return_value = True
        self.order[3].ghost.return_value = True

    def test_generate_player_line(self):
        """Test that a normal player's line is generated normally."""
        for content in blns:
            with self.subTest(content=content):
                self.order[0].nick = content
                self.assertEqual(
                    f"\n{content}",
                    tools._generate_player_line(self.context, self.order[0]),
                )

    def test_generate_player_line_addendum(self):
        """Test that Traveler's line is generated with the proper addendum."""
        self.assertTrue(
            tools._generate_player_line(self.context, self.order[0]).endswith(
                f" - {self.order[0].character.name}"
            ),
        )

    def test_generate_player_line_dead_votes(self):
        """Test that dead players' lines are generated with the proper dead votes."""
        self.assertIn("X", tools._generate_player_line(self.context, self.order[2]))
        self.assertIn("O" * 5, tools._generate_player_line(self.context, self.order[3]))
