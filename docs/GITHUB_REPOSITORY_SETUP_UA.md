# GitHub repository setup після створення проєкту з template

Цей файл — практичний чекліст для власника проєкту. Він потрібен тому, що repository-level налаштування GitHub не слід вважати автоматично перенесеними в новий repository, створений через **Use this template**.

Після створення кожного нового проєкту пройди цей файл один раз зверху вниз.

> Якщо назви пунктів у GitHub UI трохи змінилися, орієнтуйся на зміст правила, а не лише на точний текст кнопки.

## 1. Для самого template repository

Для `template-for-agents` один раз перевір:

`Settings -> General -> Template repository`

- [ ] `Template repository` увімкнено.

Це дає кнопку **Use this template** для створення нових незалежних repository.

Для repository, який уже створений із template, цей пункт зазвичай не потрібен, якщо ти не хочеш зробити і його template.

## 2. Створи Ruleset для `main`

Відкрий:

`Settings -> Rules -> Rulesets -> New branch ruleset`

Рекомендовані верхні налаштування:

```text
Ruleset name: Protect main
Enforcement status: Active
Bypass list: empty
Target branches: Include default branch
```

`Include default branch` означає, що правила застосовуються до `main`, але не блокують звичайну роботу `task/*` та `integration/*` branches.

Не використовуй `Include all branches` для цього базового ruleset.

## 3. Branch rules для `main`

Увімкни:

- [x] Restrict deletions
- [x] Block force pushes
- [x] Require linear history
- [x] Require a pull request before merging
- [x] Require status checks to pass

Поки залиш вимкненими, якщо конкретний проєкт не має окремої причини:

- [ ] Restrict creations
- [ ] Restrict updates
- [ ] Require deployments to succeed
- [ ] Require signed commits
- [ ] Require code scanning results
- [ ] Require code quality results
- [ ] Restrict code coverage
- [ ] Automatically request Copilot code review

## 4. Налаштування `Require a pull request before merging`

Рекомендована база для solo owner + AI agents:

```text
Required approvals: 0
Dismiss stale approvals: OFF
Require review from specific teams: OFF
Require review from Code Owners: OFF
Require approval of the most recent reviewable push: OFF
Require conversation resolution before merging: ON
Additional approval for unattributed Copilot PRs: OFF
```

Чому approvals = 0: AI-агенти не є незалежними human reviewers у GitHub. Якщо пізніше в проєкті з'явиться команда людей, тоді окремо розглянь `Required approvals: 1` або більше.

### Allowed merge methods

Для агентної розробки залиш:

```text
Squash: ON
Merge: OFF
Rebase: OFF
```

Squash дозволяє worker branch мати внутрішні технічні commits, але в `main` залишає один зрозумілий commit на PR.

## 5. Налаштування `Require status checks to pass`

Увімкни правило й додай required check:

```text
policy
```

Залежно від UI він може відображатися як `policy` або `CI / policy`.

Це job із `.github/workflows/ci.yml`, який запускає:

```text
python3 scripts/check_actions_policy.py
```

Залиш:

```text
Require branches to be up to date before merging: OFF
Do not require status checks on creation: OFF
```

Перший пункт залишає перевірки у більш легкому режимі й не змушує без потреби повторно ганяти CI після кожного руху `main`.

### Якщо `policy` не видно у списку checks

GitHub іноді показує check лише після того, як він хоча б раз був створений workflow.

Тоді:

1. відкрий `Actions -> CI`;
2. дочекайся першого push-to-main run або використай `Run workflow` (`workflow_dispatch`);
3. переконайся, що run успішний;
4. повернися в Ruleset;
5. додай `policy` як required check.

Не запускай workflow багато разів лише для того, щоб він з'явився у списку.

## 6. Merge settings repository

Відкрий:

`Settings -> General -> Pull Requests`

Рекомендовано:

```text
Allow squash merging: ON
Allow merge commits: OFF
Allow rebase merging: OFF
```

Це має відповідати `Allowed merge methods` у Ruleset.

Також увімкни:

- [x] Automatically delete head branches

Після merge GitHub автоматично прибере вже непотрібні `task/*` branches.

## 7. GitHub Actions permissions

Відкрий:

`Settings -> Actions -> General -> Workflow permissions`

Вибери найбільш read-only / restricted варіант, який дозволяє workflow читати repository contents, а не загальний read/write доступ.

Базовий `ci.yml` додатково сам обмежує token:

```yaml
permissions:
  contents: read
```

Тобто repository-level setting і workflow-level setting працюють разом за принципом least privilege.

Якщо майбутньому deployment/release workflow справді потрібен write-доступ, видавай його лише цьому конкретному workflow і лише на необхідний scope.

## 8. Public repository: approval для зовнішніх PR workflow

Для public repository відкрий:

`Settings -> Actions -> General`

Знайди секцію на кшталт:

`Approval for running fork pull request workflows from contributors`

Рекомендовано:

- [x] Require approval for all external contributors

Це не дає сторонньому fork/PR автоматично використовувати твої GitHub-hosted workflow без контролю.

Для private/internal repository доступні опції можуть відрізнятися — тоді зберігай той самий принцип: незнайомий зовнішній код не повинен автоматично отримувати довірений CI-контекст.

## 9. Що НЕ потрібно захищати тим самим ruleset

Не застосовуй `Protect main` до всіх branches.

Нормальна модель:

```text
main                       -> жорстко захищений
integration/<feature>      -> робоча інтеграція
task/<feature>-frontend    -> worker branch
task/<feature>-backend     -> worker branch
task/<feature>-qa          -> worker branch
```

Task/integration branches повинні залишатися достатньо гнучкими для агентної роботи, а контрольна межа стоїть перед `main`.

## 10. Мінімальна фінальна перевірка

Після налаштування нового repository:

- [ ] Default branch — `main`.
- [ ] Ruleset `Protect main` — Active.
- [ ] Target — Include default branch.
- [ ] Bypass list — empty.
- [ ] Direct delete `main` заблокований.
- [ ] Force push у `main` заблокований.
- [ ] PR required перед merge.
- [ ] Conversation resolution required.
- [ ] Linear history required.
- [ ] Required check `policy` доданий.
- [ ] `Require branches to be up to date` не ввімкнений без окремої причини.
- [ ] Squash — єдиний merge method.
- [ ] Merged head branches видаляються автоматично.
- [ ] Default Actions token permissions read-only/restricted.
- [ ] Для public repo зовнішні fork workflow потребують approval.

## 11. Швидка пам'ятка

```text
Use this template
        |
        v
new repository
        |
        +-> Settings / Rules / Protect main
        +-> PR required
        +-> policy check required
        +-> squash only
        +-> no force push / no delete
        +-> auto-delete merged branches
        +-> Actions token read-only
        +-> external fork workflow approval
        |
        v
після цього починай substantial agent work
```

Якщо сумніваєшся в конкретному перемикачі GitHub, не послаблюй `main` навмання. Звір його з `AGENTS.md`, `docs/GITHUB_ACTIONS_POLICY.md` і цим чеклістом.