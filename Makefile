SRC = src/
OBJ = $(SRC)*.py
MAIN = pac-man.py

VENV = .venv/

PYTHON = python3
DEBUGGER = $(PYTHON) pdb

RM = rm -fr

.ONESHELL:

install: $(VENV)
	@$(VENV)/bin/pip install --upgrade pip
	@$(VENV)/bin/pip install -r requirements.txt
	@source $(VENV)/bin/activate


$(VENV):
	@$(PYTHON) -m venv $(VENV)

run:
	@export PYGAME_HIDE_SUPPORT_PROMPT=1
	$(PYTHON) $(MAIN) config_file.json

debug:
	@export PYGAME_HIDE_SUPPORT_PROMPT=1
	$(DEBUGGER) $(MAIN) config_file.json

clean:
	@$(RM) ./__pycache__/ ./.mypy_cache/
	@$(RM) ./$(SRC)/__pycache__/ ./$(SRC)/.mypy_cache/

fclean: clean
	@$(RM) ./$(VENV)

lint:
	@$(PYTHON) -m flake8 $(OBJ) $(MAIN) || true
	@$(PYTHON) -m mypy $(OBJ) $(MAIN) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(OBJ) || true

lint-strict:
	@$(PYTHON) -m flake8 $(OBJ) $(MAIN) || true
	@$(PYTHON) -m mypy --strict $(OBJ) $(MAIN) || true

%:
	@:

run_dan:
	$(PYTHON) dan_test.py config_file.json
