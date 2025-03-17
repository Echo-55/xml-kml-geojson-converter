# Little script to make activating the virtual environment and running the main.py script easier.


Set-Location .venv\Scripts
.\Activate.ps1
Set-Location ..\..\

python main.py -i examples\aircraft_graveyards.xml -g -k -x