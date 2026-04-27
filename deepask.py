#!/usr/bin/env python3

import requests
import os
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich import box

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

console = Console()

if not API_KEY:
    console.print("[red]Ошибка:[/red] не задан DEEPSEEK_API_KEY")
    console.print("Пример: export DEEPSEEK_API_KEY='your_key'")
    exit(1)

history = [
    {
        "role": "system",
        "content": "Отвечай понятно и структурированно, без лишнего форматирования."
    }
]


def ask_deepseek(prompt):
    global history

    history.append({"role": "user", "content": prompt})

    data = {
        "model": "deepseek-chat",
        "messages": history
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        with console.status("[bold yellow]🤖 Думаю...[/bold yellow]"):
            response = requests.post(API_URL, headers=headers, json=data, timeout=60)
    except Exception as e:
        return f"[red]Ошибка соединения:[/red] {e}"

    if response.status_code != 200:
        return f"[red]Ошибка API:[/red] {response.text}"

    try:
        answer = response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "[red]Ошибка обработки ответа[/red]"

    history.append({"role": "assistant", "content": answer})

    return answer


def save_to_file(text):
    desktop = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop):
        desktop = os.path.expanduser("~/Рабочий стол")

    filename = f"{desktop}/deepask_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    console.print(f"[green]💾 Сохранено:[/green] {filename}")


def main():
    console.print(Panel("🔥 DeepAsk CLI", style="bold cyan", box=box.DOUBLE))

    console.print("[bold]Команды:[/bold]")
    console.print("[green]/exit[/green]  — выйти")
    console.print("[green]/save[/green]  — сохранить ответ\n")

    last_answer = ""

    while True:
        try:
            user_input = console.input("[bold green]👉 Ты:[/bold green] ")

            if not user_input.strip():
                continue

            if user_input == "/exit":
                break

            if user_input == "/save":
                if last_answer:
                    save_to_file(last_answer)
                else:
                    console.print("[red]Нет ответа для сохранения[/red]")
                continue

            answer = ask_deepseek(user_input)
            last_answer = answer

            console.print()
            console.print(Panel(
                Markdown(answer),
                title="[bold blue]🤖 DeepSeek[/bold blue]",
                border_style="blue"
            ))

        except KeyboardInterrupt:
            console.print("\n[red]Выход...[/red]")
            break


if __name__ == "__main__":
    main()
