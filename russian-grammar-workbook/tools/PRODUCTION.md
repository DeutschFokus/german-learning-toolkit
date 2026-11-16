# Production notes (content format and house rules)

Build: `python3 tools/build.py` (full book) · `--only m07` (one unit) · `--qa` (checks only, prints type mix and warnings).
Output: `output/russian-grammar-mastery-workbook.pdf`, `output/exercise-ledger.csv`.

## Content file format (`content/mNN.txt`, `content/rN.txt`)

```
@module 7            (reviews: @review 3, @title, @covers, @intro)
@part II
@title Instrumental case
@ru Творительный падеж — с кем? чем? кем?
@learn …             (repeatable: "In this module" bullets)
@target …            (repeatable: personal pattern chips)
@remix …             (repeatable: retry-with-new-examples instructions)
@lesson … @endlesson (lesson markup: ## h3, ### h4, | tables |, > ru || en, !> wrong || right || note,
                      - bullets, ::: rule|mistakes|contrast|tip Title … :::)
@stage A|B|C|D|E     (reviews use @block 1 | Title)
#A                   (exercise type letter, then fields)
Q: question   H: hint (stage A)   N: instruction   A: answer   V: also correct   W: why/how explanation
```

Types: A missing endings · B form from lemma · C preposition + ending · D conjugation · E aspect ·
F unjumble (chunks separated by " / ") · G error correction (N states number of errors) ·
H transformation (N states the change) · I mixed completion.

Gaps: `__` = ending, `___` = one word (preposition), `__________` = whole phrase/verb.
Answers for A/C list filled words in order (separate groups with `;`). Stem before `__` must begin the answer word.

## House rules
- 40 exercises per module (8 per stage), 35 per review. Type mix per unit = PLAN in build.py.
- Every gap sentence must make gender/number recoverable (context words, names, «всеми», «двумя», N: notes).
- Explanations: name the case/rule, the trigger, gender/number, and each ending change; for aspect explain the
  context (process, duration, repetition, completed whole, result, sequence). No generic copy-paste.
- If several answers are valid, give them in V: or in W:.
- Recycle the learner's patterns: с моими студентами, о моём плане, моему другу, в России, из арабоязычных стран,
  с преподавателем испанского языка, на этот вопрос, через две недели, через два месяца, пользоваться телефоном,
  работать на ноутбуке, зависеть от количества учеников, у меня была плохая связь, помогать мне исправлять ошибки,
  интересоваться русским языком, ни в одной русскоязычной стране, относиться к китайскому языку, нет свободного времени.
- Contexts: online German teaching, students, Russian/Chinese study, laptop/phone, video calls, internet problems,
  gym, friends, plans, travel, shops, restaurants, transport, appointments, home life.
