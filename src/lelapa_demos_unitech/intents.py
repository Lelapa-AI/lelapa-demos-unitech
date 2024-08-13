import re
from typing import Dict, Tuple

INTENTS: Dict[str, Dict[str, Tuple[str, str]]] = {
    # Customer Questions
    "get_prepayment_electricity": {
        "patterns": [
            r"how.*get prepayment electricity",
            r"obtain prepaid electricity",
            r"purchase prepaid power",
        ],
        "responses": (
            "To get prepayment electricity, visit your nearest Eskom customer service center or authorized vendor. You can also use online platforms or mobile apps to purchase prepaid electricity tokens.",
            "Ukuthola ugesi ophelelwa isikhathi, vakashela isikhungo sezinsiza zamakhasimende sase-Eskom esiseduze nawe noma umthengisi ogunyaziwe. Ungaphinda usebenzise amaplatformu e-inthanethi noma ama-app eselula ukuthenga amathokeni kagesi aphelelwa isikhathi."
        )
    },
    "own_prepayment_meter": {
        "patterns": [
            r"want.*own prepayment meter",
            r"install prepaid meter",
            r"get.*prepaid meter",
        ],
        "responses": (
            "To get your own prepayment meter, contact Eskom customer service. They will guide you through the process, which may include a site inspection and installation fee.",
            "Ukuthola imitha yakho yokukhokha ngaphambili, xhumana nezinsiza zamakhasimende zase-Eskom. Bazokuhola enqubweni, okungahlanganisa ukuhlolwa kwendawo kanye nenkokhelo yokufakwa."
        )
    },
    "save_money_prepayment": {
        "patterns": [
            r"save money.*prepayment",
            r"prepaid electricity cheaper",
            r"cost savings.*prepaid",
        ],
        "responses": (
            "Prepayment electricity can help you save money by allowing better control over your electricity usage. You can monitor your consumption in real-time and adjust accordingly.",
            "Ugesi ophelelwa isikhathi ungakusiza ukonga imali ngokukuvumela ukuthi ulawule kangcono ukusetshenziswa kukagesi. Ungaqapha ukusetshenziswa kwakho ngesikhathi sangempela futhi ulungise ngokufanele."
        )
    },
    "electricity_source": {
        "patterns": [
            r"where.*get.*electricity",
            r"source of electricity",
            r"electricity supplier",
        ],
        "responses": (
            "Eskom is the primary electricity supplier in South Africa. Depending on your location, you may get electricity directly from Eskom or through your local municipality.",
            "I-Eskom iyona ehlinzeka ngogesi omkhulu eNingizimu Afrika. Kuye ngendawo ohlala kuyo, ungathola ugesi ngqo ku-Eskom noma ngokusekelwa umasipala wakho wasekhaya."
        )
    },
    "meter_not_working": {
        "patterns": [
            r"meter.*not work",
            r"broken meter",
            r"faulty meter",
        ],
        "responses": (
            "If your meter is not working, please report it to Eskom customer service immediately. They will arrange for a technician to inspect and repair or replace the meter if necessary.",
            "Uma imitha yakho ingasebenzi, sicela ubike ku-Eskom customer service ngokushesha. Bazolungiselela ukuthi uchwepheshe ahlole futhi alungise noma ashintshe imitha uma kunesidingo."
        )
    },
    "about_electricity": {
        "patterns": [
            r"tell.*more about electricity",
            r"electricity information",
            r"learn about electricity",
        ],
        "responses": (
            "Electricity is a form of energy resulting from the existence of charged particles. Eskom generates, transmits, and distributes electricity throughout South Africa using various methods including coal-fired, nuclear, and renewable energy sources.",
            "Ugesi uhlobo lwamandla okudalwa ukuba khona kwezinhlayiya ezinemishini. I-Eskom ikhiqiza, idlulise, futhi isabalalise ugesi eNingizimu Afrika yonke isebenzisa izindlela ezahlukene ezihlanganisa ugesi okhiqizwa ngamalahle, ngenyukliya, kanye nemithombo yamandla avuselelekayo."
        )
    },

    # Vending Questions
    "sell_electricity_for_eskom": {
        "patterns": [
            r"sell electricity for Eskom",
            r"become.*vending agent",
            r"how to be electricity vendor",
        ],
        "responses": (
            "To become an Eskom electricity vending agent, you need to apply through Eskom's vending department. Requirements include having a suitable business premises, computer equipment, and meeting financial criteria. Contact Eskom for detailed information on the application process.",
            "Ukuze ube umuntu othengisa ugesi we-Eskom, kudingeka ufake isicelo ngomnyango wokuthengisa we-Eskom. Izidingo zihlanganisa ukuba nendawo yoshintsho ehlinzekiwe, izinsiza zekhompyutha, kanye nokuhlangabezana nezinkomba zezezimali. Xhumana ne-Eskom ukuze uthole ulwazi olunemininingwane ngenqubo yokufaka isicelo."
        )
    },
    "sell_online_vending_systems": {
        "patterns": [
            r"sell online vending systems",
            r"provide.*online electricity sales",
            r"offer digital vending platform",
        ],
        "responses": (
            "If you want to sell online vending systems to Eskom, you need to go through Eskom's procurement process. Your system must comply with Eskom's technical specifications and security requirements. Contact Eskom's procurement department for more information on becoming a registered supplier.",
            "Uma ufuna ukudayisela i-Eskom izinhlelo zokuthengisa ku-inthanethi, kudingeka udlule enqubweni yokuthenga ye-Eskom. Uhlelo lwakho kumele luhambisane nezincazelo zobuchwepheshe ze-Eskom kanye nezidingo zokuphepha. Xhumana nomnyango wokuthenga we-Eskom ukuze uthole ulwazi olwengeziwe ngokuba umhlinzeki obhalisiwe."
        )
    },
    "xmlvend_info": {
        "patterns": [
            r"what is XMLVend",
            r"explain XMLVend",
            r"XMLVend meaning",
        ],
        "responses": (
            "XMLVend is a standard protocol for prepayment vending systems. It allows for interoperability between different vending systems and meters, enabling more efficient and flexible electricity vending processes.",
            "I-XMLVend iyindlela ejwayelekile yezinhlelo zokuthenga ngaphambili. Ivumela ukusebenzisana phakathi kwezinhlelo zokuthengisa ezahlukene kanye namamitha, okwenza izinqubo zokuthengisa ugesi zibe ngcono futhi zikwazi ukushintshashintsha."
        )
    },
    "xmlvend_benefits": {
        "patterns": [
            r"why use XMLVend",
            r"benefits of XMLVend",
            r"advantages.*XMLVend",
        ],
        "responses": (
            "XMLVend is used because it provides a standardized communication protocol for prepayment systems. This allows for easier integration of different vending platforms, improved security, and more efficient management of prepaid electricity services.",
            "I-XMLVend isetshenziselwa ukunikeza indlela yokuxhumana ejwayelekile yezinhlelo zokukhokha ngaphambili. Lokhu kuvumela ukuhlanganiswa okula kwamaplatformu okuthengisa ahlukene, ukuphepha okuthuthukisiwe, kanye nokuphathwa okusebenza kangcono kwezinsiza zikagesi ezikhokhelwa ngaphambili."
        )
    },
    "new_electricity_sales_method": {
        "patterns": [
            r"new way to sell electricity",
            r"innovative electricity vending",
            r"novel.*electricity sales",
        ],
        "responses": (
            "Eskom is always interested in innovative ways to improve electricity vending. If you have a new method, you can submit a proposal to Eskom's innovation department. They will evaluate its feasibility, security, and potential benefits before considering implementation.",
            "I-Eskom ihlale inentshisekelo ezindleleni ezintsha zokuthuthukisa ukuthengiswa kukagesi. Uma unendlela entsha, ungahambisa isiphakamiso kumnyango wezokusungula we-Eskom. Bazokubheka ukuthi kungenzeka yini, ukuphepha, kanye nezinzuzo ezingaba khona ngaphambi kokucabanga ukuyisebenzisa."
        )
    },

    # Meter Manufacturer Questions
    "meter_manufacturer_qualification": {
        "patterns": [
            r"qualify.*sell prepaid meters",
            r"become prepaid meter supplier",
            r"requirements.*prepaid meter vendor",
        ],
        "responses": (
            "To qualify to sell prepaid meters to Eskom, manufacturers need to meet specific technical standards and undergo a rigorous approval process. Contact Eskom's procurement department for detailed requirements and application procedures.",
            "Ukuze ufaneleke ukudayisela i-Eskom amamitha akhokhelwa ngaphambili, abakhiqizi kumele bahlangabezane namazinga ezobuchwepheshe athile futhi badlule enqubweni yokugunyazwa eqinile. Xhumana nomnyango wokuthenga we-Eskom ukuze uthole izidingo ezinemininingwane kanye nezinqubo zokufaka isicelo."
        )
    },
    "prepaid_meters_installed": {
        "patterns": [
            r"how many prepaid meters.*installed",
            r"number of prepayment meters",
            r"prepaid meter installation stats",
        ],
        "responses": (
            "The number of prepaid meters installed by Eskom changes regularly. For the most up-to-date information on prepaid meter installations, please contact Eskom's customer service or check their latest annual report.",
            "Inani lamamitha akhokhelwa ngaphambili afakwe yi-Eskom liyashintsha njalo. Ukuze uthole ulwazi lwakamuva ngokufakwa kwamamitha akhokhelwa ngaphambili, sicela uxhumane nezinsiza zamakhasimende ze-Eskom noma ubheke umbiko wabo wonyaka wakamuva."
        )
    },
    "prepayment_meters_reliability": {
        "patterns": [
            r"prepaid meter reliability",
            r"failure rate.*prepayment meters",
            r"how reliable.*prepaid meters",
        ],
        "responses": (
            "Eskom's prepaid meters are designed to be highly reliable. Specific failure rates and reliability statistics are regularly updated. For the most current information on prepaid meter reliability, please contact Eskom's technical support team.",
            "Amamitha akhokhelwa ngaphambili e-Eskom enzelwe ukuba athembekile kakhulu. Amazinga okwehluleka athile kanye namanani okuthembeka abuyekezwa njalo. Ukuze uthole ulwazi lwakamuva ngokuthembeka kwemitha ekhokhelwa ngaphambili, sicela uxhumane nethimba losizo lobuchwepheshe le-Eskom."
        )
    },
    "prepayment_meters_purpose": {
        "patterns": [
            r"why.*prepayment meters installed",
            r"purpose of prepaid meters",
            r"reason for using prepayment",
        ],
        "responses": (
            "Prepayment meters were installed to improve revenue collection, reduce operational costs, and give customers better control over their electricity consumption. They also help in managing electricity demand and reducing non-technical losses.",
            "Amamitha akhokhelwa ngaphambili afakwa ukuze kuthuthukiswe ukuqoqwa kwemali engenayo, kuncishiswe izindleko zokusebenza, futhi kunikwe amakhasimende ukulawula okungcono kokusetshenziswa kukagesi. Aphinda asize ekulawuleni isidingo sikagesi nasekunciphiseni ukulahleka okungekho kobuchwepheshe."
        )
    },
    "prepayment_decision": {
        "patterns": [
            r"how.*prepayment decision made",
            r"why choose prepaid electricity",
            r"decision process.*prepayment",
        ],
        "responses": (
            "The decision to implement prepayment metering was made after extensive research and pilot projects. Factors considered included improved revenue collection, reduced operational costs, better demand management, and customer empowerment in controlling their electricity usage.",
            "Isinqumo sokusebenzisa ukukala ngaphambili senziwa ngemuva kocwaningo olubanzi kanye namaphrojekthi okuhlola. Izinto ezabhekwa zahlanganisa ukuthuthukiswa kokuqoqwa kwemali engenayo, ukuncishiswa kwezindleko zokusebenza, ukuphathwa kangcono kwesidingo, kanye nokunikwa amandla kwamakhasimende ekulawuleni ukusetshenziswa kwabo kukagesi."
        )
    },
    "customer_reaction_prepayment": {
        "patterns": [
            r"customer reaction.*prepayment",
            r"how.*customers feel.*prepaid",
            r"public opinion.*prepaid meters",
        ],
        "responses": (
            "Customer reactions to prepayment meters have been mixed. Many appreciate the control over consumption and budgeting, while some have concerns about access and convenience. Eskom continuously works to address customer feedback and improve the prepayment system.",
            "Izimpendulo zamakhasimende kuma-mitha okukhokha ngaphambili zixubile. Abaningi bayakuthokozela ukulawula ukusetshenziswa nokwaba ibhajethi, kanti abanye banokukhathazeka ngokufinyeleleka nokusebenziseka. I-Eskom isebenza ngokungaphezi ukubhekana nempendulo yamakhasimende nokuthuthukisa uhlelo lokukhokha ngaphambili."
        )
    },
    "prepayment_theft_solution": {
        "patterns": [
            r"prepayment solve.*theft",
            r"electricity theft.*prepaid",
            r"prevent.*theft.*prepayment",
        ],
        "responses": (
            "Prepayment metering has helped reduce electricity theft by making it more difficult to use electricity without paying. However, it's not a complete solution, and Eskom continues to implement additional measures to combat electricity theft.",
            "Ukukala ngaphambili kusizile ekunciphiseni ukwebiwa kukagesi ngokwenza kube nzima ukusebenzisa ugesi ngaphandle kokukhokha. Kodwa-ke, akusiyona isisombululo esiphelele, futhi i-Eskom iqhubeka nokusebenzisa izinyathelo ezengeziwe ukulwa nokwebiwa kukagesi."
        )
    },

    # # Technical Questions
    # "technical_terms_explanation": {
    #     "patterns": [
    #         r"what.*words and acronyms mean",
    #         r"explain.*technical terms",
    #         r"definition of.*electricity jargon",
    #     ],
    #     "responses": (
    #         "Eskom uses various technical terms and acron
}