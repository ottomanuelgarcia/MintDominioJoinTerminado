# MintDominioJoinTerminado

Aplicación para unir equipos Linux Mint a un dominio Active Directory de forma guiada.

## Características

- Interfaz gráfica en GTK3 para facilitar la incorporación al dominio.
- Búsqueda de dominios basada en `realm` y fallback por DNS/local search domains.
- Integración con `realmd`, `sssd`, `adcli`, `krb5` y `pam-auth-update`.
- Opción para otorgar permisos sudo a los administradores del dominio.

## Requisitos

Antes de instalar el paquete `.deb`, asegúrate de tener acceso a la red del dominio y permisos de administrador.

Dependencias recomendadas:

- `python3`
- `python3-gi`
- `gir1.2-gtk-3.0`
- `realmd`
- `sssd`
- `sssd-tools`
- `libnss-sss`
- `libpam-sss`
- `adcli`
- `samba-common-bin`
- `krb5-user`
- `packagekit`
- `policykit-1`

## Instalación

1. Construye el paquete:

   ```bash
   bash build_package.sh
   ```

2. Instálalo:

   ```bash
   sudo dpkg -i domainjoinmint-1.0.deb
   ```

3. Ejecuta la aplicación:

   ```bash
   domainjoinmint
   ```

## Uso

1. Abre la aplicación.
2. Introduce el dominio o úsala para que intente detectarlo automáticamente.
3. Proporciona usuario y contraseña con permisos para unirse al dominio.
4. Confirma y reinicia el equipo si el proceso termina correctamente.

## Estructura del proyecto

- `DEBIAN/` - metadatos del paquete Debian.
- `usr/share/domainjoinmint/` - lógica principal y recursos de la app.
- `po/` - archivos de traducción.
- `tests/` - pruebas básicas del fallback de descubrimiento.

## Desarrollo

Para ejecutar las pruebas:

```bash
python3 -m unittest -v tests/test_domain_discovery.py
```

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE).
