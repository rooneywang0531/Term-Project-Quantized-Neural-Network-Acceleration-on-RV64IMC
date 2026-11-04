FROM debian:bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git python3 ca-certificates device-tree-compiler \
    libboost-regex-dev libboost-system-dev libgmp10 libisl23 libmpc3 libmpfr6 libzstd1 zlib1g \
    && apt-get clean
COPY . /opt/xqmac
WORKDIR /opt/xqmac
RUN python3 scripts/install_toolchain.py && bash scripts/bootstrap_spike.sh
ENV SPIKE_SRC=/opt/xqmac/.deps/spike
ENV SPIKE_BUILD=/opt/xqmac/.deps/spike/build
ENV SPIKE_BIN=/opt/xqmac/.tools/bin/spike
ENV PATH=/opt/xqmac/.tools/cross/usr/bin:/opt/xqmac/.tools/bin:$PATH
WORKDIR /work
CMD ["bash"]
