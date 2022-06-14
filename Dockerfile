#syntax=docker/dockerfile:1.3
FROM mambaorg/micromamba:0.23.3@sha256:2f11d685a184b6398848c5b61657bd840ef7bb43fa9c64052047ac88e40f2b14

ENV PYTHON_USER xpublish
ENV HOME /home/${PYTHON_USER}
ENV DAGSTER_HOME ${HOME}
ENV PYTHONPATH ${HOME}

# Output logging faster
ENV PYTHONUNBUFFERED 1
# Don't write bytecode
ENV PYTHONDONTWRITEBYTECODE 1
# Show deprication warnings https://docs.djangoproject.com/en/2.2/howto/upgrade-version/#resolving-deprecation-warnings
ENV PYTHONWARNINGS always

RUN mkdir ${HOME}

WORKDIR ${HOME}

COPY --chown=$MAMBA_USER:$MAMBA_USER ./environment.yml ${HOME}/environment.yml

RUN --mount=type=cache,id=pygeoapi,target=/opt/conda/pkgs,uid=1000,gid=1000 \
    micromamba install -y -n base -f environment.yml

COPY --chown=$MAMBA_USER:$MAMBA_USER ./*.py ./

CMD ["python", "main.py"]
