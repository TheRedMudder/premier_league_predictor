# Quick Start
1. Add API KEY
Replace `KEY` in `constant.py` with your API Key
2. Enable API 
Set `USE_API` to `True` in `football_api.py`
3. Run `python structure_data.py`
4. Disable API
Set `USE_API` to `False` in `football_api.py`

# Caching
`USE_API=False` in `structure_data.py` will prevent API request. When `False` it will read `all_games.pickle`, which stores the unmodified FootBall API request.