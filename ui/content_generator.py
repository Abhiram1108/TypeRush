"""
TypeRush 2.1 Content Generation & Unified Text Buffer Engine

Provides rich, offline, curated text streams for the unified typing experience.
Replaces the six-mode selector with coherent, natural, readable English sentences
across four distinct difficulty levels:
- Easy: Common vocabulary, short sentences, simple punctuation, comfortable flow.
- Medium: Varied vocabulary, moderate sentence length, natural commas and periods.
- Hard: Longer sentences, rich vocabulary, complex clauses, semicolons, quotes, questions.
- Expert: Advanced vocabulary, academic/literary syntax, challenging punctuation and numbers.

Features:
- Completely offline, standard-library based (random, typing).
- Infinite buffer generation: generates initial text stream and seamlessly
  appends more text whenever the untyped buffer drops below threshold.
- Stateful shuffled-deck cycling: prevents consecutive sentence repetition and
  avoids repeating recently used sentences within a rolling window.
- Deterministic seeding support for automated tests.
- Backwards compatibility for legacy mode parameters.
"""

import random
from typing import List, Dict, Tuple, Optional


# ============================================================================
# UNIFIED CURATED SENTENCE BANKS BY DIFFICULTY (35+ Sentences per Tier)
# ============================================================================

UNIFIED_PASSAGES_BY_DIFFICULTY: Dict[str, List[str]] = {
    "Easy": [
        "Today is a calm, sunny day, and the blue sky looks clear.",
        "Can you hear the birds singing softly near the quiet river?",
        "It is time to begin, so let us focus on steady typing.",
        "Practice makes steady progress, one keystroke at a time.",
        "Keep your eyes on the screen, relax your hands, and breathe.",
        "When the wind blows gently, leaves dance along the garden path.",
        "She smiled warmly, opened the book, and started reading aloud.",
        "Is speed important? Yes, but accuracy builds true confidence.",
        "A cup of warm tea is wonderful on a chilly morning.",
        "The train arrived right on schedule at the small station.",
        "Learning a new skill takes patience, focus, and daily practice.",
        "The gentle rain tapped against the window as night fell.",
        "Good habits are built step by step through quiet dedication.",
        "He found an old wooden box hidden under the library shelf.",
        "Clear thinking leads to simple solutions and peaceful days.",
        "Fresh air and morning walks bring energy to the mind.",
        "The little cat rested quietly in the warm afternoon sun.",
        "They walked along the shore, watching waves roll onto the sand.",
        "Music filled the room as the violin played a sweet melody.",
        "Every journey begins with a single, deliberate step forward.",
        "The bright morning sun warmed the green valley below.",
        "We sat beside the fire, enjoying stories from long ago.",
        "A little kindness can make a world of difference to someone.",
        "The clock on the wall ticked steadily through the evening.",
        "He packed his bag, grabbed his coat, and walked out the door.",
        "Spring brings fresh blossoms and green grass to every meadow.",
        "She found a smooth blue stone while walking near the pond.",
        "Reading a good book is like taking a trip to a distant place.",
        "The bakery filled the whole street with the smell of fresh bread.",
        "Stay patient and keep practicing, because improvement takes time.",
        "A quiet walk in the forest helps clear the busiest mind.",
        "The stars shone brightly in the clear winter sky tonight.",
        "He placed the golden key carefully into the iron lock.",
        "Small daily achievements lead to great accomplishments over time.",
        "The river flowed smoothly between the tall green trees.",
        "Take a deep breath, sit comfortably, and type with ease.",
    ],
    "Medium": [
        '"Success is not final, and failure is not fatal," the mentor reminded us.',
        "If you practice daily, your typing cadence will improve; however, patience is essential.",
        "Why did the software engineer choose Python? Because it is concise, readable, and elegant.",
        "In the quiet laboratory, researchers observed the reaction: heat rose, and color shifted.",
        "Before submitting your project, double-check all calculations, layouts, and test logs.",
        'The speaker asked, "How many of you believe that focus is the key to deep mastery?"',
        "Mechanical switches offer tactile feedback, distinct acoustics, and crisp actuation points.",
        "Although the deadline approached swiftly, the engineering team remained calm, organized, and focused.",
        "Modern operating systems coordinate memory, storage, and processing cores with remarkable efficiency.",
        "To achieve a steady typing rhythm, prioritize accuracy over raw speed during your initial practice sessions.",
        "The library contained thousands of historical manuscripts, each preserved in climate-controlled archives.",
        "Digital typography requires careful attention to kerning, leading, and proportional hierarchy.",
        "Astronomers monitored the night sky as the comet passed within view of the mountain observatory.",
        "Effective communication requires active listening, concise phrasing, and empathetic consideration.",
        "The quarterly report showed a 14.8% increase in overall productivity across all regional offices.",
        "Sustainable architecture balances ecological conservation with functional contemporary design.",
        "A well-structured codebase minimizes technical debt and accelerates collaborative innovation.",
        "During the autumn festival, lanterns illuminated the cobblestone pathways throughout the old town.",
        "The compiler optimizes abstract syntax trees to generate highly efficient machine instructions.",
        "When designing responsive layouts, ensure interface components scale gracefully across resolutions.",
        "Consistent typing rhythm depends on muscle memory rather than frantic finger movement.",
        "The art gallery showcased contemporary sculptures crafted from recycled industrial copper and steel.",
        "Researchers published an intriguing paper analyzing network traffic patterns across distributed nodes.",
        "Careful code reviews promote software reliability and foster collective architectural ownership.",
        "The musician tuned each string precisely before the evening symphony performance commenced.",
        "A modular software architecture simplifies testing, debugging, and future feature expansion.",
        "Understanding algorithmic complexity enables developers to choose the right data structure for the job.",
        "The expedition team established a base camp at high altitude before attempting the summit ridge.",
        "Clean documentation bridges the gap between complex engineering systems and end-user comprehension.",
        "Analytical thinkers dissect complicated problems into smaller, manageable, and solvable components.",
        "The morning fog gradually lifted, revealing a panoramic view of the rugged coastline.",
        "High-performance workstations require balanced cooling solutions to prevent thermal throttling.",
        "Balancing work, creative exploration, and personal rest sustains long-term intellectual vitality.",
        "The historical expedition uncovered ancient pottery fragments buried deep beneath desert dunes.",
        "Consistent deliberate practice transforms tentative keystrokes into fluid, instinctive keyboard fluency.",
    ],
    "Hard": [
        '"Wait," she whispered, looking through the frosted pane; "did you observe that sudden anomaly?"',
        "Although the hypothesis seemed promising (as demonstrated in preliminary trials), several variables shifted unexpectedly during phase two.",
        "Architectural balance dictates that latency, throughput, and fault tolerance must be carefully measured; premature optimization remains counterproductive.",
        "Modern distributed algorithms—especially consensus protocols like Raft and Paxos—require rigorous mathematical proofs to guarantee data integrity.",
        "Could the anomalous signal originate from background thermal noise, or does it represent genuine coherent communication across interstellar distances?",
        "When designing resilient user interfaces, engineers must balance aesthetic minimalism with discoverability; otherwise, usability suffers.",
        "The archaeological expedition uncovered a subterranean corridor, dating back to approximately 450 BCE, lined with intricate limestone carvings.",
        "Quantum superposition allows computational states to coexist simultaneously; however, environmental decoherence rapidly collapses fragile wavefunctions.",
        "Beneath the dense canopy of the temperate rainforest, biodiversity flourishes in microclimates that remain insulated from seasonal fluctuations.",
        "Cryptographic signatures guarantee authenticity and non-repudiation, provided the underlying private key remains strictly confidential.",
        "According to empirical observations recorded between 2018 and 2025, cognitive endurance improves measurably when study sessions incorporate scheduled intervals.",
        "The philosophical dialogue explored whether human consciousness can ever be completely replicated by deterministic silicon architectures.",
        "Heterogeneous computing clusters distribute computational workloads across GPUs, TPUs, and high-frequency vector processing units.",
        "Theoretical linguistics investigates the underlying grammatical recursion shared across seemingly disparate natural human languages.",
        "During peak atmospheric turbulence, automated avionics systems execute microsecond corrections to maintain flight trajectory and stability.",
        "Epistemological inquiries challenge fundamental assumptions regarding empirical observation, objective reality, and cognitive bias.",
        "Modern compiler optimization passes transform intermediate representations through static single assignment (SSA) form.",
        "The marine biologist cataloged bioluminescent organisms residing in the abyssal zone, where hydrostatic pressure exceeds 1,000 atmospheres.",
        "Resilient cryptographic handshakes employ ephemeral Diffie-Hellman exchanges to guarantee forward secrecy against future decryption.",
        "Nanostructured carbon allotropes demonstrate extraordinary tensile strength, superior thermal conductivity, and chemical inertness.",
        "The sociopolitical historian examined how decentralized communication networks influenced civic mobilization during the late twentieth century.",
        "Spatial indexing algorithms, including R-trees and bounding volume hierarchies, accelerate geometric collision detection in three-dimensional simulations.",
        "By decomposing monolithic applications into decoupled microservices, organizations enhance fault isolation but introduce distributed consensus overhead.",
        "The mathematical proof established that the conjectured boundary conditions hold universally across all non-trivial complex dimensions.",
    ],
    "Expert": [
        '"To understand recursive computation," the computer science professor remarked with a subtle smile, "one must first understand recursion; nonetheless, a well-defined base case remains indispensable."',
        "Notwithstanding the remarkable convergence of empirical observations, theoretical physicists continue to debate whether spacetime emerges from quantum entanglement—or vice versa.",
        "In high-frequency algorithmic trading systems, a microscopic delay of 250 nanoseconds (measured at the network interface layer) often determines profitability; consequently, lock-free ring buffers predominate.",
        "Epistemological skepticism questions whether sensory perception accurately reflects objective physical reality: if cognitive models are evolutionary approximations, can empirical verification ever achieve absolute certainty?",
        "In the High-Performance Computing (HPC) benchmark suite v8.4, the 128-core cluster executed 1.845 x 10^15 FLOPS; CPU temperature peaked at 74.2°C with 99.995% uptime.",
        "Article §4.2.1 of the ACM Code of Ethics stipulates that professionals must protect privacy: 'Systems processing personal data (e.g., ISO/IEC 27001 compliant) require end-to-end encryption.'",
        "During audit #9902-A on 10/31/2026, the algorithmic engine processed 1,420,500 transactions/sec (mean latency: 1.85 microseconds, 99.9th percentile <= 4.20 microseconds).",
        "The aerodynamic profile of hypersonic transport aircraft requires composite carbon-matrix alloys capable of withstanding thermal gradients exceeding 1,800°C without structural fatigue.",
        "Heterogeneous multi-core architectures leverage specialized neural processing units (NPUs) to parallelize tensor contractions while maintaining sub-15W thermal dissipation budgets.",
        "In non-Euclidean differential geometry, the Riemann curvature tensor R(u,v)w characterizes the failure of second covariant derivatives to commute on Riemannian manifolds.",
        "Zero-knowledge succinct non-interactive arguments of knowledge (zk-SNARKs) allow a prover to establish mathematical assertion validity without disclosing proprietary parameters.",
        "Astrophysical simulations modeling magnetohydrodynamic accretion disks around Kerr black holes require relativistic general covariance and adaptive mesh refinement.",
        "By deploying transactional memory paradigms (STM) with optimistic concurrency control, multi-threaded kernels reduce lock contention across 512-socket NUMA domains.",
        "Sub-nanometer lithographic fabrication utilizes extreme ultraviolet (EUV) light at 13.5nm wavelengths, demanding mirror surface planarities accurate to within atomic radii.",
    ],
    "Code": [
        "const calculateScore = (hits, misses) => Math.max(0, Math.round((hits / (hits + misses)) * 100));",
        "def fetch_user_profile(user_id: int) -> dict: return db.query('SELECT * FROM users WHERE id = %s', (user_id,))",
        "for (let i = 0; i < items.length; i++) { if (items[i].status === 'active') activeList.push(items[i]); }",
        "result = [x * 2 for x in dataset if x % 2 == 0 and x is not None]",
        "class Node: def __init__(self, val, next=None): self.val = val; self.next = next",
        "int binary_search(const int arr[], int n, int key) { int l = 0, r = n - 1; while (l <= r) { int m = l + (r - l) / 2; if (arr[m] == key) return m; if (arr[m] < key) l = m + 1; else r = m - 1; } return -1; }",
        "async function loadConfig(url) { const res = await fetch(url); if (!res.ok) throw new Error(res.statusText); return await res.json(); }",
        "def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr[1:] if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr[1:] if x >= arr[0]])",
        "export interface UserSession { id: string; token: string; expiresAt: number; roles: string[]; }",
        "SELECT u.id, u.username, COUNT(o.id) AS total_orders FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id;",
        "std::vector<int> filter_primes(const std::vector<int>& numbers) { std::vector<int> primes; for (int n : numbers) if (is_prime(n)) primes.push_back(n); return primes; }",
        "def normalize_vector(v: list[float]) -> list[float]: norm = sum(x*x for x in v) ** 0.5; return [x / norm for x in v] if norm > 0 else v",
        "try { const data = JSON.parse(raw); return validateSchema(data); } catch (err) { logger.error('Failed to parse schema:', err); }",
        "def memoize(fn): cache = {}; return lambda *args: cache.setdefault(args, fn(*args))",
        "const debounce = (fn, delay = 250) => { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); }; };",
        "if __name__ == '__main__': app = create_app(); app.run(host='0.0.0.0', port=8080, debug=False)",
        "type Predicate<T> = (value: T, index: number) => boolean; function partition<T>(items: T[], fn: Predicate<T>): [T[], T[]] { return [items.filter(fn), items.filter((x, i) => !fn(x, i))]; }",
        "with open('config.yaml', 'r', encoding='utf-8') as stream: config = yaml.safe_load(stream)",
        "double calculate_variance(const double data[], int count) { double mean = compute_mean(data, count); double sum = 0.0; for (int i = 0; i < count; ++i) sum += (data[i] - mean) * (data[i] - mean); return sum / count; }",
        "git commit -m 'feat: implement cascade-immune error alignment and monospace caret navigation'",
    ],
}


# ============================================================================
# LEGACY WORD BANKS (Retained for Backwards Compatibility)
# ============================================================================

WORDS_BY_DIFFICULTY: Dict[str, List[str]] = {
    "Easy": [
        "the", "and", "for", "you", "say", "get", "make", "know", "time", "year",
        "good", "day", "man", "find", "give", "work", "call", "look", "hand", "high",
        "keep", "part", "turn", "show", "move", "play", "run", "walk", "jump", "fast",
        "blue", "tree", "sun", "road", "wind", "sea", "bird", "gold", "star", "fire",
        "home", "life", "book", "food", "rain", "dark", "cool", "warm", "boat", "fish",
        "rock", "path", "hill", "lake", "moon", "leaf", "song", "door", "room", "city",
    ],
    "Medium": [
        "about", "before", "change", "differ", "family", "govern", "happen", "impact",
        "letter", "moment", "number", "person", "reason", "school", "system", "theory",
        "travel", "water", "world", "young", "action", "create", "design", "effort",
        "future", "global", "nature", "simple", "result", "energy", "market", "policy",
    ],
    "Hard": [
        "absolute", "boundary", "capacity", "deliberate", "efficient", "frequent",
        "generate", "horizontal", "identify", "judgment", "knowledge", "language",
        "movement", "necessary", "obstacle", "potential", "quantity", "resource",
        "standard", "tradition", "universe", "variable", "wanderer", "yielding",
    ],
    "Expert": [
        "accumulate", "characteristic", "differentiate", "environmental", "fundamental",
        "heterogeneous", "infrastructure", "jurisdiction", "kaleidoscope", "logarithmically",
        "methodological", "nomenclature", "philosophical", "quantitative", "rehabilitation",
        "synchronization", "transformation", "unprecedented", "vulnerability", "weatherproofing",
    ],
}


# ============================================================================
# CONTENT GENERATOR CLASS
# ============================================================================

class ContentGenerator:
    """
    Stateful infinite text buffer generator for typing tests.
    Produces natural, readable, grammatically coherent English sentences.
    Seamless offline stream of continuous typing material.
    Guarantees zero consecutive repetitions and avoids repeating recently used sentences.
    """

    MODES = ["Unified", "Mixed", "Words", "Punctuation", "Capitalization", "Numbers", "Code"]
    DIFFICULTIES = ["Easy", "Medium", "Hard", "Expert", "Code"]

    def __init__(self, mode: str = "Unified", difficulty: str = "Medium", seed: Optional[int] = None):
        self.mode = mode if mode in self.MODES else "Unified"
        self.difficulty = difficulty if difficulty in self.DIFFICULTIES else "Medium"
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.code_index = 0
        self._shuffled_deck: List[str] = []
        self._recent_sentences: List[str] = []
        self._last_selected_sentence: Optional[str] = None
        self._custom_text: Optional[str] = None
        self._custom_words: List[str] = []
        self._custom_index: int = 0

    def set_custom_text(self, text: str) -> None:
        """Inject custom user text for specialized practice."""
        clean = " ".join(text.strip().split())
        if clean:
            self._custom_text = clean
            self._custom_words = clean.split()
            self._custom_index = 0

    def clear_custom_text(self) -> None:
        """Clear custom user text and resume standard deck generation."""
        self._custom_text = None
        self._custom_words = []
        self._custom_index = 0

    def generate_weak_key_practice(self, weak_keys: List[str], word_target: int = 50) -> str:
        """Generate targeted practice passages rich in the user's weak characters."""
        if not weak_keys:
            return self.generate_initial_buffer(min_words=word_target)

        keys_set = {k.lower() for k in weak_keys}
        # Gather all sentences across difficulties
        all_sentences = []
        for pool in UNIFIED_PASSAGES_BY_DIFFICULTY.values():
            all_sentences.extend(pool)

        # Score sentences by frequency of weak keys
        scored = []
        for s in all_sentences:
            s_lower = s.lower()
            score = sum(1 for ch in s_lower if ch in keys_set)
            if score > 0:
                scored.append((score, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        chosen = [s for _, s in scored[:10]]
        if not chosen:
            return self.generate_initial_buffer(min_words=word_target)

        self.rng.shuffle(chosen)
        result = []
        count = 0
        idx = 0
        while count < word_target and idx < len(chosen) * 3:
            s = chosen[idx % len(chosen)]
            result.append(s)
            count += len(s.split())
            idx += 1
        return " ".join(result)

    def set_config(self, mode: str, difficulty: str) -> None:
        """Update active mode and difficulty, resetting sentence deck."""
        if mode in self.MODES:
            self.mode = mode
        if difficulty in self.DIFFICULTIES:
            if self.difficulty != difficulty:
                self.difficulty = difficulty
                self._shuffled_deck = []
                self._recent_sentences = []
                self._last_selected_sentence = None

    def _get_next_sentence(self, pool: List[str]) -> str:
        """
        Stateful deck exhaustion algorithm:
        Pulls from shuffled deck without replacement.
        Guarantees that consecutive sentences are never identical.
        Avoids repeating any sentence within rolling window.
        """
        if not self._shuffled_deck:
            deck = list(pool)
            self.rng.shuffle(deck)
            # Ensure the first sentence of the new shuffle is not the same as the last sentence selected
            if len(deck) > 1 and deck[0] == self._last_selected_sentence:
                deck[0], deck[-1] = deck[-1], deck[0]
            self._shuffled_deck = deck

        # Try to find next sentence that is not in recent history
        candidate = None
        for i in range(len(self._shuffled_deck)):
            cand = self._shuffled_deck[i]
            if cand not in self._recent_sentences and cand != self._last_selected_sentence:
                candidate = self._shuffled_deck.pop(i)
                break

        if candidate is None:
            # If all remaining in deck were in recent history, pop the first that isn't the last selected
            for i in range(len(self._shuffled_deck)):
                if self._shuffled_deck[i] != self._last_selected_sentence:
                    candidate = self._shuffled_deck.pop(i)
                    break
            if candidate is None:
                candidate = self._shuffled_deck.pop(0)

        self._last_selected_sentence = candidate
        self._recent_sentences.append(candidate)
        # Keep recent window reasonable (e.g. 10 sentences)
        if len(self._recent_sentences) > 12:
            self._recent_sentences.pop(0)

        return candidate

    def generate_chunk(self, word_target: int = 40) -> str:
        """
        Generate a cohesive chunk of natural text appropriate for current difficulty.
        """
        # 1. Custom User Text
        if self._custom_text and self._custom_words:
            chunk = []
            while len(chunk) < word_target:
                chunk.append(self._custom_words[self._custom_index % len(self._custom_words)])
                self._custom_index += 1
            return " ".join(chunk)

        if self.mode == "Words":
            pool = WORDS_BY_DIFFICULTY.get(self.difficulty, WORDS_BY_DIFFICULTY["Medium"])
            words = [self.rng.choice(pool) for _ in range(word_target)]
            return " ".join(words)

        # Code Mode or Code Difficulty
        if self.mode == "Code" or self.difficulty == "Code":
            pool = UNIFIED_PASSAGES_BY_DIFFICULTY.get("Code", [])
            selected = []
            word_count = 0
            while word_count < word_target:
                snippet = self._get_next_sentence(pool)
                selected.append(snippet)
                word_count += len(snippet.split())
            return " ".join(selected)

        # Unified typing experience (Default & standard for all tests)
        pool = UNIFIED_PASSAGES_BY_DIFFICULTY.get(self.difficulty, UNIFIED_PASSAGES_BY_DIFFICULTY["Medium"])
        selected = []
        word_count = 0
        while word_count < word_target:
            sentence = self._get_next_sentence(pool)
            selected.append(sentence)
            word_count += len(sentence.split())
        return " ".join(selected)

    def generate_initial_buffer(self, min_words: int = 120) -> str:
        """
        Generate a robust initial typing buffer containing at least min_words.
        Guarantees no consecutive sentence repetition.
        """
        chunks = []
        words_so_far = 0
        while words_so_far < min_words:
            chunk = self.generate_chunk(word_target=45)
            chunks.append(chunk)
            words_so_far += len(chunk.split())
        return " ".join(chunks)

    def generate_continuation(self, min_words: int = 40) -> str:
        """
        Generate an additional text segment to seamlessly append to the typing buffer.
        """
        return " " + self.generate_chunk(word_target=min_words)
