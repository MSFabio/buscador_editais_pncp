import json
import math

# Coordinates of Camaçari/BA
CAMACARI_COORDS = (-12.6975, -38.3242)

# Coordinates of Bahia Municipalities
MUNICIPALITY_COORDS = {
    "Camaçari": (-12.6975, -38.3242),
    "Dias d'Ávila": (-12.6181, -38.2961),
    "Lauro de Freitas": (-12.8944, -38.3272),
    "Simões Filho": (-12.7844, -38.4028),
    "Salvador": (-12.9714, -38.5014),
    "Mata de São João": (-12.5303, -38.3039),
    "Pojuca": (-12.4344, -38.3314),
    "Candeias": (-12.6681, -38.5444),
    "São Francisco do Conde": (-12.6264, -38.6806),
    "São Sebastião do Passé": (-12.5117, -38.4958),
    "Madre de Deus": (-12.7411, -38.6214),
    "Santo Amaro": (-12.5469, -38.7111),
    "São Félix": (-12.6058, -38.9722),
    "Cachoeira": (-12.5997, -38.9639),
    "Cabaceiras do Paraguaçu": (-12.6167, -39.1500),
    "Alagoinhas": (-12.1356, -38.4194),
    "Feira de Santana": (-12.2667, -38.9667),
    "Barrocas": (-11.5300, -39.0800),
    "Santa Terezinha": (-12.7722, -39.5242),
    "Santo Antônio de Jesus": (-12.9694, -39.2611),
    "Cruz das Almas": (-12.6731, -39.1022),
    "Jiquiriçá": (-13.2569, -39.5700),
    "Nova Itarana": (-13.1694, -39.9278),
    "Ibirapitanga": (-13.9572, -39.3800),
    "Ubaitaba": (-14.3122, -39.3242),
    "Itagibá": (-14.2831, -39.8458),
    "Ipiaú": (-14.1378, -39.7028),
    "Itajuípe": (-14.6781, -39.3758),
    "Itabuna": (-14.7858, -39.2800),
    "Ilhéus": (-14.7889, -39.0494),
    "Jequié": (-13.8581, -40.0842),
    "Lafaiete Coutinho": (-13.6558, -40.2100),
    "Ruy Barbosa": (-12.2858, -40.4939),
    "Itaberaba": (-12.5278, -40.3069),
    "Capim Grosso": (-11.3808, -40.0128),
    "Campo Formoso": (-10.5108, -40.3217),
    "Iguaí": (-14.7578, -40.0894),
    "Poções": (-14.5300, -40.3667),
    "Brumado": (-14.2039, -41.6653),
    "Rio do Antônio": (-14.4039, -41.7458),
    "Lagoa Real": (-14.1500, -42.2333),
    "Livramento de Nossa Senhora": (-13.6467, -41.8406),
    "Paramirim": (-13.4428, -42.2389),
    "Rio do Pires": (-13.1258, -42.2789),
    "Boquira": (-12.8228, -41.9700),
    "Ibipeba": (-11.6408, -42.0167),
    "Irecê": (-11.3039, -41.8558),
    "Gentio do Ouro": (-11.4339, -42.5039),
    "Xique-Xique": (-10.8231, -42.7311),
    "Juazeiro": (-9.4117, -40.5033),
    "Ibotirama": (-12.1853, -43.2206),
    "Barreiras": (-12.1528, -44.9961),
    "São Desidério": (-12.3639, -44.9733),
    "Luís Eduardo Magalhães": (-12.0967, -45.7967),
    "Riachão das Neves": (-11.7461, -44.9100),
    "Formosa do Rio Preto": (-11.0483, -45.1931),
    "Correntina": (-13.3433, -44.6367),
    "Cocos": (-14.1839, -44.5339),
    "Teixeira de Freitas": (-17.5367, -39.7422),
    "Vitória da Conquista": (-14.8661, -40.8394),
    "Santana": (-13.6067, -44.0500),
    "Curaçá": (-8.9903, -39.9094)
}

def haversine(coord1, coord2):
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    r = 6371.0 # Earth radius in kilometers
    return r * c

# Test with municipalities
with open(r'C:\Users\11429149760\.gemini\antigravity\scratch\aug18_bahia_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ba_items = data.get('bahia', [])

missing = set()
distances = {}

for item in ba_items:
    muni = item.get('municipio')
    if not muni:
        continue
    # Clean up name if needed
    muni_clean = muni.replace('', 'a') # fallback if encoding issue
    # match against keys
    matched_key = None
    for k in MUNICIPALITY_COORDS:
        if k.lower() in muni.lower() or muni.lower() in k.lower():
            matched_key = k
            break
    if matched_key:
        d = haversine(CAMACARI_COORDS, MUNICIPALITY_COORDS[matched_key])
        # Add road factor ~1.15 to 1.2 for realistic road distance or use geodesic directly
        distances[muni] = (round(d, 1), matched_key)
    else:
        missing.add(muni)

print("Found distances for:", len(distances), "municipalities")
print("Missing:", missing)
