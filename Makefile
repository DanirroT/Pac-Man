SRC = src/
OBJ = $(SRC)*.py

VENV = .venv/

PYTHON = python3
DEBUGGER = $(PYTHON) pdb

RM = rm -fr

.ONESHELL:

install: $(VENV)
	@$(VENV)/bin/pip install --upgrade pip
	@$(VENV)/bin/pip install -r requirements.txt
	

$(VENV):
	@$(PYTHON) -m venv $(VENV)

run:
	@$(PYTHON) $(SRC) config_file.json

debug:
	@$(DEBUGGER) $(MAIN).py config_file.json

clean:
	@$(RM) ./__pycache__/ ./.mypy_cache/
	@$(RM) ./$(SRC)/__pycache__/ ./$(SRC)/.mypy_cache/

fclean: clean
	@$(RM) ./$(VENV)

lint:
	@$(PYTHON) flake8 $(OBJ) || true
	@$(PYTHON) mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(OBJ) || true

lint-strict:
	@$(PYTHON) flake8 $(OBJ) || true
	@$(PYTHON) mypy --strict $(OBJ) || true

%:
	@:
