.PHONY: install lint freeze

# Set the default task to lint
.DEFAULT_GOAL := run


install:
	@echo "Upgrading pip..."
	@pip install --upgrade pip

	@echo "Installing dependencies..."
	@pip install -r requirements.txt


clean:
	@echo "Cleaning up..."
	@find . -name "junit.xml" -type f -delete
	@find . -name "report" -type d -exec rm -rf {} +

lint:
	@echo "Running linters..."
	@echo "Running flake8..."
	@flake8 .
	@echo "Running pylint..."
	@pylint --rcfile=setup.cfg .

test: clean lint
	@echo "Running Unit Tests..."
	@coverage run -m pytest -m unit -v
	@echo "Done"

freeze:
	@pip freeze > requirements.txt


docker:
	docker build -t example_project:latest .


run: docker
	@echo "Server is running on http://localhost:8080/docs"
	docker run  -p 8080:8000 testcontainer-fastapi-demo:latest

#	@echo "To stop the server, run 'docker ps' to get the container ID and then run 'docker stop <container_id>'"