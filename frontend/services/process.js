{
    display_name: "combinedCatalogName",
        pipeline: 1,
            used_config: {
        "param": {
            "crossmatch": {
                "n_neighbors": 1,
                    "radius_arcsec": 1.0,
                        "output_catalog_name": "tsm_cross_001"
            },
            "duplicate_criteria": "closest" // all // In case of multiple spec-z measurements for the same object:
        },
    }
    release: "1", // Select the LSST objects catalog
        inputs: [

        ]

}


// TSM só pode ter um input (criar uma regra para tratar)
// O campo release é obrigatório


// O Combine não tem release
// o numero de um input terá que ser > 1 (se for < ou = a 1, cancela o submit)