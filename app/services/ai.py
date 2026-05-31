import re
import os
import json
import httpx
from openai import AsyncOpenAI


client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


GENERATE_TASK_PROMPT = """
Ты — опытный технический интервьюер. Создай тестовое задание для кандидата.

Входные данные:
- Вакансия: {vacancy}
- Уровень: {level}
- Тема (необязательно): {topic}

Верни ТОЛЬКО валидный JSON без каких-либо пояснений и без markdown-блоков, строго в таком формате:
{{
  "title": "Краткое название задания",
  "description": "Подробное описание задания (2-4 абзаца)",
  "requirements": ["требование 1", "требование 2", "требование 3"],
  "tech_stack": "React, TypeScript, REST API",
  "difficulty": "{level}",
  "time_limit": 120
}}

Требования к заданию:
- Реалистичное, как в настоящей компании
- Соответствует уровню {level}
- time_limit в минутах (60-480)
- 3-6 конкретных требований
- Описание на русском языке
"""


REVIEW_SOLUTION_PROMPT = """
Ты — строгий технический интервьюер в крупной компании. Оцени решение кандидата.

Задание:
Название: {title}
Описание: {description}
Требования:
{requirements}

Решение кандидата:
{solution}

КРИТИЧЕСКИ ВАЖНО перед оценкой:
1. Проверь — соответствует ли технологический стек решения требованиям задания?
   Если задание требует React/TypeScript, а кандидат сдал Python/FastAPI — это ПРОВАЛ по correctness.
2. Выполнено ли каждое требование из списка? Отвечай по каждому пункту отдельно.
3. Если репозиторий содержит совсем другой проект — score не может быть выше 20.

Верни ТОЛЬКО валидный JSON без markdown-блоков:
{{
  "score": 75,
  "architecture_score": 80,
  "code_quality_score": 70,
  "correctness_score": 75,
  "feedback": "Подробный фидбэк: пройдись по КАЖДОМУ требованию — выполнено/не выполнено и почему. Если технологии не совпадают с заданием — укажи это явно в первом предложении. Упоминай конкретные файлы из кода. Минимум 6 предложений.",
  "improvements": "Конкретные пункты что нужно исправить, каждый с новой строки через \\n. Минимум 3 пункта.",
  "passed": true
}}

Правила оценки (строго):
- correctness_score: насколько решение соответствует заданию по технологиям и функционалу.
  Неправильный стек (например Python вместо React) = correctness_score не выше 10.
- score = среднее взвешенное: correctness 50%, code_quality 25%, architecture 25%
- passed: true только если score >= 65
- Если код не предоставлен — score не выше 30, попроси кандидата приложить репозиторий
- Весь текст строго на русском
"""


async def fetch_github_code(repo_url: str) -> str:
    """Скачивает файлы из публичного GitHub репо."""
    
    # Извлекаем owner/repo из ссылки
    match = re.search(r'github\.com/([^/]+)/([^/?\s]+)', repo_url)
    if not match:
        return ""
    
    owner, repo = match.group(1), match.group(2).rstrip('/')
    
    async with httpx.AsyncClient() as client:
        # Получаем дерево файлов
        tree_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )
        if tree_resp.status_code != 200:
            return ""
        
        files = tree_resp.json().get("tree", [])
        
        # Фильтруем только исходники (не берём lock-файлы и бинарники)
        CODE_EXTENSIONS = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go',
            '.rs', '.cpp', '.c', '.cs', '.rb', '.php', '.sql',
            '.html', '.css', '.json', '.yaml', '.yml', '.md'
        }
        SKIP = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'}
        
        code_files = [
            f for f in files
            if f['type'] == 'blob'
            and any(f['path'].endswith(ext) for ext in CODE_EXTENSIONS)
            and f['path'].split('/')[-1] not in SKIP
            and f.get('size', 0) < 50000  # пропускаем огромные файлы
        ][:20]  # максимум 20 файлов чтобы не перегружать контекст
        
        # Скачиваем содержимое каждого файла
        result = []
        for file in code_files:
            resp = await client.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{file['path']}",
                timeout=10,
            )
            if resp.status_code == 200:
                result.append(f"### {file['path']}\n{resp.text}")
        
        return "\n\n".join(result)


async def generate_task(vacancy: str, level: str, topic: str = "") -> dict:
    prompt = GENERATE_TASK_PROMPT.format(
        vacancy=vacancy,
        level=level,
        topic=topic or "не указана"
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()

    # Убираем markdown-блоки если вдруг модель добавила
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    return json.loads(raw)


async def review_solution(title, description, requirements, solution, repo_url=None) -> dict:
    
    code_context = ""
    
    if repo_url and "github.com" in repo_url:
        try:
            code = await fetch_github_code(repo_url)
            if code:
                code_context = f"\n\nКод из репозитория:\n{code}"
        except Exception:
            pass  # если не удалось скачать — проверяем только по тексту
    
    prompt = REVIEW_SOLUTION_PROMPT.format(
        title=title,
        description=description,
        requirements="\n".join(f"- {r}" for r in requirements),
        solution=solution + code_context,  # добавляем код к решению
    )
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    return json.loads(raw)