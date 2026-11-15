"""
TypeRush 2.1 Word-Level and Character-Level Error Alignment Engine

Solves the cascade alignment problem where a single typo previously shifted
and ruined subsequent correct words.

Architecture:
- Word-Level Segmentation: The target text and user inputs are tokenized into words with exact character spans.
- Independent Word Evaluation: Each word is compared to its target counterpart.
- Levenshtein & Positional Character Alignment: Inside each word, substitutions,
  insertions (extra characters), and deletions (missing characters) are identified.
- Cascade Immunity: Errors in word N do NOT shift word N+1 or subsequent words.
- Case-Insensitive Matching: Prevents false penalties for uppercase/lowercase differences
  while retaining punctuation verification.
- Protected Spacebar: Commits active words and ignores empty repetitions.
- Native Text Cursor Mapping: Provides exact character offsets for native Text widget cursor positioning.
"""

import re
from typing import List, Dict, Tuple, Optional, Any


class WordEvaluation:
    """Evaluation result for an individual word."""
    def __init__(
        self,
        word_index: int,
        expected: str,
        typed: str,
        is_completed: bool,
        is_correct: bool,
        correct_chars: int,
        incorrect_chars: int,
        char_statuses: List[Tuple[str, str]]  # list of (char, status: 'correct'|'incorrect'|'extra')
    ):
        self.word_index = word_index
        self.expected = expected
        self.typed = typed
        self.is_completed = is_completed
        self.is_correct = is_correct
        self.correct_chars = correct_chars
        self.incorrect_chars = incorrect_chars
        self.char_statuses = char_statuses

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word_index": self.word_index,
            "expected": self.expected,
            "typed": self.typed,
            "is_completed": self.is_completed,
            "is_correct": self.is_correct,
            "correct_chars": self.correct_chars,
            "incorrect_chars": self.incorrect_chars,
        }


def levenshtein_align(expected: str, typed: str) -> List[Tuple[Optional[str], Optional[str], str]]:
    """
    Compute optimal character alignment between expected word and typed word.
    Case-insensitive matching ensures standard typing conventions while
    strictly preserving punctuation accuracy.
    Returns list of (expected_char, typed_char, op: 'match'|'sub'|'insert'|'delete').
    """
    m, n = len(expected), len(typed)
    # dp[i][j] stores minimum edit distance
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if expected[i - 1].lower() == typed[j - 1].lower():
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j - 1],  # substitution
                    dp[i][j - 1],      # insertion (extra char in typed)
                    dp[i - 1][j]       # deletion (missing char from expected)
                )

    # Backtrack to reconstruct alignment
    i, j = m, n
    alignment = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and expected[i - 1].lower() == typed[j - 1].lower():
            alignment.append((expected[i - 1], typed[j - 1], "match"))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            alignment.append((expected[i - 1], typed[j - 1], "sub"))
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            alignment.append((None, typed[j - 1], "insert"))
            j -= 1
        else:
            alignment.append((expected[i - 1], None, "delete"))
            i -= 1

    alignment.reverse()
    return alignment


class TypingAlignmentEngine:
    """
    High-precision stateful typing alignment engine.
    Maintains target words, user typed words, exact character spans, and current cursor.
    Provides word-level and character-level accuracy without cascade error shifting.
    """

    def __init__(self, target_text: str = ""):
        self.target_text: str = ""
        self.expected_words: List[str] = []
        self.word_char_spans: List[Tuple[int, int]] = []
        self.typed_words: List[str] = []
        self.current_word_idx: int = 0
        self.is_completed: bool = False

        if target_text:
            self.set_target_text(target_text)

    def _compute_spans(self) -> None:
        """Compute exact (start_char_idx, end_char_idx) in target_text for each word."""
        self.word_char_spans = []
        for match in re.finditer(r'\S+', self.target_text):
            self.word_char_spans.append((match.start(), match.end()))

    def set_target_text(self, text: str) -> None:
        """Initialize engine with new target passage."""
        self.target_text = text
        self.expected_words = text.split()
        self._compute_spans()
        self.typed_words = ["" for _ in self.expected_words]
        self.current_word_idx = 0
        self.is_completed = False

    def append_target_text(self, text_chunk: str) -> None:
        """
        Append additional text dynamically for continuous stream mode.
        Seamlessly extends expected words and typed slots without resetting progress.
        """
        if not text_chunk:
            return
        if self.target_text and not self.target_text.endswith(" ") and not text_chunk.startswith(" "):
            self.target_text += " " + text_chunk
        else:
            self.target_text += text_chunk

        new_words = text_chunk.split()
        if new_words:
            self.expected_words.extend(new_words)
            self._compute_spans()
            self.typed_words.extend(["" for _ in new_words])
            self.is_completed = False

    def handle_character(self, char: str) -> bool:
        """
        Process printable character input.
        Returns True if a word was committed via Space, False otherwise.
        """
        if self.current_word_idx >= len(self.expected_words):
            return False

        if char == " ":
            # Space commits current word and advances to next word.
            # Empty words do not advance on space (prevents runaway skipped words).
            if len(self.typed_words[self.current_word_idx]) == 0:
                return False

            if self.current_word_idx < len(self.expected_words) - 1:
                self.current_word_idx += 1
            elif self.current_word_idx == len(self.expected_words) - 1:
                self.is_completed = True
            return True

        # Regular character: append to current typed word
        self.typed_words[self.current_word_idx] += char
        return False

    def handle_backspace(self) -> None:
        """
        Process Backspace key within current active word.
        Keeps committed words safely isolated.
        """
        if self.current_word_idx < len(self.typed_words):
            cur = self.typed_words[self.current_word_idx]
            if len(cur) > 0:
                # Delete last character of current word
                self.typed_words[self.current_word_idx] = cur[:-1]

    def get_current_word_and_char_index(self) -> Tuple[int, int]:
        """Return (word_index, char_index_in_word)."""
        char_idx = len(self.typed_words[self.current_word_idx]) if self.current_word_idx < len(self.typed_words) else 0
        return self.current_word_idx, char_idx

    def get_current_caret_index(self) -> int:
        """
        Return the exact character index in target_text where the caret should sit.
        For active word, sits at start + min(typed_len, expected_len).
        """
        if self.current_word_idx >= len(self.word_char_spans):
            return len(self.target_text)

        start, end = self.word_char_spans[self.current_word_idx]
        typed_len = len(self.typed_words[self.current_word_idx])
        expected_len = end - start
        return start + min(typed_len, expected_len)

    def get_word_span(self, word_idx: int) -> Tuple[int, int]:
        """Return (start_idx, end_idx) in target_text for specified word index."""
        if 0 <= word_idx < len(self.word_char_spans):
            return self.word_char_spans[word_idx]
        return 0, 0

    def is_word_correct(self, word_idx: int) -> bool:
        """Check if word at word_idx was typed correctly (case-insensitive for letters)."""
        if 0 <= word_idx < len(self.typed_words) and word_idx < len(self.expected_words):
            return self.typed_words[word_idx].lower() == self.expected_words[word_idx].lower()
        return False

    def get_remaining_untyped_words(self) -> int:
        """Return count of remaining words in buffer."""
        return max(0, len(self.expected_words) - self.current_word_idx)

    def evaluate(self) -> Dict[str, Any]:
        """
        Perform complete word-level and character-level alignment evaluation.
        Returns comprehensive metrics dictionary.
        Cascade Immunity: mistake in word N never cascades to word N+1.
        """
        total_correct_chars = 0
        total_incorrect_chars = 0
        actual_keystrokes = 0
        correct_words_count = 0
        incorrect_words_count = 0
        weak_key_counts: Dict[str, int] = {}
        word_evals: List[WordEvaluation] = []

        total_words_to_eval = min(self.current_word_idx + 1, len(self.expected_words))

        for w_idx in range(total_words_to_eval):
            expected = self.expected_words[w_idx]
            typed = self.typed_words[w_idx]
            is_active = (w_idx == self.current_word_idx)
            is_committed = (w_idx < self.current_word_idx) or (is_active and self.is_completed)

            # If active word has nothing typed yet at end of test, do not penalize as an incorrect word
            if is_active and typed == "" and not (w_idx < self.current_word_idx):
                continue

            char_statuses: List[Tuple[str, str]] = []
            word_correct_chars = 0
            word_incorrect_chars = 0
            word_keystrokes = len(typed)
            if w_idx < self.current_word_idx:
                word_keystrokes += 1  # Space that committed the word

            # Case-insensitive matching for letters
            if typed.lower() == expected.lower():
                word_is_correct = True
                word_correct_chars = len(expected)
                if w_idx < self.current_word_idx:
                    word_correct_chars += 1  # Trailing space counted
                char_statuses = [(c, "correct") for c in expected]
            else:
                align_ops = levenshtein_align(expected, typed)
                for exp_c, typ_c, op in align_ops:
                    if op == "match":
                        char_statuses.append((exp_c, "correct"))
                        word_correct_chars += 1
                    elif op in ("sub", "insert"):
                        display_c = typ_c if typ_c is not None else exp_c
                        char_statuses.append((display_c, "incorrect"))
                        word_incorrect_chars += 1
                        missed = exp_c or typ_c
                        if missed and missed.strip():
                            m_char = missed.lower()
                            weak_key_counts[m_char] = weak_key_counts.get(m_char, 0) + 1
                    elif op == "delete":
                        if is_committed:
                            word_incorrect_chars += 1
                            if exp_c and exp_c.strip():
                                m_char = exp_c.lower()
                                weak_key_counts[m_char] = weak_key_counts.get(m_char, 0) + 1

                if is_committed:
                    word_is_correct = False
                    if w_idx < self.current_word_idx:
                        word_correct_chars += 1  # Space separator typed
                else:
                    word_is_correct = False

            if is_committed:
                if word_is_correct:
                    correct_words_count += 1
                else:
                    incorrect_words_count += 1

            total_correct_chars += word_correct_chars
            total_incorrect_chars += word_incorrect_chars
            actual_keystrokes += word_keystrokes

            word_evals.append(WordEvaluation(
                word_index=w_idx,
                expected=expected,
                typed=typed,
                is_completed=is_committed,
                is_correct=word_is_correct,
                correct_chars=word_correct_chars,
                incorrect_chars=word_incorrect_chars,
                char_statuses=char_statuses
            ))

        total_typed = max(actual_keystrokes, total_correct_chars + total_incorrect_chars)
        total_eval_chars = total_correct_chars + total_incorrect_chars
        accuracy = round((total_correct_chars / total_eval_chars * 100.0), 1) if total_eval_chars > 0 else 100.0

        return {
            "correct_chars": total_correct_chars,
            "incorrect_chars": total_incorrect_chars,
            "total_chars": total_typed,
            "actual_keystrokes": actual_keystrokes,
            "accuracy": accuracy,
            "correct_words": correct_words_count,
            "incorrect_words": incorrect_words_count,
            "word_evaluations": word_evals,
            "current_word_idx": self.current_word_idx,
            "total_errors": total_incorrect_chars,
            "weak_keys": weak_key_counts,
        }
