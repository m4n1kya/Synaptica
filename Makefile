.PHONY: dev-backend dev-frontend install-backend clean

dev-backend:
	cd backend && uvicorn main:app --reload --port 8000

dev-frontend:
	npx serve frontend -p 3000

install-backend:
	cd backend && pip install -r requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf backend/.venv
