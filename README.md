# DHL eCommerce NL for Home Assistant

Unofficial Home Assistant integration for **DHL eCommerce NL** (formerly DHL Parcel).
This integration tracks your incoming and delivered packages.

## Installation via HACS

1. Go to HACS -> Integrations.
2. Click the 3 dots (top right) -> **Custom repositories**.
3. Add URL: `https://github.com/rononline/dhl-ecommerce-nl`
4. Type: `Integration`.
5. Click **Add** and then **Download**.
6. Restart Home Assistant.

## Configuration

1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration**.
3. Search for **DHL eCommerce NL**.
4. Enter your DHL email and password.
   * You can add multiple accounts by adding the integration again.

## Dashboard Card (Lovelace)

Requires [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) and [lovelace-template-entity-row](https://github.com/thomasloven/lovelace-template-entity-row).

```yaml
type: custom:auto-entities
card:
  type: entities
  title: DHL Packages
filter:
  template: >
    {% set dhl_sensors = states.sensor | selectattr('entity_id', 'search', 'dhl_packages_') | list %}
    {% set ns = namespace(rows=[]) %}
    
    {% for sensor in dhl_sensors %}
      {% set packages = state_attr(sensor.entity_id, 'parcels_json') or [] %}
      {% for package in packages %}
        {% set name = package.sender.name if package.sender.name else 'Unknown Sender' %}
        {% set status = package.status | replace('_', ' ') | capitalize %}
        
        {% set row = {
          'type': 'custom:template-entity-row',
          'entity': sensor.entity_id,
          'name': name,
          'secondary': status ~ ' (' ~ package.barcode ~ ')',
          'state': '',
          'icon': 'mdi:package-variant-closed'
        } %}
        {% set ns.rows = ns.rows + [row] %}
      {% endfor %}
    {% endfor %}
    
    {{ ns.rows }}
