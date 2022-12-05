# build poetry
FROM quay.io/centos/centos:stream8 as poetry

RUN dnf -y module install python39 && dnf -y install python39 python39-pip && dnf -y install procps-ng pcp pcp-export-pcp2json sysstat #collectl

WORKDIR /app

COPY poetry.lock /app/
COPY pyproject.toml /app/

RUN python3.9 -m pip install poetry \
 && python3.9 -m poetry config virtualenvs.create false \
 && python3.9 -m poetry install --without dev --no-root \
 && python3.9 -m poetry export -f requirements.txt --output requirements.txt --without-hashes

# run tests
COPY pmlogger.conf /app/
COPY pcp2json.conf /app/
COPY pcp_plugin.py /app/
COPY pcp_schema.py /app/
COPY test_pcp_plugin.py /app/

RUN mkdir /htmlcov
RUN python3.9 -m pip install coverage
RUN python3.9 -m coverage run test_pcp_plugin.py
RUN python3.9 -m coverage html -d /htmlcov --omit=/usr/local/*

# final image
FROM quay.io/centos/centos:stream8

RUN dnf -y module install python39 && dnf -y install python39 python39-pip && dnf -y install procps-ng pcp pcp-export-pcp2json sysstat #collectl

WORKDIR /app

COPY --from=poetry /app/requirements.txt /app/
COPY --from=poetry /htmlcov /htmlcov/
COPY LICENSE /app/
COPY README.md /app/
COPY pmlogger.conf /app/
COPY pcp2json.conf /app/
COPY pcp_plugin.py /app/
COPY pcp_schema.py /app/

RUN python3.9 -m pip install -r requirements.txt

ENTRYPOINT ["python3.9", "/app/pcp_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugin-pcp"
LABEL org.opencontainers.image.licenses="Apache-2.0+GPL-2.0-only"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Arcaflow Performance Copilot Plugin"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
