VENV = . env/bin/activate;

env: requirements.txt
	test -d env || python3 -m venv env
	$(VENV) pip install -r requirements.txt
	touch env

freeze:
	$(VENV) pip freeze > requirements.txt

clean:
	$(RM) -r __pycache__

clean-env:
	$(RM) -r env

.PHONY: freeze

