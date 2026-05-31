FROM alpine:3.19

RUN apk add --no-cache curl bash

COPY scanner.sh /opt/discovery/scanner.sh
COPY wordlists/ /opt/discovery/wordlists/

RUN mkdir -p /opt/discovery/output

ENTRYPOINT ["/bin/bash", "/opt/discovery/scanner.sh"]
