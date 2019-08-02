SHELL         = ./make-venv
PYTHON        = C:/ProgramFiles/Python/python
PROJECT_ROOT  = $(shell pwd)
VENV          = ${PROJECT_ROOT}/venv

.PHONY: help clean clean-venv activate deactivate

clean-venv:
	if [ -d "${VENV}" ]; then \
        ${VENV}/Scripts/deactivate; \
        rm -rf ${VENV}; \
    fi

install-packages:venv
	${PYTHON} -m pip install setuptools Pillow xlsxwriter twine

venv:${VENV}

${VENV}:
	${PYTHON} -m venv ${VENV}




