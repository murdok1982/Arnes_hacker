---
name: nmap-recon
description: Escaneo de red con Nmap - Puertos, servicios, vulnerabilidades
version: 1.0.0
tags:
  - recon
  - nmap
  - scanning
author: FSOCIETY
---

# Skill: Nmap Reconnaissance

## Uso

Ejecuta escaneos de red con Nmap para enumerar puertos, servicios, y vulnerabilidades.

## Comandos Base

### Escaneo rapido de puertos comunes
```bash
nmap -sV -sC -T4 <target>
```

### Escaneo completo (todos los puertos)
```bash
nmap -sV -sC -p- -T4 <target>
```

### Escaneo de vulnerabilidades
```bash
nmap --script=vuln <target>
```

### Escaneo UDP
```bash
nmap -sU --top-ports 100 <target>
```

### Deteccion de OS
```bash
nmap -O <target>
```

### Escaneo agresivo (todo)
```bash
nmap -A -T4 <target>
```

## Scripts Nmap Utiles

### HTTP Enumeration
```bash
nmap --script=http-enum,http-robots.txt,http-sitemap-generator <target> -p 80,443
```

### SMB Enumeration
```bash
nmap --script=smb-enum-shares,smb-enum-users,smb-os-discovery <target> -p 445
```

### DNS Enumeration
```bash
nmap --script=dns-brute,dns-zone-transfer <target> -p 53
```

### SSL/TLS Analysis
```bash
nmap --script=ssl-enum-ciphers,ssl-cert,ssl-heartbleed <target> -p 443
```

## Output Format

Siempre usar `-oA <output_base>` para guardar en todos los formatos:
```bash
nmap -sV -sC -oA scan_results <target>
```

Esto genera:
- `scan_results.nmap` (formato texto)
- `scan_results.xml` (formato XML)
- `scan_results.gnmap` (formato grep)

## Stealth Mode

Para escaneos sigilosos:
```bash
nmap -sS -T2 -f --data-length 24 <target>
```

- `-sS`: SYN scan (no completa conexion)
- `-T2`: Timing lento
- `-f`: Fragmentar paquetes
- `--data-length`: Padding aleatorio

## WAF Evasion

```bash
nmap -sS -T2 --script=waf-detect <target>
```

Si detecta WAF, usar:
```bash
nmap -sS --script=waf-detect --script-args="waf-detect.detectBodyChanges" <target>
```
