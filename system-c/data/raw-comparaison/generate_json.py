#!/usr/bin/env python3
import json
import os

OUTPUT_DIR = "/tmp/opencode/system-c/data/raw-comparaison/taches"
os.makedirs(OUTPUT_DIR, exist_ok=True)

data = [
    {
        "cnp": "31301",
        "nom_metier": "Infirmières et infirmiers autorisés / infirmiers psychiatriques",
        "extraction_date": "2026-07-24",
        "sources": {
            "imt_en_ligne": {
                "url": "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/31301-infirmiers-infirmieres",
                "texte_brut": "Infirmiers / infirmières\n\nPlanifier et évaluer les soins à donner.\nÉvaluer la condition physique et mentale des patient(e)s.\nInformer les patient(e)s et leur famille sur certains aspects de santé.\nCollaborer avec des équipes interdisciplinaires de soins de santé.\nAdministrer les médicaments et les traitements prescrits.\nAjuster le plan thérapeutique infirmier.\nSurveiller, évaluer, documenter et consigner les symptômes et les changements dans l'état des patient(e)s.\nAssister les médecins lors des interventions chirurgicales et des procédures médicales.\nSuperviser, s'il y a lieu, d'autres membres du personnel.\nExécuter la démarche de renvoi des patient(e)s.\n\nInfirmiers / infirmières en santé du travail\n\nDévelopper des programmes d'éducation sur la santé pour le personnel.\nOffrir des soins infirmiers dans des entreprises et des industries privées.\n\nInfirmiers / infirmières en santé communautaire\n\nDonner des soins infirmiers et des renseignements sur la santé à domicile et dans des établissements de santé.\nParticiper à l'évaluation des besoins de collectivités et à l'élaboration de programmes.\nDépister des maladies et administrer des vaccins.\n\nInfirmiers / infirmières en psychiatrie\n\nProdiguer des soins infirmiers en contexte de santé mentale.\nFournir des services de counseling aux patient(e)s.\n\nConsultants / consultantes en soins infirmiers\n\nFournir des services de consultation relatifs à la profession d'infirmier(-ière) et aux sciences infirmières.\n\nChercheurs infirmiers / chercheuses infirmières en sciences infirmières\n\nFaire des recherches en sciences infirmières.\n\nInfirmiers cliniciens / infirmières cliniciennes\n\nÉvaluer l'état de santé des patient(e)s.\nAssurer la réalisation du plan de soins et de traitements infirmiers pour les personnes qui présentent des problèmes de santé complexes.\nProdiguer des soins et des traitements.",
                "extraction_reussie": True,
                "notes": ""
            },
            "guichet_emplois": {
                "url": "https://www.guichetemplois.gc.ca/rapportmarche/profession/993/QC",
                "texte_brut": "Tâches et fonctions\nVoici les tâches et activités principales que les Infirmiers autorisés/infirmières autorisées et infirmiers psychiatriques autorisés/infirmières psychiatriques autorisées doivent effectuer, et certaines des exigences physiques que celles-ci impliquent :\n\nLes infirmiers autorisés en soins généraux\névaluer les patients afin d'identifier les soins infirmiers appropriés;\ncollaborer avec les autres membres des équipes interdisciplinaires de soins de santé afin de planifier, d'implanter, de coordonner et d'évaluer les soins aux patients en consultation avec les patients et leurs familles;\nadministrer les médicaments et les traitements prescrits par un médecin ou selon les politiques et les protocoles en vigueur;\nsurveiller, évaluer, documenter et consigner les symptômes et les changements dans l'état des patients, et prendre des mesures nécessaires;\nutiliser du matériel ou des appareils médicaux ou en surveiller l'utilisation;\nassister les médecins dans les interventions chirurgicales et les autres procédures médicales;\nsuperviser, s'il y a lieu, les infirmiers auxiliaires autorisés et les autres membres du personnel infirmier;\nélaborer et mettre à exécution, s'il y a lieu, la démarche de planification de renvoi des patients lorsque ceux-ci sont admis en établissement;\ninformer et conseiller, au besoin, les patients et leurs familles sur certains aspects de la santé, en collaboration avec d'autres travailleurs dans le domaine de la santé.\n\nLes infirmiers en santé du travail\nélaborent et mettent en oeuvre des programmes d'éducation sur la santé pour les employés et dispensent des soins d'infirmiers autorisés dans des entreprises et industries privées.\n\nLes infirmiers en santé communautaire\ndonnent des renseignements sur la santé et des soins d'infirmiers autorisés dans des unités de santé publique et à domicile, ils gèrent les cas complexes de soins à domicile, prennent part à des évaluations des besoins de la collectivité et à l'élaboration de programmes, effectuent des tests de dépistage de maladies et assurent la prestation de programmes d'immunisation.\n\nLes infirmiers autorisés en psychiatrie\ndispensent des soins infirmiers et des services de counselling et donnent des cours de dynamique de la vie aux patients dans les hôpitaux psychiatriques, les cliniques de santé mentale, les établissements de soins de longue durée ainsi qu'au sein de la collectivité.\n\nLes chercheurs et les consultants en soins infirmiers\neffectuent des travaux de recherche liés aux sciences infirmières, en tant que travailleurs autonomes ou employés de centres hospitaliers, d'organismes privés et publics et du gouvernement;\nfournissent des services consultatifs à des établissements, à des associations et à des organisations de soins de santé sur les questions et les préoccupations relatives à la profession d'infirmier et à l'exercice en sciences infirmières.\n\nLes infirmiers cliniciens\nfournissent leadership, conseils et orientation en ce qui concerne la prestation de soins basés sur la recherche à des groupes précis de patients dont le soin relève d'organisations de soins de santé particulières.",
                "extraction_reussie": True,
                "notes": ""
            },
            "noc_oasis": {
                "url": "https://www23.statcan.gc.ca/imdb/p3VD_f.pl?Function=getVD&TVD=1322554&CVD=1322870&CPV=31301&CST=01052021&CLV=5&MLV=5",
                "texte_brut": "Fonctions principales\nCe groupe exerce une partie ou l'ensemble des fonctions suivantes :\n\nLes infirmiers autorisés en soins généraux\n\névaluer les patients afin d'identifier les soins infirmiers appropriés;\ncollaborer avec les autres membres des équipes interdisciplinaires de soins de santé afin de planifier, d'implanter, de coordonner et d'évaluer les soins aux patients en consultation avec les patients et leurs familles;\nadministrer les médicaments et les traitements prescrits par un médecin ou selon les politiques et les protocoles en vigueur;\nsurveiller, évaluer, documenter et consigner les symptômes et les changements dans l'état des patients, et prendre des mesures nécessaires;\nutiliser du matériel ou des appareils médicaux ou en surveiller l'utilisation;\nassister les médecins dans les interventions chirurgicales et les autres procédures médicales;\nsuperviser, s'il y a lieu, les infirmiers auxiliaires autorisés et les autres membres du personnel infirmier;\nélaborer et mettre à exécution, s'il y a lieu, la démarche de planification de renvoi des patients lorsque ceux-ci sont admis en établissement;\ninformer et conseiller, au besoin, les patients et leurs familles sur certains aspects de la santé, en collaboration avec d'autres travailleurs dans le domaine de la santé.\n\nLes infirmiers autorisés peuvent se spécialiser dans des domaines tels que la chirurgie, les soins obstétriques, les soins psychiatriques, les soins de phase aiguë, la pédiatrie, la gériatrie, la santé communautaire, la médecine du travail, les soins d'urgence, la réadaptation ou l'oncologie.\n\nLes infirmiers en santé du travail\n\nélaborent et mettent en oeuvre des programmes d'éducation sur la santé pour les employés et dispensent des soins d'infirmiers autorisés dans des entreprises et industries privées.\n\nLes infirmiers en santé communautaire\n\ndonnent des renseignements sur la santé et des soins d'infirmiers autorisés dans des unités de santé publique et à domicile, ils gèrent les cas complexes de soins à domicile, prennent part à des évaluations des besoins de la collectivité et à l'élaboration de programmes, effectuent des tests de dépistage de maladies et assurent la prestation de programmes d'immunisation.\n\nLes infirmiers autorisés en psychiatrie\n\ndispensent des soins infirmiers et des services de counseling et donnent des cours de dynamique de la vie aux patients dans les hôpitaux psychiatriques, les cliniques de santé mentale, les établissements de soins de longue durée ainsi qu'au sein de la collectivité.\n\nLes chercheurs et les consultants en soins infirmiers\n\neffectuent des travaux de recherche liés aux sciences infirmières, en tant que travailleurs autonomes ou employés de centres hospitaliers, d'organismes privés et publics et du gouvernement;\nfournissent des services consultatifs à des établissements, à des associations et à des organisations de soins de santé sur les questions et les préoccupations relatives à la profession d'infirmier et à l'exercice en sciences infirmières.\n\nLes infirmiers cliniciens\n\nfournissent leadership, conseils et orientation en ce qui concerne la prestation de soins basés sur la recherche à des groupes précis de patients dont le soin relève d'organisations de soins de santé particulières.",
                "extraction_reussie": True,
                "notes": "Page StatCan NOC 2021 utilisée car noc.esdc.gc.ca bloquait les requêtes webfetch"
            }
        }
    },
    {
        "cnp": "72300",
        "nom_metier": "Plombiers/plombières",
        "extraction_date": "2026-07-24",
        "sources": {
            "imt_en_ligne": {
                "url": "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/72300-plombiers-plombieres",
                "texte_brut": "Plombiers / plombières\n\nLire et interpréter des plans, des dessins et des spécifications techniques.\nDéterminer l'emplacement des raccords des tuyaux et des trous nécessaires à leur passage.\nFaire des ouvertures dans les murs et les planchers.\nMesurer, couper, plier et percer les tuyaux.\nJoindre les tuyaux avec des raccords ou du matériel de collage, de brasage ou de soudage.\nVérifier les tuyaux pour déceler les fuites.",
                "extraction_reussie": True,
                "notes": ""
            },
            "guichet_emplois": {
                "url": "https://www.guichetemplois.gc.ca/rapportmarche/profession/4747/QC",
                "texte_brut": "Tâches et fonctions\nVoici les tâches et activités principales que les Plombiers/plombières doivent effectuer, et certaines des exigences physiques que celles-ci impliquent :\n\nlire des plans, des dessins et des spécifications techniques afin de déterminer la disposition de la tuyauterie, du réseau d'alimentation en eau et des réseaux d'égout et d'évacuation des eaux;\ninstaller, réparer et entretenir des accessoires et des installations de tuyauterie dans des résidences et des bâtiments commerciaux et industriels;\ndéterminer et marquer l'emplacement des raccords des tuyaux, des trous pour le passage des tuyaux dans les murs et les planchers ainsi que les accessoires;\npratiquer, dans les murs et les planchers, des ouvertures de diamètre convenant aux tuyaux et aux accessoires de tuyauterie;\nmesurer, couper, plier et tarauder les tuyaux à l'aide de machines ou d'outils manuels ou mécaniques;\njoindre les tuyaux avec des raccords, des colliers de serrage, des vis, des boulons ou du matériel de collage, de brasage ou de soudage;\nvérifier les tuyaux à l'aide de manomètres pour déceler les fuites;\npréparer, s'il y a lieu, des devis.",
                "extraction_reussie": True,
                "notes": ""
            },
            "noc_oasis": {
                "url": "https://www23.statcan.gc.ca/imdb/p3VD_f.pl?Function=getVD&TVD=1322554&CVD=1322870&CPV=72300&CST=01052021&CLV=5&MLV=5",
                "texte_brut": "Fonctions principales\nCe groupe exerce une partie ou l'ensemble des fonctions suivantes :\n\nlire des plans, des dessins et des spécifications techniques afin de déterminer la disposition de la tuyauterie, du réseau d'alimentation en eau et des réseaux d'égout et d'évacuation des eaux;\ninstaller, réparer et entretenir des accessoires et des installations de tuyauterie dans des résidences et des bâtiments commerciaux et industriels;\ndéterminer et marquer l'emplacement des raccords des tuyaux, des trous pour le passage des tuyaux dans les murs et les planchers ainsi que les accessoires;\npratiquer, dans les murs et les planchers, des ouvertures de diamètre convenant aux tuyaux et aux accessoires de tuyauterie;\nmesurer, couper, plier et tarauder les tuyaux à l'aide de machines ou d'outils manuels ou mécaniques;\njoindre les tuyaux avec des raccords, des colliers de serrage, des vis, des boulons ou du matériel de collage, de brasage ou de soudage;\nvérifier les tuyaux à l'aide de manomètres pour déceler les fuites;\npréparer, s'il y a lieu, des devis.",
                "extraction_reussie": True,
                "notes": "Page StatCan NOC 2021 utilisée car noc.esdc.gc.ca bloquait les requêtes webfetch"
            }
        }
    },
    {
        "cnp": "21222",
        "nom_metier": "Spécialistes en informatique",
        "extraction_date": "2026-07-24",
        "sources": {
            "imt_en_ligne": {
                "url": "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/21222-specialistes-en-informatique",
                "texte_brut": "Spécialistes en informatique\n\nAnalystes et consultants / consultantes en informatique\n\nDéterminer et documenter les besoins informatiques des utilisateur(-trice)s.\nConcevoir, utiliser et maintenir des bases de données et des applications.\nFaire des recommandations sur des problèmes liés aux systèmes informatiques.\nOptimiser l'efficacité et la qualité des logiciels.\nAnalyser les couts de développement, d'utilisation et d'optimisation des systèmes.\nParticiper au développement, à la mise en place et à la réalisation de stratégies en matière informatique.\nConseiller les responsables de l'informatique au sein d'entreprises.\nPréparer des présentations et des rapports écrits basés sur la recherche, la collecte et l'analyse de données de plusieurs sources.\nConcevoir et optimiser des algorithmes.\n\nAnalystes en assurance de la qualité des systèmes informatiques\n\nOptimiser l'efficacité et la qualité des logiciels.\nConcevoir et mettre en oeuvre des procédures liées au cycle de vie des logiciels.\nConseiller les responsables de l'informatique au sein d'entreprises.\n\nVérificateurs / vérificatrices de systèmes\n\nEffectuer des révisions indépendantes pour évaluer les pratiques en assurance de la qualité, les produits logiciels et les systèmes d'information.",
                "extraction_reussie": True,
                "notes": ""
            },
            "guichet_emplois": {
                "url": "https://www.guichetemplois.gc.ca/rapportmarche/profession/22490/QC",
                "texte_brut": "Tâches et fonctions\nVoici les tâches et activités principales que les Spécialistes en informatique doivent effectuer, et certaines des exigences physiques que celles-ci impliquent :\n\nconcevoir, développer, tester, mettre en oeuvre et superviser les systèmes informatiques;\ncollecter et analyser les données pour identifier les domaines à améliorer au sein des infrastructures informatiques de l'organisation;\nexaminer les systèmes de technologies de l'information (TI) et les processus internes existants;\nconcevoir, mettre en oeuvre et appliquer les politiques et les procédures liées au cycle de vie des logiciels afin d'optimiser l'efficacité, le rendement et la qualité des logiciels et des systèmes d'information et de garantir que tous les systèmes et processus répondent aux normes de l'organisation et aux exigences des utilisateurs;\ndévelopper des procédures et des tests d'assurance qualité pour le développement et l'amélioration des systèmes existants et des nouveaux systèmes;\nidentifier, analyser et documenter les anomalies et assurer la réalisation des correctifs appropriés;\neffectuer des tâches d'entretien préventif sur les systèmes informatiques et les équipements périphériques.",
                "extraction_reussie": True,
                "notes": ""
            },
            "noc_oasis": {
                "url": "https://www23.statcan.gc.ca/imdb/p3VD_f.pl?Function=getVD&TVD=1322554&CVD=1322870&CPV=21222&CST=01052021&CLV=5&MLV=5",
                "texte_brut": "Fonctions principales\nCe groupe exerce une partie ou l'ensemble des fonctions suivantes :\n\nconcevoir, développer, tester, mettre en oeuvre et superviser les systèmes informatiques;\ncollecter et analyser les données pour identifier les domaines à améliorer au sein des infrastructures informatiques de l'organisation;\nexaminer les systèmes de technologies de l'information (TI) et les processus internes existants;\nconcevoir, mettre en oeuvre et appliquer les politiques et les procédures liées au cycle de vie des logiciels afin d'optimiser l'efficacité, le rendement et la qualité des logiciels et des systèmes d'information et de garantir que tous les systèmes et processus répondent aux normes de l'organisation et aux exigences des utilisateurs;\ndévelopper des procédures et des tests d'assurance qualité pour le développement et l'amélioration des systèmes existants et des nouveaux systèmes;\nidentifier, analyser et documenter les anomalies et assurer la réalisation des correctifs appropriés;\neffectuer des tâches d'entretien préventif sur les systèmes informatiques et les équipements périphériques.",
                "extraction_reussie": True,
                "notes": "Page StatCan NOC 2021 utilisée car noc.esdc.gc.ca bloquait les requêtes webfetch"
            }
        }
    },
    {
        "cnp": "64100",
        "nom_metier": "Vendeurs/vendeuses et décorateurs-étalagistes/décoratrices-étalagistes en commerce de détail",
        "extraction_date": "2026-07-24",
        "sources": {
            "imt_en_ligne": {
                "url": "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/64100-vendeurs-vendeuses-et-decorateurs-etalagistes-decoratrices-etalagistes-commerce-de-detail",
                "texte_brut": "Vendeurs / vendeuses et décorateurs-étalagistes / décoratrices-étalagistes - commerce de détail\n\nAccueillir la clientèle et gagner sa confiance.\nDiscuter des produits ou des services recherchés par la clientèle et lui en conseiller.\nRenseigner la clientèle sur l'utilisation et l'entretien des marchandises.\nDécrire les prix, les modalités de crédit et d'échange, les garanties et les dates de livraison.\nRédiger les contrats de vente ou de location.\nPréparer les marchandises et les présenter d'une manière attrayante.\nRecevoir les paiements et effectuer les transactions par voie électronique, s'il y a lieu.\nGérer la marchandise, les inventaires et les commandes de marchandises.\nAssurer le service après-vente.",
                "extraction_reussie": True,
                "notes": ""
            },
            "guichet_emplois": {
                "url": "https://www.guichetemplois.gc.ca/rapportmarche/profession/20599/QC",
                "texte_brut": "Tâches et fonctions\nVoici les tâches et activités principales que les Vendeurs/vendeuses et décorateurs-étalagistes/décoratrices-étalagistes en commerce de détail doivent effectuer, et certaines des exigences physiques que celles-ci impliquent :\n\nVendeurs\naccueillir les clients et discuter des caractéristiques, de la qualité et de la quantité des marchandises ou des services qu'ils désirent acheter ou louer;\nrenseigner les clients sur l'utilisation et l'entretien des marchandises, et les conseiller sur les produits ou services spécialisés;\nestimer ou indiquer des prix, préciser des modalités de crédit et d'échange, des garanties et des dates de livraison;\npréparer les marchandises à vendre ou à louer;\npréparer des contrats de vente ou de location, et accepter des paiements en espèces, par chèque, par carte de crédit ou par débit automatique;\naider à l'étalage des marchandises;\ntenir à jour des registres des ventes pour l'inventaire;\nse servir des systèmes informatisés de tenue d'inventaire et de commande de stocks;\neffectuer, au besoin, des transactions par le biais du commerce électronique.\n\nDécorateurs - étalagistes\nCréer et réalisent des décors, des vitrines et des présentoirs intérieurs;\nAssembler les présentoirs de vente pour promouvoir les produits, les événements promotionnels et les changements saisonniers;\nS'assurer que l'affichage visuel est conforme aux normes et directives de la marque, y compris la culture, l'image et les marchés cibles de l'entreprise;\nCréer et aménagent la luminosité des vitrines et étalages de manière à produire une atmosphère visuelle.",
                "extraction_reussie": True,
                "notes": ""
            },
            "noc_oasis": {
                "url": "https://www23.statcan.gc.ca/imdb/p3VD_f.pl?Function=getVD&TVD=1322554&CVD=1322870&CPV=64100&CST=01052021&CLV=5&MLV=5",
                "texte_brut": "Fonctions principales\nCe groupe exerce une partie ou l'ensemble des fonctions suivantes :\n\nVendeurs\n\naccueillir les clients et discuter des caractéristiques, de la qualité et de la quantité des marchandises ou des services qu'ils désirent acheter ou louer;\nrenseigner les clients sur l'utilisation et l'entretien des marchandises, et les conseiller sur les produits ou services spécialisés;\nestimer ou indiquer des prix, préciser des modalités de crédit et d'échange, des garanties et des dates de livraison;\npréparer les marchandises à vendre ou à louer;\npréparer des contrats de vente ou de location, et accepter des paiements en espèces, par chèque, par carte de crédit ou par débit automatique;\naider à l'étalage des marchandises;\ntenir à jour des registres des ventes pour l'inventaire;\nse servir des systèmes informatisés de tenue d'inventaire et de commande de stocks;\neffectuer, au besoin, des transactions par le biais du commerce électronique.\n\nDécorateurs - étalagistes\n\nCréer et réalisent des décors, des vitrines et des présentoirs intérieurs;\nAssembler les présentoirs de vente pour promouvoir les produits, les événements promotionnels et les changements saisonniers;\nS'assurer que l'affichage visuel est conforme aux normes et directives de la marque, y compris la culture, l'image et les marchés cibles de l'entreprise;\nCréer et aménagent la luminosité des vitrines et étalages de manière à produire une atmosphère visuelle.\n\nLes vendeurs - commerce de détail peuvent se spécialiser et agir à titre de conseiller en systèmes de divertissement au foyer, en informatique et dans d'autres gammes de produits et services.",
                "extraction_reussie": True,
                "notes": "Page StatCan NOC 2021 utilisée car noc.esdc.gc.ca bloquait les requêtes webfetch"
            }
        }
    },
    {
        "cnp": "12200",
        "nom_metier": "Techniciens/techniciennes en comptabilité et teneurs/teneuses de livres",
        "extraction_date": "2026-07-24",
        "sources": {
            "imt_en_ligne": {
                "url": "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/12200-techniciens-techniciennes-en-comptabilite-et-teneurs-teneuses-de-livres",
                "texte_brut": "Techniciens / techniciennes en comptabilité et teneurs / teneuses de livres\n\nTenir des registres financiers.\nOrganiser, tenir à jour et faire la balance de divers comptes.\nTenir des grands livres généraux, reporter des écritures au journal et faire concorder des comptes.\nPréparer les balances de vérification des comptes et des états financiers.\nFaire des calculs et préparer des chèques de paye et des factures.\nRemplir et soumettre des formulaires et des documents gouvernementaux (versement d'impôts, indemnisation des accidents du travail, prestations de retraite, etc.).\nPréparer des déclarations de revenus et fournir des services de tenue de livres pour des particuliers(-ière)s.\nPréparer des rapports statistiques, financiers et comptables.",
                "extraction_reussie": True,
                "notes": ""
            },
            "guichet_emplois": {
                "url": "https://www.guichetemplois.gc.ca/rapportmarche/profession/24500/QC",
                "texte_brut": "Tâches et fonctions\nVoici les tâches et activités principales que les Techniciens/techniciennes en comptabilité et teneurs/teneuses de livres doivent effectuer, et certaines des exigences physiques que celles-ci impliquent :\n\ntenir des registres financiers et établir, tenir à jour et faire la balance de divers comptes en utilisant des systèmes de tenue de livres manuels ou informatisés;\nreporter des écritures au journal et faire concorder des comptes, préparer les balances de vérification des comptes, tenir des grands livres généraux et préparer des états financiers;\nfaire des calculs et préparer des chèques de paye, des factures de services d'utilité publique, de taxes et d'autres factures;\ncompléter et soumettre des formulaires de versement d'impôts, d'indemnisation des accidents du travail, de prestations de retraite et d'autres documents gouvernementaux;\npréparer des déclarations de revenus et effectuer d'autres services de tenue de livres pour des particuliers;\npréparer d'autres rapports statistiques, financiers et comptables.",
                "extraction_reussie": True,
                "notes": ""
            },
            "noc_oasis": {
                "url": "https://www23.statcan.gc.ca/imdb/p3VD_f.pl?Function=getVD&TVD=1322554&CVD=1322870&CPV=12200&CST=01052021&CLV=5&MLV=5",
                "texte_brut": "Fonctions principales\nCe groupe exerce une partie ou l'ensemble des fonctions suivantes :\n\ntenir des registres financiers et établir, tenir à jour et faire la balance de divers comptes en utilisant des systèmes de tenue de livres manuels ou informatisés;\nreporter des écritures au journal et faire concorder des comptes, préparer les balances de vérification des comptes, tenir des grands livres généraux et préparer des états financiers;\nfaire des calculs et préparer des chèques de paye, des factures de services d'utilité publique, de taxes et d'autres factures;\ncompléter et soumettre des formulaires de versement d'impôts, d'indemnisation des accidents du travail, de prestations de retraite et d'autres documents gouvernementaux;\npréparer des déclarations de revenus et effectuer d'autres services de tenue de livres pour des particuliers;\npréparer d'autres rapports statistiques, financiers et comptables.",
                "extraction_reussie": True,
                "notes": "Page StatCan NOC 2021 utilisée car noc.esdc.gc.ca bloquait les requêtes webfetch"
            }
        }
    }
]

for item in data:
    filepath = os.path.join(OUTPUT_DIR, f"{item['cnp']}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False, indent=2)
    print(f"Created: {filepath}")

print("Done.")
