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
