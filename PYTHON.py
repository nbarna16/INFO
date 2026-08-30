"""
Programozott halozatkonfiguracio - Netmiko alapu script
Feladat: HQ-CoreSW1 es HQ-CoreSW2 alap VLAN- es leiro-konfiguraciojanak
automatikus feltoltese SSH-n keresztul.

Telepites (ha meg nincs meg):
    pip install netmiko

Hasznalat:
    python network_config_automation.py
"""

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# --- Eszközlista: minden switch, amit a script sorban konfigural ---
DEVICES = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.10.2",       # HQ-CoreSW1 management IP
        "username": "admin",
        "password": "Admin123!",
        "secret": "Admin123!",         # enable jelszo (ha eltero, ide azt kell irni)
        "port": 22,
    },
    {
        "device_type": "cisco_ios",
        "host": "192.168.10.3",       # HQ-CoreSW2 management IP
        "username": "admin",
        "password": "Admin123!",
        "secret": "Admin123!",
        "port": 22,
    },
]

# --- A parancsok, amiket minden eszközre fel akarunk tolteni ---
# Pelda: uj VLAN letrehozasa nevvel, es egy leiro szoveg (description)
# hozzaadasa egy interfeszhez - ezt szabadon bovitheted barmilyen
# valos konfiguracios feladattal.
CONFIG_COMMANDS = [
    "vlan 60",
    "name GUEST",
    "exit",
    "interface range FastEthernet0/20-24",
    "switchport mode access",
    "switchport access vlan 60",
    "description Automatizalt konfiguracio - Python/Netmiko",
    "exit",
]


def configure_device(device: dict) -> None:
    """Csatlakozik egy eszkozhoz SSH-n, feltolti a konfiguraciot,
    majd elmenti a futo konfiguraciot a startup-configba."""
    host = device["host"]
    print(f"\n=== Csatlakozas: {host} ===")

    try:
        connection = ConnectHandler(**device)
        connection.enable()

        print(f"[{host}] Sikeres bejelentkezes, konfiguracio feltoltese...")
        output = connection.send_config_set(CONFIG_COMMANDS)
        print(output)

        print(f"[{host}] Konfiguracio mentese (write memory)...")
        save_output = connection.save_config()
        print(save_output)

        # Ellenorzeskent visszaolvassuk a VLAN-listat
        verify_output = connection.send_command("show vlan brief")
        print(f"[{host}] Aktualis VLAN-lista:\n{verify_output}")

        connection.disconnect()
        print(f"[{host}] Kesz, kapcsolat lezarva.")

    except NetmikoAuthenticationException:
        print(f"[{host}] HIBA: hibas felhasznalonev vagy jelszo.")
    except NetmikoTimeoutException:
        print(f"[{host}] HIBA: nem sikerult csatlakozni (idotullepes) - "
              f"ellenorizd az IP-cimet es hogy fut-e az SSH szolgaltatas.")
    except Exception as exc:  # noqa: BLE001 - vizsga/demo celra elegendo
        print(f"[{host}] HIBA: varatlan kivetel tortent: {exc}")


def main() -> None:
    print("Halozati eszkozok programozott konfiguracioja indul...")
    for device in DEVICES:
        configure_device(device)
    print("\nMinden eszkoz feldolgozva.")


if __name__ == "__main__":
    main()