FROM quay.io/centos/centos:stream8

RUN dnf -y module install python39 && dnf -y install python39 python39-pip && dnf -y install pcp pcp-export-pcp2json sysstat #collectl
RUN mkdir /app
RUN chmod 777 /app
ADD README.md /app
ADD poetry.lock /app
ADD pyproject.toml /app
ADD pcp_plugin.py /app
ADD pcp_schema.py /app
#ADD test_pcp_plugin.py /app
ADD pmlogger.conf /app
ADD pcp2json.conf /app
ADD https://raw.githubusercontent.com/arcalot/arcaflow-plugin-template-python/main/LICENSE /app
RUN chmod +x /app/pcp_plugin.py #/app/test_pcp_plugin.py
WORKDIR /app

RUN python3.9 -m pip install "poetry>=1.2.2,<1.3"
RUN python3.9 -m poetry --version
RUN python3.9 -m poetry config virtualenvs.create false
RUN python3.9 -m poetry install --without dev
#USER 1000

#RUN mkdir /htmlcov
#RUN pip3 install coverage
#RUN python3.9 -m coverage run test_example_plugin.py
#RUN python3.9 -m coverage html -d /htmlcov --omit=/usr/local/*


ENTRYPOINT ["/app/pcp_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugin-pcp"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Arcaflow Performance Copilot Plugin"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
