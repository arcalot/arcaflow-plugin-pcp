# Package path for this plugin module relative to the repo root
ARG package=arcaflow_plugin_pcp

# PRE-STAGE -- Get collectl
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-osbase:0.2.0 as collectl

RUN dnf -y install git
RUN git clone https://github.com/sharkcz/collectl.git --branch 4.3.5 --single-branch

WORKDIR collectl
ENV DESTDIR /collectl-install
RUN ./INSTALL

# STAGE 1 -- Build module dependencies and run tests
# The 'poetry' and 'coverage' modules are installed and verson-controlled in the
# quay.io/arcalot/arcaflow-plugin-baseimage-python-buildbase image to limit drift
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-buildbase:0.2.0 as build
ARG package
RUN dnf -y install procps-ng pcp pcp-export-pcp2json sysstat perl

# An RPM dependency breaks this link from the arcaflow-plugin-baseimage-python-osbase image, so re-applying here
RUN ln -s /usr/bin/python3.9 /usr/bin/python

COPY poetry.lock /app/
COPY pyproject.toml /app/

# Convert the dependencies from poetry to a static requirements.txt file
RUN python -m poetry install --without dev --no-root \
 && python -m poetry export -f requirements.txt --output requirements.txt --without-hashes

COPY ${package}/ /app/${package}
COPY tests /app/${package}/tests
COPY --from=collectl /collectl-install/ //

ENV PYTHONPATH /app/${package}

WORKDIR /app/${package}

# Run tests and return coverage analysis
RUN python -m coverage run tests/test_${package}.py \
 && python -m coverage html -d /htmlcov --omit=/usr/local/*


# STAGE 2 -- Build final plugin image
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-osbase:0.2.0
ARG package
RUN dnf -y install procps-ng pcp pcp-export-pcp2json sysstat perl

# An RPM dependency breaks this link from the arcaflow-plugin-baseimage-python-osbase image, so re-applying here
RUN ln -s /usr/bin/python3.9 /usr/bin/python

COPY --from=build /app/requirements.txt /app/
COPY --from=build /htmlcov /htmlcov/
COPY --from=collectl /collectl-install/ //
COPY LICENSE /app/
COPY README.md /app/
COPY ${package}/ /app/${package}

RUN python -m pip install -r requirements.txt

WORKDIR /app/${package}

ENTRYPOINT ["python", "pcp_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugin-pcp"
LABEL org.opencontainers.image.licenses="Apache-2.0+GPL-2.0-only"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Arcaflow Performance Copilot Plugin"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
