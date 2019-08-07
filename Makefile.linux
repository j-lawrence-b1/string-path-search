PROJECT_ROOT  = $(shell pwd)
VENV          = ${PROJECT_ROOT}/venv
DIST          = ${PROJECT_ROOT}/dist
TEMP          = ${PROJECT_ROOT}/tests/temp
BUILD         = ${PROJECT_ROOT}/build
OUT_DIR       = ${PROJECT_ROOT}/temp
EGG_INFO      = ${PROJECT_ROOT}/string_path_search.egg-info
MAKEFILE_LIST = ${PROJECT_ROOT}/Makefile

.PHONY: help clean clean-dist clean-venv install-packages

help: ## Show this help message.
	@echo 'usage: make [target] ...'
	@echo
	@echo 'targets:'
	@egrep  '^(.+):(.*) ## (.+)' ${MAKEFILE_LIST} | grep -v egrep | sed 's/:.*##/: ##/' | column -t -c 2 -s ':#'

real-clean:clean-venv clean ## In addition to the regular clean, cleanup the python virtual environment.

clean: clean-build clean-dist ## cleanup build and distribution products
	for dir in ${BUILD} ${DIST} ${EGG_INFO}; do \
    if [ -d "${EGG_INFO}" ]; then \
        rm -r $dir; \
    fi

clean-venv: ## Cleanup this project's Python virtual environment
	if [ -d "${VENV}" ]; then \
        $(. ${VENV}/Scripts/deactivate; rm -rf ${VENV}); \
    fi

venv:${VENV} ## Setup a Python virtual environment for this project.

${VENV}:
	${PYTHON} -m venv ${VENV}

install-packages:venv ## Install third party packages required to build this project
	$(. ${VENV}/Scripts/activate; ${PYTHON} -m pip install --upgrade \
    pylint nose2 setuptools Pillow xlsxwriter twine)

test: ## Use nose2 to run the test scripts.
	$(. ${VENV}/Scripts/activate; ${PYthon} -m no)

