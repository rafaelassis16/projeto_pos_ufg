# Makefile for To-Do API

.PHONY: install run test setup clean

install:
	powershell -ExecutionPolicy Bypass -File scripts/install.ps1

run:
	powershell -ExecutionPolicy Bypass -File scripts/run.ps1

test:
	powershell -ExecutionPolicy Bypass -File scripts/test.ps1

setup:
	powershell -ExecutionPolicy Bypass -File scripts/setup_env.ps1

clean:
	if exist .venv rmdir /s /q .venv
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .coverage del .coverage
	if exist app\tests\results rmdir /s /q app\tests\results
