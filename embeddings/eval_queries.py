from ranx import Qrels

GROUND_TRUTH = {
    # ─── AUTO-RESTART / EMERGENCY FUNCTION ───────────────────────────────────
    "q1": [
        {
            "relevance": 2,
            "doc_id": "01_p8",
            "query": "¿Cuáles son los pasos para desactivar la función AUTO-RESTART?",
        }
    ],
    "q2": [
        {
            "relevance": 2,
            "doc_id": "01_p8",
            "query": "¿Qué ocurre al presionar el botón de emergencia dos veces en menos de 3 segundos?",
        }
    ],
    "q3": [
        {
            "relevance": 2,
            "doc_id": "01_p8",
            "query": "¿Cuántos beeps emite la unidad al activar correctamente la función AUTO-RESTART?",
        }
    ],
    # ─── REMOTE CONTROLLER BUTTONS ───────────────────────────────────────────
    "q4": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "¿Qué función activa el botón HEALTHY en el control remoto?",
        }
    ],
    "q5": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "¿Qué temperatura y velocidad de ventilador activa el modo SUPER en refrigeración?",
        },
        {
            "relevance": 1,
            "doc_id": "02_p34",
            "query": "¿Qué temperatura y velocidad de ventilador activa el modo SUPER en refrigeración?",
        },
    ],
    "q6": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "¿Qué hace el botón ECO en modo calefacción?",
        },
        {
            "relevance": 1,
            "doc_id": "02_p34",
            "query": "¿Qué hace el botón ECO en modo calefacción?",
        },
    ],
    "q7": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "¿Qué sucede al presionar el botón 3D en el control remoto?",
        }
    ],
    # ─── TIMER MODE ──────────────────────────────────────────────────────────
    "q8": [
        {
            "relevance": 2,
            "doc_id": "01_p10",
            "query": "¿Cuáles son los pasos para programar el encendido automático (Timer ON)?",
        }
    ],
    # ─── FEEL / SLEEP MODES ──────────────────────────────────────────────────
    "q9": [
        {
            "relevance": 2,
            "doc_id": "01_p11",
            "query": "¿A qué temperatura ambiente el modo FEEL activa automáticamente el modo calefacción?",
        }
    ],
    "q10": [
        {
            "relevance": 2,
            "doc_id": "01_p17",
            "query": "¿Cuántos grados sube la temperatura de consigna en modo SLEEP durante las primeras 2 horas en refrigeración?",
        }
    ],
    "q11": [
        {
            "relevance": 2,
            "doc_id": "01_p17",
            "query": "¿Cuántas horas después de activar el modo SLEEP se apaga automáticamente el equipo?",
        }
    ],
    "q12": [
        {
            "relevance": 2,
            "doc_id": "01_p17",
            "query": "¿Cómo ajusta el modo SLEEP la temperatura en modo calefacción durante las primeras 2 horas?",
        }
    ],
    # ─── PROTECTION / CLIMATE CONDITIONS ─────────────────────────────────────
    "q13": [
        {
            "relevance": 2,
            "doc_id": "01_p18",
            "query": "¿Cuáles son los límites de temperatura exterior para el modo calefacción en equipos T1?",
        }
    ],
    "q14": [
        {
            "relevance": 2,
            "doc_id": "01_p18",
            "query": "¿Cuál es la temperatura exterior máxima para operar en modo refrigeración en equipos T3 (tropical)?",
        }
    ],
    "q15": [
        {
            "relevance": 2,
            "doc_id": "01_p18",
            "query": "¿A qué temperatura de habitación se activa la protección en modo calefacción T1?",
        }
    ],
    # ─── INSTALLATION — DISTANCES, TORQUES, PIPES ────────────────────────────
    "q16": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "¿Cuál es la distancia máxima permitida entre la unidad interior y la exterior?",
        },
        {
            "relevance": 1,
            "doc_id": "03_p5",
            "query": "¿Cuál es la distancia máxima permitida entre la unidad interior y la exterior?",
        },
    ],
    "q17": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "¿Cuál es la diferencia de nivel máxima entre la unidad interior y la exterior?",
        }
    ],
    "q18": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "¿Cuál es el torque de apriete para tubería de 1/4\" (6mm)?",
        },
        {
            "relevance": 1,
            "doc_id": "03_p12",
            "query": "¿Cuál es el torque de apriete para tubería de 1/4\" (6mm)?",
        },
    ],
    "q19": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "¿Cuánto refrigerante adicional (g/m) se debe añadir por metro en modelos de 15/18k BTU de velocidad fija?",
        }
    ],
    "q20": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "¿Cuál es la longitud de tubería incluida en la carga estándar de refrigerante para un modelo de 12k BTU?",
        }
    ],
    # ─── CABLE SPECIFICATIONS ────────────────────────────────────────────────
    "q21": [
        {
            "relevance": 2,
            "doc_id": "01_p27",
            "query": "¿Cuál es el calibre de cable de alimentación para un modelo de 22/24k BTU tipo inversor?",
        },
        {
            "relevance": 1,
            "doc_id": "03_p9",
            "query": "¿Cuál es el calibre de cable de alimentación para un modelo de 22/24k BTU tipo inversor?",
        },
    ],
    # ─── MAINTENANCE ────────────────────────────────────────────────────────
    "q22": [
        {
            "relevance": 2,
            "doc_id": "01_p28",
            "query": "¿Cada cuánto tiempo deben reemplazarse los filtros electrostáticos y desodorantes?",
        }
    ],
    "q23": [
        {
            "relevance": 2,
            "doc_id": "01_p28",
            "query": "¿Con qué temperatura máxima de agua se puede limpiar el filtro de polvo?",
        }
    ],
    # ─── ERROR CODES — 01.pdf ────────────────────────────────────────────────
    "q24": [
        {
            "relevance": 2,
            "doc_id": "01_p29",
            "query": "¿Cuántas veces parpadea el indicador RUN cuando falla el sensor de temperatura interior?",
        }
    ],
    "q25": [
        {
            "relevance": 2,
            "doc_id": "01_p29",
            "query": "¿Cuántas veces parpadea el indicador RUN cuando falla el motor del ventilador interior?",
        }
    ],
    # ─── FCAC DIMENSIONS & SPECS ─────────────────────────────────────────────
    "q26": [
        {
            "relevance": 2,
            "doc_id": "02_p7",
            "query": "¿Cuáles son las dimensiones A, B y C del modelo FCAC-36?",
        }
    ],
    "q27": [
        {
            "relevance": 2,
            "doc_id": "02_p7",
            "query": "¿Cuánto pesa el modelo FCAC-60 y cuáles son sus dimensiones de ancho y profundidad?",
        }
    ],
    # ─── FCAC ELECTRICAL CHARACTERISTICS ─────────────────────────────────────
    "q28": [
        {
            "relevance": 2,
            "doc_id": "02_p8",
            "query": "¿Cuál es el rango de voltaje de operación (mínimo y máximo) del modelo FCAC-60?",
        }
    ],
    # ─── FCAC SOUND LEVELS & WIRING ──────────────────────────────────────────
    "q29": [
        {
            "relevance": 2,
            "doc_id": "02_p9",
            "query": "¿Cuál es el nivel de ruido del modelo FCAC-24 en velocidad baja?",
        }
    ],
    "q30": [
        {
            "relevance": 2,
            "doc_id": "02_p9",
            "query": "¿Cuál es el nivel de ruido del modelo FCAC-36 en velocidad alta?",
        }
    ],
    "q31": [
        {
            "relevance": 2,
            "doc_id": "02_p9",
            "query": "¿Cuál es el tamaño del cable de alimentación del FCAC-36?",
        }
    ],
    # ─── ERROR CODES — 02.pdf ────────────────────────────────────────────────
    "q32": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "¿Qué significa el código de error E3 en la unidad FCAC?",
        }
    ],
    "q33": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "¿Qué indica el código de error E0 en la unidad FCAC?",
        }
    ],
    "q34": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "¿Qué significa el código F0 en la unidad FCAC?",
        }
    ],
    "q35": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "¿Qué indica el código F3 en el display de la unidad?",
        }
    ],
    # ─── VACUUM DRY PROCEDURE ────────────────────────────────────────────────
    "q36": [
        {
            "relevance": 2,
            "doc_id": "02_p19",
            "query": "¿Cuánto tiempo mínimo debe operar la bomba de vacío en el procedimiento de vacío común?",
        }
    ],
    "q37": [
        {
            "relevance": 2,
            "doc_id": "02_p19",
            "query": "¿Qué nivel mínimo de vacío en mmHg debe alcanzarse durante el secado?",
        }
    ],
    "q38": [
        {
            "relevance": 2,
            "doc_id": "02_p19",
            "query": "¿Cuánto tiempo se deja en reposo el sistema después del vacío para verificar que no hay fuga?",
        }
    ],
    # ─── WATER DRAINAGE ──────────────────────────────────────────────────────
    "q39": [
        {
            "relevance": 2,
            "doc_id": "02_p21",
            "query": "¿Cuál es la pendiente mínima que debe tener el tubo de drenaje?",
        }
    ],
    # ─── INSULATION ─────────────────────────────────────────────────────────
    "q40": [
        {
            "relevance": 2,
            "doc_id": "02_p24",
            "query": "¿Qué material de aislamiento se recomienda para la tubería de gas en equipos tipo bomba de calor?",
        }
    ],
    "q41": [
        {
            "relevance": 2,
            "doc_id": "02_p24",
            "query": "¿Cuál es la temperatura mínima que debe soportar el aislamiento del lado de alta presión?",
        }
    ],
    # ─── FCAC INSTALLATION — HANGING BOLTS ──────────────────────────────────
    "q42": [
        {
            "relevance": 2,
            "doc_id": "02_p27",
            "query": "¿Cuántos pernos colgantes M10 se requieren para la instalación del FCAC?",
        }
    ],
    # ─── FCAC REMOTE CONTROLLER — ECON / TURBO ──────────────────────────────
    "q43": [
        {
            "relevance": 2,
            "doc_id": "02_p34",
            "query": "¿A qué temperatura fija el modo ECON la consigna cuando se activa en modo refrigeración?",
        }
    ],
    "q44": [
        {
            "relevance": 2,
            "doc_id": "02_p34",
            "query": "¿El modo TURBO funciona cuando el equipo está en modo deshumidificación?",
        }
    ],
    # ─── DAIKIN FTXN — INSTALLATION SITE ────────────────────────────────────
    "q45": [
        {
            "relevance": 2,
            "doc_id": "03_p5",
            "query": "¿Cuál es la distancia mínima entre la unidad interior Daikin FTXN y el techo?",
        }
    ],
    "q46": [
        {
            "relevance": 2,
            "doc_id": "03_p3",
            "query": "¿Cuál es el alcance máximo del control remoto inalámbrico del Daikin FTXN?",
        }
    ],
    "q47": [
        {
            "relevance": 2,
            "doc_id": "03_p3",
            "query": "¿Cómo se configura el DIP switch para una unidad Daikin de solo refrigeración (cooling only)?",
        }
    ],
    # ─── DAIKIN FTXN — PIPING & WIRING ──────────────────────────────────────
    "q48": [
        {
            "relevance": 2,
            "doc_id": "03_p6",
            "query": "¿Qué diámetro debe tener el orificio en la pared para pasar la tubería del Daikin FTXN?",
        }
    ],
    "q49": [
        {
            "relevance": 2,
            "doc_id": "03_p9",
            "query": "¿Qué tipo de cable debe usarse para el cableado interunidad cuando la longitud supera los 10 metros en el Daikin FTXN?",
        },
        {
            "relevance": 1,
            "doc_id": "01_p27",
            "query": "¿Qué tipo de cable debe usarse para el cableado interunidad cuando la longitud supera los 10 metros en el Daikin FTXN?",
        },
    ],
    "q50": [
        {
            "relevance": 2,
            "doc_id": "03_p12",
            "query": "¿Cuál es el torque de apriete para las tuercas flare del lado del gas (3/8\") en el Daikin FTXN12KEVJU?",
        },
        {
            "relevance": 1,
            "doc_id": "01_p25",
            "query": "¿Cuál es el torque de apriete para las tuercas flare del lado del gas (3/8\") en el Daikin FTXN12KEVJU?",
        },
    ],
}

VISUAL_TRUTH = {
    "q51": [
        {
            "relevance": 2,
            "doc_id": "6b3043_p21",
            "query": "What is the refrigerant flow path in the freezing cycle, and what components does it pass through?"
        }
    ],
    "q52": [
        {
            "relevance": 2,
            "doc_id": "6b3043_p46",
            "query": "What components make up the SMPS source power circuit and what output voltages does it produce?"
        }
    ],
    "q53": [
        {
            "relevance": 2,
            "doc_id": "6b3043_p46",
            "query": "What is the oscillation frequency of the microprocessor clock circuit?"
        }
    ],
    "q54": [
        {
            "relevance": 2,
            "doc_id": "7f7b5d_p21",
            "query": "How are indoor units connected in a header joint configuration compared to a Y-joint configuration?"
        }
    ],
    "q55": [
        {
            "relevance": 2,
            "doc_id": "16fee4_p8",
            "query": "How should the assembly cable terminals be wired between the indoor and outdoor unit for the SH**YAA(B) model?"
        }
    ],
    "q56": [
        {
            "relevance": 2,
            "doc_id": "16fee4_p8",
            "query": "What is the terminal wiring configuration difference between the SH**YAA(B) model and the other models when connecting the assembly cable?"
        }
    ],
    "q57": [
        {
            "relevance": 2,
            "doc_id": "80a911_p16",
            "query": "What interior components and storage sections are visible in the refrigerator interior view diagram?"
        }
    ],
    "q58": [
        {
            "relevance": 2,
            "doc_id": "80a911_p16",
            "query": "Where is the Cool Select Pantry PLUS located inside the refrigerator?"
        }
    ],
    "q59": [
        {
            "relevance": 2,
            "doc_id": "80a911_p16",
            "query": "What storage components are available in the freezer section of the refrigerator?"
        }
    ],
    "q60": [
        {
            "relevance": 2,
            "doc_id": "80a911_p31",
            "query": "What are the steps to disassemble the refrigerator door, including how to disconnect the electrical connector and remove the water tube?"
        }
    ],
    "q61": [
        {
            "relevance": 2,
            "doc_id": "80a911_p31",
            "query": "How do you remove the water tube fitting from the refrigerator door hinge without damaging it?"
        }
    ],
    "q62": [
        {
            "relevance": 2,
            "doc_id": "90a2ab_p29",
            "query": "How do you safely remove the refrigerator door, including the correct angle to open it and how to handle the top hinge?"
        }
    ],
    "q63": [
        {
            "relevance": 2,
            "doc_id": "90a2ab_p29",
            "query": "What precautions must be taken when lifting the refrigerator door vertically to avoid injury or damage?"
        }
    ],
    "q64": [
        {
            "relevance": 2,
            "doc_id": "ac_mxad_p9",
            "query": "How is the ELB and MCCB connected to the indoor unit when using 1-phase vs 3-phase power supply?"
        }
    ],
    "q65": [
        {
            "relevance": 2,
            "doc_id": "ac_mxad_p9",
            "query": "How should the outdoor-to-indoor power cable, main power cable, and communication cable be connected to the terminal board using ELB?"
        }
    ],
    "q66": [
        {
            "relevance": 2,
            "doc_id": "ac_mxad_p12",
            "query": "How is the silence mode controller wired to the outdoor unit using the ASSY Control out and non-voltage contact for AC090/100/120/140MXAD*H?"
        }
    ],
    "q67": [
        {
            "relevance": 2,
            "doc_id": "ac_mxad_p12",
            "query": "How are the outdoor-to-indoor power cable, main power cable, and communication cable routed between the indoor and outdoor unit in a 1-phase installation?"
        }
    ],
    "q68": [
        {
            "relevance": 2,
            "doc_id": "ac_mxad_p12",
            "query": "In a 3-phase installation, how is the 4-wire main power cable (AC 380V) connected between the outdoor unit terminal board and the indoor unit?"
        }
    ],
    "q69": [
        {
            "relevance": 2,
            "doc_id": "de0bde_p93",
            "query": "What is the troubleshooting flowchart procedure when power is not applied to the unit?"
        }
    ],
    "q70": [
        {
            "relevance": 2,
            "doc_id": "de0bde_p93",
            "query": "If the SMPS delivers normal output voltages of 12V and 5V but power is still not applied, what is the next diagnostic step?"
        }
    ],
}

def get_qrels():
    truth = { **GROUND_TRUTH, **VISUAL_TRUTH }
    qrels = { id: { doc['doc_id']: doc['relevance'] for doc in docs } for id, docs in truth.items() }  
    return Qrels(qrels)

def get_queries():
    truth = { **GROUND_TRUTH, **VISUAL_TRUTH }
    return { id: docs[0]['query'] for id, docs in truth.items() }  
