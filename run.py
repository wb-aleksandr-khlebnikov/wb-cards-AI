import os
import subprocess
import sys

def main():
    print("📦 Проверка .venv окружения...")

    if not os.path.isdir(".venv"):
        print("🧪 Создание виртуального окружения...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)

    # Путь к pip в виртуалке
    pip_path = os.path.join(".venv", "bin", "pip") if os.name != "nt" else ".venv\\Scripts\\pip.exe"
    python_path = os.path.join(".venv", "bin", "python") if os.name != "nt" else ".venv\\Scripts\\python.exe"

    print("📦 Установка зависимостей из requirements.txt...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)

    print("🚀 Запуск analyze_cards.py...")
    subprocess.run([python_path, "analyze_cards.py"], check=True)

if __name__ == "__main__":
    main()
