Set-Location -LiteralPath 'C:\Users\Fox\OneDrive\Рабочий стол\AI\text'
& "$env:APPDATA\npm\pi.ps1" --model 'openrouter/deepseek/deepseek-v4.1-flash' --role auditor -- '@.factory/logs/auditor-09-final-task.txt'
