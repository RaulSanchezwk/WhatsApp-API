DAYS_TO_SHOW = 5

BRANCHES = {
    1: {
        "BRANCH NAME": "CENTRO",
        "DOCTOR ID": 43692,
        "DOCTOR NAME": "DR. CESAR JASSO"
        },
    2: {
        "BRANCH NAME": "FUNDIDORA",
        "DOCTOR ID": 30496,
        "DOCTOR NAME": "DIANA SULEM GARCIA JUAREZ"
        },
    3: {
        "BRANCH NAME": "LA FE",
        "DOCTOR ID": 97668,
        "DOCTOR NAME": "CAROLINA SANCHEZ CASTILLO"
        },
    4: {
        "BRANCH NAME": "SAN NICOLÁS",
        "DOCTOR ID": 99674,
        "DOCTOR NAME": "RAUL IRAM PONCE"
        },
    5: {
        "BRANCH NAME": "LINCOLN",
        "DOCTOR ID": 158068,
        "DOCTOR NAME": "DULCE KARINA SANCHEZ"
        },
    6: {
        "BRANCH NAME": "SANTA CATARINA",
        "DOCTOR ID": 143837,
        "DOCTOR NAME": "DIANA LAURA GUERRA LOZANO"
        },
    7: {
        "BRANCH NAME": "GUADALUPE",
        "DOCTOR ID": 87303,
        "DOCTOR NAME": "GILBERTO"
        }
}

ALOUD_APPT_INTENTION_FIELDS = {"chosen_branch", "chosen_date", "chosen_hours_range", "chosen_hours"}

INITIAL_STEP = "sucursales"

NOT_VALID_OPTION = """
⚠️ Opción no válida.
Por favor, elige una opción válida del menú para poder continuar 😊
"""

ERROR_MESSAGE = """
🙏 Una disculpa, tuvimos un error en el sistema.
En breve, uno de nuestros agentes te atenderá.

¡Gracias por tu paciencia! 😊
"""