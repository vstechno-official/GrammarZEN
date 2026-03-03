import language_tool_python
import threading
from dataclasses import dataclass, field
from typing import List
from custom_rules import check_custom_rules


@dataclass
class GrammarIssue:
    offset: int
    length: int
    message: str
    replacements: List[str]
    rule_id: str
    category: str
    context: str
    severity: str


@dataclass
class CorrectionResult:
    original_text: str
    corrected_text: str
    issues: List[GrammarIssue]
    score: float
    word_count: int
    sentence_count: int
    issue_count: int
    suggestions: List[str] = field(default_factory=list)
    readability_score: float = 0.0
    sentiment: str = "neutral"
    sentiment_polarity: float = 0.0
    avg_sentence_length: float = 0.0
    vocabulary_richness: float = 0.0
    processing_time_ms: int = 0


class GrammarEngine:
    _instance = None
    _lock = threading.Lock()
    _tool = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self):
        if self._tool is None:
            self._tool = language_tool_python.LanguageTool(
                'en-US',
                config={
                    'maxSpellingSuggestions': 5,
                    'maxCheckThreads': 4,
                }
            )

    def get_tool(self):
        if self._tool is None:
            self.initialize()
        return self._tool

    def _calculate_severity(self, rule_id: str, category: str) -> str:
        critical = ['MORFOLOGIK_RULE', 'GRAMMAR', 'TYPOS']
        warning = ['STYLE', 'REDUNDANCY', 'REPETITIONS_STYLE']
        for r in critical:
            if r in rule_id or r in category:
                return 'error'
        for r in warning:
            if r in rule_id or r in category:
                return 'warning'
        return 'style'

    def correct(self, text: str) -> CorrectionResult:
        import time
        start = time.time()
        tool = self.get_tool()
        matches = tool.check(text)
        issues = []
        for m in matches:
            issues.append(GrammarIssue(
                offset=m.offset,
                length=m.error_length,
                message=m.message,
                replacements=list(m.replacements[:5]),
                rule_id=m.rule_id,
                category=m.category,
                context=m.context,
                severity=self._calculate_severity(m.rule_id, m.category)
            ))
        corrected = language_tool_python.utils.correct(text, matches)
        custom_issues, custom_corrected = check_custom_rules(text)
        existing_ranges = [(i.offset, i.offset + i.length) for i in issues]
        for ci in custom_issues:
            ci_start = ci['offset']
            ci_end = ci_start + ci['length']
            overlaps = any(
                not (ci_end <= es or ci_start >= ee)
                for es, ee in existing_ranges
            )
            if not overlaps:
                issues.append(GrammarIssue(
                    offset=ci['offset'],
                    length=ci['length'],
                    message=ci['message'],
                    replacements=ci['replacements'],
                    rule_id=ci['rule_id'],
                    category=ci['category'],
                    context=ci['context'],
                    severity=ci['severity']
                ))
        if custom_issues and not matches:
            corrected = custom_corrected
        elif custom_issues:
            corrected = check_custom_rules(corrected)[1]
        words = text.split()
        sentences = [s.strip() for s in __import__('re').split(r'[.!?]+', text) if s.strip()]
        word_count = len(words)
        sentence_count = max(len(sentences), 1)
        issue_count = len(issues)
        severity_weights = {'error': 15, 'warning': 8, 'style': 3}
        weighted_penalty = sum(severity_weights.get(i.severity, 8) for i in issues)
        error_density = issue_count / max(word_count, 1)
        density_multiplier = 1.0 + min(error_density * 5, 2.0)
        penalty = min(weighted_penalty * density_multiplier, 95)
        score = max(100 - penalty, 5) if text.strip() else 0
        avg_sent = round(word_count / sentence_count, 1)
        unique_words = set(w.lower().strip('.,!?;:') for w in words)
        vocab_richness = round((len(unique_words) / max(word_count, 1)) * 100, 1)
        elapsed = int((time.time() - start) * 1000)
        return CorrectionResult(
            original_text=text,
            corrected_text=corrected,
            issues=issues,
            score=round(score, 1),
            word_count=word_count,
            sentence_count=sentence_count,
            issue_count=issue_count,
            processing_time_ms=elapsed,
            avg_sentence_length=avg_sent,
            vocabulary_richness=vocab_richness
        )

    def is_ready(self) -> bool:
        return self._tool is not None
