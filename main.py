#!/usr/bin/env python3
"""
ARNES FSOCIETY - Main Entry Point
Sistema de Ciberguerra Estatal - Red Team Automation
"""

import argparse
import asyncio
import sys
from pathlib import Path

from arnes_fsociety import create_arnes


def main():
    parser = argparse.ArgumentParser(
        description="ARNES FSOCIETY - Sistema de Ciberguerra Estatal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Ejecutar una mision de reconocimiento
  python main.py --mission "Realizar reconocimiento completo de target.com"
  
  # Ejecutar con sandbox habilitado
  python main.py --mission "Explotar vulnerabilidad en 192.168.1.100" --sandbox
  
  # Ejecutar mision async
  python main.py --mission "OSINT sobre organizacion ACME" --async
  
  # Listar subagentes disponibles
  python main.py --list-agents
        """,
    )
    
    parser.add_argument(
        "--mission",
        type=str,
        help="Descripcion de la mision a ejecutar",
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="fsociety",
        help="Modelo LLM a usar (default: fsociety)",
    )
    
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Habilitar Docker sandbox para ejecucion de payloads",
    )
    
    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="Deshabilitar sandbox (modo solo texto)",
    )
    
    parser.add_argument(
        "--async",
        dest="async_mode",
        action="store_true",
        help="Ejecutar mision en modo async",
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="Directorio de salida para resultados (default: ./output)",
    )
    
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="Listar subagentes disponibles",
    )
    
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="Listar skills disponibles",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verbose con logging detallado",
    )
    
    args = parser.parse_args()
    
    if args.list_agents:
        print("\n=== SUBAGENTES DISPONIBLES ===\n")
        agents = [
            ("recon", "Reconocimiento y Enumeracion", "Nmap, DNS, Fingerprinting"),
            ("exploit", "Explotacion de Vulnerabilidades", "SQLMap, Metasploit, Nuclei"),
            ("osint", "Inteligencia de Fuentes Abiertas", "OSINT, Brechas, Geolocalizacion"),
            ("post_exploit", "Post-Explotacion", "Escalada, Persistencia, Lateral Movement"),
            ("cyber_warfare", "Ciberguerra y Guerra Hibrida", "APT, Campañas, PSYOPS"),
        ]
        
        for name, desc, tools in agents:
            print(f"  [{name}]")
            print(f"    Descripcion: {desc}")
            print(f"    Herramientas: {tools}")
            print()
        
        return
    
    if args.list_skills:
        print("\n=== SKILLS DISPONIBLES ===\n")
        skills_dir = Path("./skills")
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        print(f"  - {skill_dir.name}")
        else:
            print("  No hay skills instaladas")
        print()
        return
    
    if not args.mission:
        parser.print_help()
        sys.exit(1)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    project_root = Path(__file__).parent.resolve()
    sandbox_enabled = args.sandbox and not args.no_sandbox
    
    print("\n" + "=" * 60)
    print("  ARNES FSOCIETY - Sistema de Ciberguerra Estatal")
    print("=" * 60)
    print(f"  Modelo: {args.model}")
    print(f"  Sandbox: {'Habilitado' if sandbox_enabled else 'Deshabilitado'}")
    print(f"  Output: {output_dir}")
    print(f"  Project Root: {project_root}")
    print("=" * 60 + "\n")
    
    try:
        arnes = create_arnes(
            model_name=args.model,
            sandbox_enabled=sandbox_enabled,
            project_root=project_root,
            mcp_servers=[
                {"type": "nmap"},
                {"type": "sqlmap"},
                {"type": "nuclei"},
                {"type": "metasploit"},
            ],
        )
        
        print(f"[+] Mision: {args.mission}\n")
        
        if args.async_mode:
            result = asyncio.run(arnes.run_async(args.mission))
        else:
            result = arnes.run(args.mission)
        
        result_file = output_dir / "mission_result.json"
        import json
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("  MISION COMPLETADA")
        print("=" * 60)
        print(f"  Estado: {result.get('status', 'unknown')}")
        print(f"  Resultado guardado en: {result_file}")
        print("=" * 60 + "\n")
        
        arnes.cleanup()
    
    except KeyboardInterrupt:
        print("\n\n[!] Operacion cancelada por el usuario")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
