"""
Alloy raw-material cost calculation engine.
"""

TROY_OZ_PER_KG = 1000.0 / 31.1035

def calc_alloy_cost(comp: dict, prices: dict) -> tuple[float, float, float]:
    cost = ag_cost = li_cost = 0.0
    for elem, wt_pct in comp.items():
        if wt_pct == 0:
            continue
        frac = wt_pct / 100.0
        if elem == 'Al':
            p = prices['Al'] / 1000.0
        elif elem in ('Cu', 'Zn', 'Ni'):
            p = prices[elem] / 1000.0
        elif elem == 'Ag':
            p = prices['Ag_oz'] * TROY_OZ_PER_KG
        elif elem in ('Mg', 'Mn', 'Ti', 'Zr', 'Li', 'Fe', 'Si'):
            p = prices[elem]
        else:
            continue
        elem_cost = p * frac
        cost += elem_cost
        if elem == 'Ag': ag_cost = elem_cost
        if elem == 'Li': li_cost = elem_cost
    return cost, ag_cost, li_cost

def calc_conversion_costs(raw_cost, r_billet, r_total):
    return raw_cost * r_billet, raw_cost * r_total
