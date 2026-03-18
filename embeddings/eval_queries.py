from ranx import Qrels

GROUND_TRUTH = {
    # ─── AUTO-RESTART / EMERGENCY FUNCTION ───────────────────────────────────
    "q1": [
        {
            "relevance": 2,
            "doc_id": "01_p8",
            "query": "What are the steps to deactivate the AUTO-RESTART function?",
        }
    ],
    "q2": [
        {
            "relevance": 2,
            "doc_id": "01_p8",
            "query": "What happens when the emergency button is pressed twice within less than 3 seconds?",
        }
    ],
    "q3": [
        {
            "relevance": 2,
            "doc_id": "01_p8",
            "query": "How many beeps does the unit emit when the AUTO-RESTART function is correctly activated?",
        }
    ],
    # ─── REMOTE CONTROLLER BUTTONS ───────────────────────────────────────────
    "q4": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "What function does the HEALTHY button on the remote controller activate?",
        }
    ],
    "q5": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "What temperature and fan speed does SUPER mode activate in cooling?",
        },
        {
            "relevance": 1,
            "doc_id": "02_p34",
            "query": "What temperature and fan speed does SUPER mode activate in cooling?",
        },
    ],
    "q6": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "What does the ECO button do in heating mode?",
        },
        {
            "relevance": 1,
            "doc_id": "02_p34",
            "query": "What does the ECO button do in heating mode?",
        },
    ],
    "q7": [
        {
            "relevance": 2,
            "doc_id": "01_p9",
            "query": "What happens when the 3D button on the remote controller is pressed?",
        }
    ],
    # ─── TIMER MODE ──────────────────────────────────────────────────────────
    "q8": [
        {
            "relevance": 2,
            "doc_id": "01_p10",
            "query": "What are the steps to schedule an automatic power-on (Timer ON)?",
        }
    ],
    # ─── FEEL / SLEEP MODES ──────────────────────────────────────────────────
    "q9": [
        {
            "relevance": 2,
            "doc_id": "01_p11",
            "query": "At what ambient temperature does FEEL mode automatically activate heating mode?",
        }
    ],
    "q10": [
        {
            "relevance": 2,
            "doc_id": "01_p17",
            "query": "How many degrees does the set temperature rise in SLEEP mode during the first 2 hours in cooling?",
        }
    ],
    "q11": [
        {
            "relevance": 2,
            "doc_id": "01_p17",
            "query": "How many hours after activating SLEEP mode does the unit automatically turn off?",
        }
    ],
    "q12": [
        {
            "relevance": 2,
            "doc_id": "01_p17",
            "query": "How does SLEEP mode adjust the temperature in heating mode during the first 2 hours?",
        }
    ],
    # ─── PROTECTION / CLIMATE CONDITIONS ─────────────────────────────────────
    "q13": [
        {
            "relevance": 2,
            "doc_id": "01_p18",
            "query": "What are the outdoor temperature limits for heating mode in T1 units?",
        }
    ],
    "q14": [
        {
            "relevance": 2,
            "doc_id": "01_p18",
            "query": "What is the maximum outdoor temperature for operating in cooling mode in T3 (tropical) units?",
        }
    ],
    "q15": [
        {
            "relevance": 2,
            "doc_id": "01_p18",
            "query": "At what room temperature does the protection in T1 heating mode activate?",
        }
    ],
    # ─── INSTALLATION — DISTANCES, TORQUES, PIPES ────────────────────────────
    "q16": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "What is the maximum allowable distance between the indoor and outdoor unit?",
        },
        {
            "relevance": 1,
            "doc_id": "03_p5",
            "query": "What is the maximum allowable distance between the indoor and outdoor unit?",
        },
    ],
    "q17": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "What is the maximum level difference between the indoor and outdoor unit?",
        }
    ],
    "q18": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "What is the tightening torque for 1/4\" (6mm) piping?",
        },
        {
            "relevance": 1,
            "doc_id": "03_p12",
            "query": "What is the tightening torque for 1/4\" (6mm) piping?",
        },
    ],
    "q19": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "How much additional refrigerant (g/m) must be added per meter for fixed-speed 15/18k BTU models?",
        }
    ],
    "q20": [
        {
            "relevance": 2,
            "doc_id": "01_p25",
            "query": "What is the pipe length included in the standard refrigerant charge for a 12k BTU model?",
        }
    ],
    # ─── CABLE SPECIFICATIONS ────────────────────────────────────────────────
    "q21": [
        {
            "relevance": 2,
            "doc_id": "01_p27",
            "query": "What is the power cable gauge for a 22/24k BTU inverter-type model?",
        },
        {
            "relevance": 1,
            "doc_id": "03_p9",
            "query": "What is the power cable gauge for a 22/24k BTU inverter-type model?",
        },
    ],
    # ─── MAINTENANCE ────────────────────────────────────────────────────────
    "q22": [
        {
            "relevance": 2,
            "doc_id": "01_p28",
            "query": "How often should the electrostatic and deodorizing filters be replaced?",
        }
    ],
    "q23": [
        {
            "relevance": 2,
            "doc_id": "01_p28",
            "query": "What is the maximum water temperature for cleaning the dust filter?",
        }
    ],
    # ─── ERROR CODES — 01.pdf ────────────────────────────────────────────────
    "q24": [
        {
            "relevance": 2,
            "doc_id": "01_p29",
            "query": "How many times does the RUN indicator blink when the indoor temperature sensor fails?",
        }
    ],
    "q25": [
        {
            "relevance": 2,
            "doc_id": "01_p29",
            "query": "How many times does the RUN indicator blink when the indoor fan motor fails?",
        }
    ],
    # ─── FCAC DIMENSIONS & SPECS ─────────────────────────────────────────────
    "q26": [
        {
            "relevance": 2,
            "doc_id": "02_p7",
            "query": "What are the A, B, and C dimensions of the FCAC-36 model?",
        }
    ],
    "q27": [
        {
            "relevance": 2,
            "doc_id": "02_p7",
            "query": "How much does the FCAC-60 model weigh and what are its width and depth dimensions?",
        }
    ],
    # ─── FCAC ELECTRICAL CHARACTERISTICS ─────────────────────────────────────
    "q28": [
        {
            "relevance": 2,
            "doc_id": "02_p8",
            "query": "What is the operating voltage range (minimum and maximum) of the FCAC-60 model?",
        }
    ],
    # ─── FCAC SOUND LEVELS & WIRING ──────────────────────────────────────────
    "q29": [
        {
            "relevance": 2,
            "doc_id": "02_p9",
            "query": "What is the noise level of the FCAC-24 model at low speed?",
        }
    ],
    "q30": [
        {
            "relevance": 2,
            "doc_id": "02_p9",
            "query": "What is the noise level of the FCAC-36 model at high speed?",
        }
    ],
    "q31": [
        {
            "relevance": 2,
            "doc_id": "02_p9",
            "query": "What is the power cable size of the FCAC-36?",
        }
    ],
    # ─── ERROR CODES — 02.pdf ────────────────────────────────────────────────
    "q32": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "What does error code E3 mean on the FCAC unit?",
        }
    ],
    "q33": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "What does error code E0 indicate on the FCAC unit?",
        }
    ],
    "q34": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "What does code F0 mean on the FCAC unit?",
        }
    ],
    "q35": [
        {
            "relevance": 2,
            "doc_id": "02_p16",
            "query": "What does code F3 indicate on the unit display?",
        }
    ],
    # ─── VACUUM DRY PROCEDURE ────────────────────────────────────────────────
    "q36": [
        {
            "relevance": 2,
            "doc_id": "02_p19",
            "query": "What is the minimum time the vacuum pump must operate during the standard vacuum procedure?",
        }
    ],
    "q37": [
        {
            "relevance": 2,
            "doc_id": "02_p19",
            "query": "What is the minimum vacuum level in mmHg that must be reached during the drying process?",
        }
    ],
    "q38": [
        {
            "relevance": 2,
            "doc_id": "02_p19",
            "query": "How long is the system left at rest after the vacuum to verify there are no leaks?",
        }
    ],
    # ─── WATER DRAINAGE ──────────────────────────────────────────────────────
    "q39": [
        {
            "relevance": 2,
            "doc_id": "02_p21",
            "query": "What is the minimum slope the drain pipe must have?",
        }
    ],
    # ─── INSULATION ─────────────────────────────────────────────────────────
    "q40": [
        {
            "relevance": 2,
            "doc_id": "02_p24",
            "query": "What insulation material is recommended for the gas pipe in heat pump units?",
        }
    ],
    "q41": [
        {
            "relevance": 2,
            "doc_id": "02_p24",
            "query": "What is the minimum temperature the high-pressure side insulation must withstand?",
        }
    ],
    # ─── FCAC INSTALLATION — HANGING BOLTS ──────────────────────────────────
    "q42": [
        {
            "relevance": 2,
            "doc_id": "02_p27",
            "query": "How many M10 hanging bolts are required for the FCAC installation?",
        }
    ],
    # ─── FCAC REMOTE CONTROLLER — ECON / TURBO ──────────────────────────────
    "q43": [
        {
            "relevance": 2,
            "doc_id": "02_p34",
            "query": "At what fixed temperature does ECON mode set the setpoint when activated in cooling mode?",
        }
    ],
    "q44": [
        {
            "relevance": 2,
            "doc_id": "02_p34",
            "query": "Does TURBO mode work when the unit is in dehumidification mode?",
        }
    ],
    # ─── DAIKIN FTXN — INSTALLATION SITE ────────────────────────────────────
    "q45": [
        {
            "relevance": 2,
            "doc_id": "03_p5",
            "query": "What is the minimum clearance between the Daikin FTXN indoor unit and the ceiling?",
        }
    ],
    "q46": [
        {
            "relevance": 2,
            "doc_id": "03_p3",
            "query": "What is the maximum range of the Daikin FTXN wireless remote controller?",
        }
    ],
    "q47": [
        {
            "relevance": 2,
            "doc_id": "03_p3",
            "query": "How is the DIP switch configured for a Daikin cooling-only unit?",
        }
    ],
    # ─── DAIKIN FTXN — PIPING & WIRING ──────────────────────────────────────
    "q48": [
        {
            "relevance": 2,
            "doc_id": "03_p6",
            "query": "What diameter should the wall hole be for routing the Daikin FTXN piping?",
        }
    ],
    "q49": [
        {
            "relevance": 2,
            "doc_id": "03_p9",
            "query": "What type of cable must be used for inter-unit wiring when the length exceeds 10 meters in the Daikin FTXN?",
        },
        {
            "relevance": 1,
            "doc_id": "01_p27",
            "query": "What type of cable must be used for inter-unit wiring when the length exceeds 10 meters in the Daikin FTXN?",
        },
    ],
    "q50": [
        {
            "relevance": 2,
            "doc_id": "03_p12",
            "query": "What is the tightening torque for the gas-side flare nuts (3/8\") on the Daikin FTXN12KEVJU?",
        },
        {
            "relevance": 1,
            "doc_id": "01_p25",
            "query": "What is the tightening torque for the gas-side flare nuts (3/8\") on the Daikin FTXN12KEVJU?",
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

def get_truth(select: str ='all'):
    if select == 'all':
        return { **GROUND_TRUTH, **VISUAL_TRUTH }
    elif select == 'visual':
        return VISUAL_TRUTH
    elif select == 'text':
        return GROUND_TRUTH
    else:
        return { **GROUND_TRUTH, **VISUAL_TRUTH }


def get_qrels(select: str):
    truth = get_truth(select)
    # print("Total: ", len(truth))
    qrels = { id: { doc['doc_id']: doc['relevance'] for doc in docs } for id, docs in truth.items() }  
    return Qrels(qrels)

def get_queries(select: str):
    truth = get_truth(select)
    return { id: docs[0]['query'] for id, docs in truth.items() }  
