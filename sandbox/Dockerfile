FROM kalilinux/kali-rolling:latest

LABEL maintainer="FSOCIETY State Division"
LABEL description="Sandbox Kali Linux para operaciones de Red Team"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    nmap \
    sqlmap \
    nuclei \
    metasploit-framework \
    hydra \
    john \
    hashcat \
    aircrack-ng \
    burpsuite \
    gobuster \
    dirb \
    nikto \
    wfuzz \
    theharvester \
    masscan \
    crackmapexec \
    impacket-scripts \
    responder \
    evil-winrm \
    bloodhound \
    netexec \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    netcat-openbsd \
    socat \
    tcpdump \
    wireshark \
    john \
    hashcat \
    medusa \
    ncrack \
    recon-ng \
    sherlock \
    subfinder \
    amass \
    httpx \
    dnsx \
    naabu \
    katana \
    waybackurls \
    gau \
    ffuf \
    feroxbuster \
    rustscan \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
    pwntools \
    impacket \
    crackmapexec \
    bloodhound \
    certipy \
    lsassy \
    pypykatz \
    minikerberos \
    aiowmi

RUN mkdir -p /workspace /output /tools

WORKDIR /workspace

CMD ["/bin/bash"]
