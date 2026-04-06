"""
Alloy definitions, conversion geometry, and default minor-element prices.
"""
import math

ALLOYS = {
    'AA2040': {
        'name': 'AA 2040', 'spec': 'AMS 4345',
        'desc': 'Al-5.0Cu-0.8Mg-0.6Mn-0.5Ag-0.12Zr',
        'app': 'Forgings (high-strength, elevated temp)',
        'comp': {
            'Al': 92.73, 'Cu': 5.00, 'Ag': 0.45, 'Mg': 0.80,
            'Mn': 0.60, 'Zr': 0.12, 'Ti': 0.05, 'Zn': 0.05,
            'Li': 0, 'Ni': 0, 'Fe': 0.10, 'Si': 0.10,
        },
    },
    'AA2050': {
        'name': 'AA 2050', 'spec': 'AMS 4413',
        'desc': 'Al-3.5Cu-1.0Li-0.45Ag-0.40Mg-0.35Mn-0.12Zr',
        'app': 'Thick plate (wing structures, space)',
        'comp': {
            'Al': 93.88, 'Cu': 3.50, 'Ag': 0.45, 'Li': 1.00,
            'Mg': 0.40, 'Mn': 0.35, 'Zr': 0.12, 'Ti': 0.05,
            'Zn': 0.05, 'Ni': 0, 'Fe': 0, 'Si': 0,
        },
    },
    'AA2099': {
        'name': 'AA 2099', 'spec': 'AMS 4287',
        'desc': 'Al-2.7Cu-1.8Li-0.7Zn-0.3Mg-0.3Mn-0.09Zr',
        'app': 'Extrusions (fuselage, stringers)',
        'comp': {
            'Al': 93.81, 'Cu': 2.70, 'Li': 1.80, 'Zn': 0.70,
            'Mg': 0.30, 'Mn': 0.30, 'Zr': 0.09, 'Ti': 0.05,
            'Ag': 0, 'Ni': 0, 'Fe': 0.04, 'Si': 0.025,
        },
    },
    'AA2618': {
        'name': 'AA 2618', 'spec': 'AMS 4132',
        'desc': 'Al-2.3Cu-1.6Mg-1.1Fe-1.0Ni-0.18Si',
        'app': 'Engine forgings, pistons (high temp)',
        'comp': {
            'Al': 93.72, 'Cu': 2.30, 'Mg': 1.60, 'Fe': 1.10,
            'Ni': 1.00, 'Si': 0.18, 'Ti': 0.07,
            'Zn': 0, 'Mn': 0, 'Zr': 0, 'Ag': 0, 'Li': 0,
        },
    },
    'AA7140': {
        'name': 'AA 7140', 'spec': 'AMS 4408',
        'desc': 'Al-6.6Zn-2.0Mg-1.8Cu-0.10Zr',
        'app': 'Ultra-thick plate (structural)',
        'comp': {
            'Al': 89.35, 'Zn': 6.60, 'Mg': 2.00, 'Cu': 1.80,
            'Zr': 0.10, 'Ti': 0.05, 'Fe': 0.07, 'Si': 0.06,
            'Mn': 0, 'Ag': 0, 'Li': 0, 'Ni': 0,
        },
    },
}

D_CAST = 533; L_CAST = 5900; D_LATHED = 416; L_USABLE = 5284
VOL_CAST = math.pi / 4 * D_CAST**2 * L_CAST
VOL_USABLE = math.pi / 4 * D_LATHED**2 * L_USABLE
R_BILLET = VOL_CAST / VOL_USABLE
R_EXTRUSION = 1.3
R_TOTAL = R_BILLET * R_EXTRUSION

CONVERSION = {
    'd_cast': D_CAST, 'l_cast': L_CAST,
    'd_lathed': D_LATHED, 'l_usable': L_USABLE,
    'r_billet': R_BILLET, 'r_extrusion': R_EXTRUSION, 'r_total': R_TOTAL,
    'yield_billet': 1/R_BILLET, 'yield_extrusion': 1/R_EXTRUSION, 'yield_total': 1/R_TOTAL,
}

MINOR_ELEMENT_DEFAULTS = {
    'Mg': 2.40, 'Mn': 1.85, 'Ti': 7.00,
    'Zr': 35.00, 'Fe': 0.10, 'Si': 2.40, 'Li': 195.0,
}
