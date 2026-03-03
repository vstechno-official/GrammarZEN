import re
from typing import List, Tuple


CONFUSED_WORDS = [
    {
        'pattern': r'\bthere\s+(report|reports|homework|assignment|assignments|submission|submissions|work|project|projects|idea|ideas|opinion|opinions|car|house|phone|bag|book|books|name|names|plan|plans|team|goal|goals|result|results|effort|efforts|contribution|contributions|performance|proposal|proposals|feedback|response|responses|answer|answers|solution|solutions|decision|decisions|problem|problems|concern|concerns|responsibility|responsibilities|role|roles|duty|duties|task|tasks|schedule|deadline|deadlines)\b',
        'wrong': 'there',
        'correct': 'their',
        'message': 'Did you mean "their" (possessive) instead of "there" (location)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'THERE_THEIR_CONFUSION',
    },
    {
        'pattern': r'\b(submitted|lost|forgot|finished|completed|started|changed|updated|sold|bought|found|missed|received|sent|read|wrote|returned|filed|uploaded|downloaded|shared|published|reviewed|approved|rejected|signed|delivered|presented|collected|gathered|checked|prepared|organized|managed|handled|processed|removed|deleted|created|designed|built|fixed|repaired|moved|took|grabbed|packed|opened|closed|left|forgot)\s+there\b',
        'wrong': 'there',
        'correct': 'their',
        'message': 'Did you mean "their" (possessive) instead of "there" (location)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'THERE_THEIR_CONFUSION',
    },
    {
        'pattern': r'\blast\s+weak\b',
        'wrong': 'weak',
        'correct': 'week',
        'message': 'Did you mean "week" (a period of seven days) instead of "weak" (not strong)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'WEAK_WEEK_CONFUSION',
    },
    {
        'pattern': r'\bnext\s+weak\b',
        'wrong': 'weak',
        'correct': 'week',
        'message': 'Did you mean "week" (a period of seven days) instead of "weak" (not strong)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'WEAK_WEEK_CONFUSION',
    },
    {
        'pattern': r'\bevery\s+weak\b',
        'wrong': 'weak',
        'correct': 'week',
        'message': 'Did you mean "week" (a period of seven days) instead of "weak" (not strong)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'WEAK_WEEK_CONFUSION',
    },
    {
        'pattern': r'\bthis\s+weak\b',
        'wrong': 'weak',
        'correct': 'week',
        'message': 'Did you mean "week" (a period of seven days) instead of "weak" (not strong)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'WEAK_WEEK_CONFUSION',
    },
    {
        'pattern': r'\bper\s+weak\b',
        'wrong': 'weak',
        'correct': 'week',
        'message': 'Did you mean "week" (a period of seven days) instead of "weak" (not strong)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'WEAK_WEEK_CONFUSION',
    },
    {
        'pattern': r'\byour\s+(is|are|was|were|has|have|had|will|would|could|should|can|may|might|shall|do|does|did|been|being|not|never|always|also|just|already|still|very|really|so|too|quite|rather|here|going|coming|doing|making|getting|running|walking|talking|working|trying|looking|leaving|staying|moving|thinking|feeling|living|eating|sleeping|playing|writing|reading|singing|dancing|swimming|driving|flying|learning|teaching|studying|growing|falling|rising|sitting|standing)\b',
        'wrong': 'your',
        'correct': "you're",
        'message': 'Did you mean "you\'re" (you are) instead of "your" (possessive)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'YOUR_YOURE_CONFUSION',
    },
    {
        'pattern': r'\bwhere\s+(due|born|raised|located|placed|kept|stored|hidden|found|seen|heard|made|built|created|sold|bought)\b',
        'wrong': 'where',
        'correct': 'were',
        'message': 'Did you mean "were" (past tense of "be") instead of "where" (location)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'WHERE_WERE_CONFUSION',
    },
    {
        'pattern': r'\bwe\s+was\b',
        'wrong': 'was',
        'correct': 'were',
        'message': 'Use "were" with "we" \u2014 "we were" is correct.',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\bthey\s+was\b',
        'wrong': 'was',
        'correct': 'were',
        'message': 'Use "were" with "they" \u2014 "they were" is correct.',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\byou\s+was\b',
        'wrong': 'was',
        'correct': 'were',
        'message': 'Use "were" with "you" \u2014 "you were" is correct.',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\b(he|she|it)\s+were\b(?!\s+(to|able|not\s+able))',
        'wrong': 'were',
        'correct': 'was',
        'message': 'Use "was" with singular subjects like "he", "she", or "it".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\bI\s+is\b',
        'wrong': 'is',
        'correct': 'am',
        'message': 'Use "am" with "I" \u2014 "I am" is correct.',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\bI\s+are\b',
        'wrong': 'are',
        'correct': 'am',
        'message': 'Use "am" with "I" \u2014 "I am" is correct.',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\b(he|she|it)\s+are\b',
        'wrong': 'are',
        'correct': 'is',
        'message': 'Use "is" with singular subjects like "he", "she", or "it".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\b(he|she|it)\s+have\b(?!\s+(to|been|got))',
        'wrong': 'have',
        'correct': 'has',
        'message': 'Use "has" with singular subjects like "he", "she", or "it".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\b(I|we|they|you)\s+has\b',
        'wrong': 'has',
        'correct': 'have',
        'message': 'Use "have" with plural subjects or "I".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\b(he|she|it)\s+don\'t\b',
        'wrong': "don't",
        'correct': "doesn't",
        'message': 'Use "doesn\'t" with singular subjects like "he", "she", or "it".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\b(I|we|they|you)\s+doesn\'t\b',
        'wrong': "doesn't",
        'correct': "don't",
        'message': 'Use "don\'t" with plural subjects or "I".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\bwhich\s+were\s+due\b',
        'wrong': 'were',
        'correct': 'was',
        'message': 'When "which" refers to a singular noun, use "was" instead of "were".',
        'category': 'GRAMMAR',
        'rule_id': 'WHICH_AGREEMENT',
    },
    {
        'pattern': r'\b(alot)\b',
        'wrong': 'alot',
        'correct': 'a lot',
        'message': '"Alot" is not a word. Use "a lot" (two words).',
        'category': 'GRAMMAR',
        'rule_id': 'ALOT_A_LOT',
    },
    {
        'pattern': r'\b(definately|definatly|defintely|definetly|defiantly)\b',
        'wrong': None,
        'correct': 'definitely',
        'message': 'The correct spelling is "definitely".',
        'category': 'TYPOS',
        'rule_id': 'DEFINITELY_SPELLING',
    },
    {
        'pattern': r'\brecieve\b',
        'wrong': 'recieve',
        'correct': 'receive',
        'message': 'The correct spelling is "receive". Remember: "i before e except after c".',
        'category': 'TYPOS',
        'rule_id': 'RECEIVE_SPELLING',
    },
    {
        'pattern': r'\brecieved\b',
        'wrong': 'recieved',
        'correct': 'received',
        'message': 'The correct spelling is "received". Remember: "i before e except after c".',
        'category': 'TYPOS',
        'rule_id': 'RECEIVE_SPELLING',
    },
    {
        'pattern': r'\brecieves\b',
        'wrong': 'recieves',
        'correct': 'receives',
        'message': 'The correct spelling is "receives". Remember: "i before e except after c".',
        'category': 'TYPOS',
        'rule_id': 'RECEIVE_SPELLING',
    },
    {
        'pattern': r'\brecieving\b',
        'wrong': 'recieving',
        'correct': 'receiving',
        'message': 'The correct spelling is "receiving". Remember: "i before e except after c".',
        'category': 'TYPOS',
        'rule_id': 'RECEIVE_SPELLING',
    },
    {
        'pattern': r'\boccured\b',
        'wrong': 'occured',
        'correct': 'occurred',
        'message': 'The correct spelling is "occurred" (double r).',
        'category': 'TYPOS',
        'rule_id': 'OCCURRED_SPELLING',
    },
    {
        'pattern': r'\boccuring\b',
        'wrong': 'occuring',
        'correct': 'occurring',
        'message': 'The correct spelling is "occurring" (double r).',
        'category': 'TYPOS',
        'rule_id': 'OCCURRED_SPELLING',
    },
    {
        'pattern': r'\b(goed|buyed|costed|teached|catched|bringed|thinked|writed|drived|speaked|breaked|choosed|stealed|fighted|hided|keeped|leaved|meaned|payed|putted|runned|sayed|seed|sended|singed|sitted|sleeped|swinged|taked|throwed|weared|winned)\b',
        'wrong': None,
        'correct': None,
        'message': 'This appears to be an incorrect past tense form. English has many irregular verbs.',
        'category': 'GRAMMAR',
        'rule_id': 'IRREGULAR_VERB',
    },
    {
        'pattern': r'\b(grammer)\b',
        'wrong': 'grammer',
        'correct': 'grammar',
        'message': 'The correct spelling is "grammar".',
        'category': 'TYPOS',
        'rule_id': 'GRAMMAR_SPELLING',
    },
    {
        'pattern': r'\b(competiton|competion)\b',
        'wrong': None,
        'correct': 'competition',
        'message': 'The correct spelling is "competition".',
        'category': 'TYPOS',
        'rule_id': 'COMPETITION_SPELLING',
    },
    {
        'pattern': r'\b(happend|happned)\b',
        'wrong': None,
        'correct': 'happened',
        'message': 'The correct spelling is "happened".',
        'category': 'TYPOS',
        'rule_id': 'HAPPENED_SPELLING',
    },
    {
        'pattern': r'\bpeople\s+chooses\b',
        'wrong': 'chooses',
        'correct': 'choose',
        'message': '"People" is plural \u2014 use "choose" instead of "chooses".',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\bwe\s+has\b',
        'wrong': 'has',
        'correct': 'have',
        'message': 'Use "have" with "we" \u2014 "we have" is correct.',
        'category': 'GRAMMAR',
        'rule_id': 'SUBJECT_VERB_AGREEMENT',
    },
    {
        'pattern': r'\bvery\s+very\b',
        'wrong': 'very very',
        'correct': 'very',
        'message': 'Avoid repeating "very". Consider using a stronger word instead.',
        'category': 'STYLE',
        'rule_id': 'WORD_REPETITION',
    },
    {
        'pattern': r'\b(Their)\s+(are|is)\s+(many|several|some|few|no|a)\b',
        'wrong': None,
        'correct': 'There',
        'message': 'Did you mean "There" (existential) instead of "Their" (possessive)?',
        'category': 'CONFUSED_WORDS',
        'rule_id': 'THEIR_THERE_CONFUSION',
    },
]


def _get_context(text: str, start: int, length: int, context_size: int = 40) -> str:
    ctx_start = max(0, start - context_size)
    ctx_end = min(len(text), start + length + context_size)
    return text[ctx_start:ctx_end]


def _apply_correction(text: str, issues: List[Tuple[int, int, str]]) -> str:
    sorted_issues = sorted(issues, key=lambda x: x[0], reverse=True)
    result = text
    for offset, length, replacement in sorted_issues:
        result = result[:offset] + replacement + result[offset + length:]
    return result


def check_custom_rules(text: str) -> Tuple[list, str]:
    issues = []
    corrections = []
    found_ranges = []

    for rule in CONFUSED_WORDS:
        for match in re.finditer(rule['pattern'], text, re.IGNORECASE):
            wrong_word = rule.get('wrong')
            correct_word = rule.get('correct')
            message = rule.get('message')

            if not message:
                continue

            if wrong_word:
                try:
                    word_start = match.start() + match.group().lower().index(wrong_word.lower())
                except ValueError:
                    word_start = match.start()
                word_length = len(wrong_word)
            else:
                word_start = match.start()
                word_length = len(match.group())

            overlaps = any(
                not (word_start + word_length <= rs or word_start >= re_)
                for rs, re_ in found_ranges
            )
            if overlaps:
                continue
            found_ranges.append((word_start, word_start + word_length))

            replacements = [correct_word] if correct_word else []

            severity = 'error'
            if rule['category'] == 'STYLE':
                severity = 'warning'

            issues.append({
                'offset': word_start,
                'length': word_length,
                'message': message,
                'replacements': replacements,
                'rule_id': rule['rule_id'],
                'category': rule['category'],
                'context': _get_context(text, word_start, word_length),
                'severity': severity,
            })

            if correct_word:
                corrections.append((word_start, word_length, correct_word))

    corrected_text = _apply_correction(text, corrections) if corrections else text
    issues.sort(key=lambda x: x['offset'])
    return issues, corrected_text
