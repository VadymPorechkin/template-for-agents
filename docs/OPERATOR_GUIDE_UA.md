# Посібник оператора: як користуватися цим template

Цей файл призначений насамперед для власника/оператора проєкту. Його мета — щоб ключові налаштування, правила та порядок запуску нового проєкту не доводилося відновлювати з історії чатів.

## 1. Що дає цей template

Template не визначає мову програмування, framework чи базу даних. Він задає операційний каркас:

- правила роботи ШІ-агентів;
- безпечну роботу з Git;
- контроль GitHub Actions;
- місце для архітектури та рішень;
- базову структуру `src/`, `tests/`, `output/`;
- правила для одночасної роботи кількох агентів;
- шаблон handoff між агентами;
- захист від випадкового розширення CI/workflow.

## 2. Після створення нового проєкту з template

Пройди цей чекліст:

1. **Спочатку виконай `docs/GITHUB_REPOSITORY_SETUP_UA.md`.** GitHub Rulesets, merge settings та Actions permissions треба перевіряти для кожного нового repository окремо.
2. Перейменуй/перепиши `README.md` під конкретний продукт.
3. Визнач стек: мова, framework, package manager, база даних, test runner.
4. Доповни `.gitignore` під стек.
5. Заповни `.env.example` тільки назвами потрібних environment variables — без реальних секретів.
6. Заповни `docs/architecture.md` важливими межами й потоками системи.
7. Зафіксуй уже прийняті неочевидні рішення в `docs/decisions.md`.
8. Додай реальні команди lint/typecheck/test/build у `.github/workflows/ci.yml`, не змінюючи cost-control policy без окремої причини.
9. Якщо додаєш нові workflow, свідомо додай їх до allowlist у `scripts/check_actions_policy.py`.
10. Зроби початковий стабільний commit до великої агентної роботи.

## 3. Доступ агентів

Базове правило: агент отримує мінімально достатній доступ.

- Не відкривай агенту весь диск заради одного проєкту.
- Не давай write-доступ до даних, які задача не повинна змінювати.
- Не клади паролі, токени, API keys та приватні ключі в `AGENTS.md`, README або інші tracked-файли.
- Реальні `.env` залишаються локальними/секретними й не комітяться.
- Веб-доступ, browser/computer-use, конектори та інші інструменти додавай лише коли вони реально потрібні задачі.

`AGENTS.md` — це інструкція, а не абсолютний security barrier. Те, що не повинно статися ніколи, краще обмежувати permissions/sandbox/access scope.

## 4. Один агент

Для невеликої задачі достатньо:

```text
main
  -> task/<name>
      -> Draft PR
      -> implementation + local/agent-workspace checks
      -> one meaningful batch push
      -> Ready for review
      -> exact-head CI
      -> merge
```

Не роби push після кожної дрібної правки лише для запуску CI.

## 5. Кілька агентів одночасно

Повна модель описана в `docs/AGENT_WORKFLOW.md`.

Головна формула:

> **один одночасний агент = одна обмежена задача = одна task branch = одне ізольоване writable-середовище**

Для локальної Git-роботи таким середовищем зазвичай є **Git worktree**.

Приклад для великої функції:

```text
main
  |
  +-- integration/auth-redesign
        |
        +-- task/auth-design
        +-- task/auth-frontend
        +-- task/auth-backend
        +-- task/auth-qa
```

Фізично це може виглядати так:

```text
project-control/   -> integration/auth-redesign
project-design/    -> task/auth-design
project-frontend/  -> task/auth-frontend
project-backend/   -> task/auth-backend
project-qa/        -> task/auth-qa
```

Одночасні агенти не повинні писати в одну й ту саму робочу папку.

## 6. Роль Control / Integration Agent

Для суттєвої multi-agent задачі один агент виконує роль координатора.

Він:

- розуміє кінцевий результат;
- ділить задачу на незалежні частини;
- фіксує shared contracts до паралельної роботи;
- задає ownership;
- стежить, щоб агенти не лізли в чужий scope;
- переглядає diff і handoff кожного;
- інтегрує гілки в `integration/<feature>`;
- вирішує конфлікти на рівні поведінки/контрактів, а не просто тексту;
- організовує integrated QA;
- готує фінальний PR до `main`.

Головний агент не повинен без причини переписувати роботу всіх інших агентів.

## 7. Shared contracts

Паралельну реалізацію варто запускати лише після узгодження спільних меж.

Наприклад:

- API route + request/response schema;
- DB schema boundary;
- component props;
- event payload;
- environment-variable names;
- acceptance criteria;
- ownership paths.

Інакше frontend і backend можуть окремо бути правильними, але разом не працювати.

## 8. Ownership

Перед запуском паралельних агентів задай, хто за що відповідає.

Наприклад:

```text
Frontend:
  src/frontend/**
  src/components/**

Backend:
  src/backend/**
  database/**

QA:
  tests/integration/**
  validation evidence
```

Shared-файли (`package.json`, root config, shared schemas/types тощо) змінюються координовано.

Якщо агенту для своєї задачі треба змінити чужу область, він повинен підняти blocker/coordination request, а не самовільно розширити scope.

## 9. Handoff

Для паралельної роботи використовуй `docs/HANDOFF_TEMPLATE.md`.

Handoff потрібен, щоб control-agent або наступна сесія не відновлювали контекст із чату.

У ньому мають бути:

- задача і роль;
- base/final SHA;
- що змінено;
- рішення й припущення;
- що протестовано;
- що не тестувалося;
- blockers/limitations;
- contract changes;
- integration notes;
- rollback.

## 10. GitHub Actions — економія ліміту

Головний принцип:

> **CI is a review/release gate, not an iterative debugger.**

Поточний base workflow:

- важкий PR CI запускається на `ready_for_review` до `main`;
- є post-merge перевірка push у `main`;
- є manual `workflow_dispatch`;
- немає автоматичного `synchronize` full CI;
- є `concurrency` + `cancel-in-progress: true`;
- є timeout;
- permissions за замовчуванням read-only;
- checkout не зберігає credentials;
- `scripts/check_actions_policy.py` контролює drift.

Для multi-agent задачі worker-гілки за можливості перевіряються локально/в agent workspace. Основний дорогий checkpoint — зібрана integration-версія перед `main`.

## 11. Якщо CI впав

Не натискай rerun автоматично.

```text
CI FAIL
  -> прочитати logs
  -> code/test defect?
       так -> Draft -> bounded fix round -> batch push -> Ready
       ні  -> підтверджений transient GitHub/runner issue -> один обґрунтований rerun
```

## 12. Що змінювати під конкретний стек

Зазвичай змінюються:

- `README.md`;
- `.gitignore`;
- `.env.example`;
- `docs/architecture.md`;
- `docs/decisions.md`;
- `.github/workflows/ci.yml` (додаються реальні перевірки);
- `src/`;
- `tests/`.

Зазвичай майже без змін залишаються:

- базові принципи `AGENTS.md`;
- `docs/GITHUB_ACTIONS_POLICY.md`;
- `docs/GITHUB_REPOSITORY_SETUP_UA.md`;
- multi-agent принципи в `docs/AGENT_WORKFLOW.md`;
- `.editorconfig`;
- `.gitattributes`.

## 13. Коли НЕ потрібні кілька агентів

Не паралель роботу тільки тому, що це можливо.

Краще один агент, якщо:

- задача маленька;
- усі будуть редагувати ті самі файли;
- архітектура ще не визначена;
- друга задача повністю залежить від результату першої;
- координація дорожча за саму реалізацію.

## 14. Швидкий старт multi-agent задачі

Перед запуском перевір:

- [ ] Є чіткий кінцевий результат.
- [ ] Є integration branch, якщо задача справді велика.
- [ ] Кожен агент має окрему task branch.
- [ ] Одночасні агенти мають окремі worktree/ізольовані writable workspaces.
- [ ] Ownership записаний.
- [ ] Shared contracts записані.
- [ ] Acceptance criteria записані.
- [ ] Кожен знає, де залишити handoff.
- [ ] Worker agents не мають причини самовільно merge у `main`.
- [ ] Control agent відповідає за інтеграцію.
- [ ] QA перевіряє assembled integration state.
- [ ] Full CI не використовується як trial-and-error debugger.

## 15. Перед фінальним merge

- [ ] Усі worker handoff переглянуті.
- [ ] Shared-contract conflicts вирішені.
- [ ] Integration branch містить потрібні зміни всіх прийнятих задач.
- [ ] Integrated tests пройшли або blocker явно зафіксований.
- [ ] QA/review перевірив зібраний результат.
- [ ] Final PR head однозначний.
- [ ] CI evidence належить саме final head.
- [ ] Немає реальних секретів або mutable runtime data в Git.
- [ ] Є зрозумілий rollback для ризикових змін.

## 16. GitHub settings, які не можна забути

Після кожного **Use this template** відкрий `docs/GITHUB_REPOSITORY_SETUP_UA.md` до початку substantial agent work.

Найкоротший список:

```text
Protect main
+ PR required
+ policy status check required
+ squash only
+ block force push/delete
+ linear history
+ auto-delete merged branches
+ Actions token read-only
+ external fork workflow approval for public repos
```

Не покладайся на те, що ці repository-level settings автоматично скопіювалися з template repository.

## 17. Найкоротша пам'ятка

```text
мінімальні дозволи
+ короткий AGENTS.md
+ Git як точка повернення
+ один агент = одна ізольована область
+ contracts before parallel code
+ control agent integrates
+ QA tests assembled result
+ CI only at meaningful checkpoints
+ protected main
+ secrets never in Git
```

Якщо через кілька місяців забудеш, чому template влаштований саме так, починай із цього файла, потім читай `docs/GITHUB_REPOSITORY_SETUP_UA.md`, `AGENTS.md`, `docs/AGENT_WORKFLOW.md` і `docs/GITHUB_ACTIONS_POLICY.md`.
